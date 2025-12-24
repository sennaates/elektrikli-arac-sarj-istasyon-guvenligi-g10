"""
Machine Learning-Based Intrusion Detection System
Isolation Forest kullanarak anomali tespiti yapar.
"""
import numpy as np
import time
from typing import Dict, List, Optional, Tuple
from collections import deque
from loguru import logger

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn bulunamadı. ML-IDS devre dışı.")


class FeatureExtractor:
    """
    OCPP ve CAN trafiğinden feature'lar çıkarır.
    """
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.last_timestamps: Dict[int, float] = {}
        self.frequency_window: deque = deque(maxlen=1000)
        
        # Diğer özellikler için bufferlar
        self.ocpp_timestamps: deque = deque(maxlen=1000)
        self.ocpp_action_counts: Dict[str, int] = {}
        self.meter_values: deque = deque(maxlen=1000)
        self.meter_timestamps: deque = deque(maxlen=1000)
    
    def extract_can_features(self, can_id: int, data: List[int], timestamp: float) -> np.ndarray:
        # 1. Feature: CAN ID (Normalize)
        feature_can_id = can_id / 2048.0
        
        # 2. Feature: Payload Length
        feature_payload_len = len(data) / 8.0
        
        # 3. Feature: Entropy
        feature_entropy = self._calculate_entropy(data)
        
        # 4. Feature: Inter-arrival time
        last_time = self.last_timestamps.get(can_id, timestamp - 0.1)
        feature_inter_arrival = min(timestamp - last_time, 10.0) / 10.0
        self.last_timestamps[can_id] = timestamp
        
        # 5. Feature: Frequency
        self.frequency_window.append((timestamp, can_id))
        recent_count = sum(1 for t, cid in self.frequency_window 
                          if cid == can_id and timestamp - t <= 10.0)
        feature_frequency = min(recent_count / 100.0, 1.0)
        
        # 6. Feature: Mean Value
        feature_mean = np.mean(data) / 255.0 if data else 0.0
        
        # 7. Feature: Std Dev
        feature_std = (np.std(data) / 255.0) if len(data) > 1 else 0.0
        
        # 8 & 9. Feature: Time cyclical
        time_of_day = timestamp % 86400
        feature_time_sin = np.sin(2 * np.pi * time_of_day / 86400)
        feature_time_cos = np.cos(2 * np.pi * time_of_day / 86400)
        
        features = np.array([
            feature_can_id,
            feature_payload_len,
            feature_entropy,
            feature_inter_arrival,
            feature_frequency,
            feature_mean,
            feature_std,
            feature_time_sin,
            feature_time_cos
        ])
        
        return features
    
    def _calculate_entropy(self, data: List[int]) -> float:
        if not data: return 0.0
        counts = np.bincount(data, minlength=256)
        probabilities = counts / len(data)
        entropy = -np.sum([p * np.log2(p) for p in probabilities if p > 0])
        return entropy / 8.0


class MLBasedIDS:
    """
    Makine öğrenmesi tabanlı saldırı tespit sistemi.
    """
    
    def __init__(self, model_path: Optional[str] = None, contamination: float = 0.1, threshold: float = 0.7):
        if not SKLEARN_AVAILABLE:
            logger.error("sklearn kurulu değil! ML-IDS kullanılamaz.")
            self.model = None
            self.scaler = None
            return
        
        self.model_path = model_path
        self.contamination = contamination
        self.threshold = threshold
        self.feature_extractor = FeatureExtractor()
        self.scaler = StandardScaler()
        
        # Training buffer
        self.training_buffer: List[np.ndarray] = []
        self.is_trained = False  # Varsayılan olarak eğitilmemiş
        
        # Model yükle veya yeni oluştur
        if model_path:
            self.load_model(model_path)  # Bu is_trained = True yapacak
        else:
            self.model = IsolationForest(
                contamination=contamination,
                random_state=42,
                n_estimators=100
            )
            logger.info("Yeni Isolation Forest modeli oluşturuldu (eğitilmemiş)")
    
    def predict(
        self,
        can_id: int,
        data: List[int],
        timestamp: float
    ) -> Tuple[bool, float]:
        """
        CAN frame'in anomali olup olmadığını tahmin et.
        
        Returns:
            (is_anomaly, anomaly_score) tuple
            - is_anomaly: True ise anomali
            - anomaly_score: 0-1 arası, 1'e yakın = daha anormal
        """
        if self.model is None or not self.is_trained:
            return False, 0.0
        
        features = self.feature_extractor.extract_can_features(can_id, data, timestamp)
        
        try:
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            prediction = self.model.predict(features_scaled)[0]
            score_raw = self.model.decision_function(features_scaled)[0]
            
            # Score normalizasyonu (0-1 arası)
            anomaly_score = max(0.0, min(1.0, 0.5 - score_raw))
            
            is_anomaly = prediction == -1 or anomaly_score >= self.threshold
            
            if is_anomaly:
                logger.debug(f"ML-IDS: Anomali tespit edildi (score={anomaly_score:.3f})")
            
            return is_anomaly, anomaly_score
            
        except Exception as e:
            # logger.error(f"Predict hatası: {e}")
            return False, 0.0
    
    def add_training_sample(self, can_id: int, data: List[int], timestamp: float) -> None:
        features = self.feature_extractor.extract_can_features(can_id, data, timestamp)
        self.training_buffer.append(features)
    
    def train(self, min_samples: int = 100) -> bool:
        """
        Modeli eğit.
        
        Args:
            min_samples: Minimum eğitim örneği sayısı
        
        Returns:
            Başarılı mı?
        """
        if self.model is None or not SKLEARN_AVAILABLE:
            logger.error("Model veya sklearn mevcut değil!")
            return False
        
        if len(self.training_buffer) < min_samples:
            logger.warning(f"Yetersiz eğitim verisi: {len(self.training_buffer)}/{min_samples}")
            return False
        
        try:
            X = np.array(self.training_buffer)
            
            # Scaler fit
            self.scaler.fit(X)
            X_scaled = self.scaler.transform(X)
            
            # Model eğit
            logger.info(f"Model eğitiliyor... ({len(X)} örnek)")
            self.model.fit(X_scaled)
            
            self.is_trained = True
            logger.info("✓ Model başarıyla eğitildi")
            
            return True
        except Exception as e:
            logger.error(f"Model eğitim hatası: {e}")
            return False
    
    def save_model(self, path: str) -> bool:
        """Modeli ve scaler'ı kaydet"""
        if self.model is None or not self.is_trained:
            logger.error("Eğitilmiş model yok!")
            return False
        
        try:
            joblib.dump({
                "model": self.model,
                "scaler": self.scaler,
                "contamination": self.contamination
            }, path)
            logger.info(f"Model kaydedildi: {path}")
            return True
        except Exception as e:
            logger.error(f"Model kaydetme hatası: {e}")
            return False
    
    def load_model(self, path: str) -> bool:
        try:
            data = joblib.load(path)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.contamination = data.get("contamination", 0.1)
            self.is_trained = True
            logger.info(f"Model yüklendi: {path}")
            return True
        except FileNotFoundError:
            logger.warning(f"Model dosyası bulunamadı: {path}")
            return False
        except Exception as e:
            logger.error(f"Model yükleme hatası: {e}")
            return False


class HybridIDS:
    """
    Rule-based ve ML-based IDS'i birleştirir.
    """
    
    def __init__(self, rule_based_ids, ml_based_ids: Optional[MLBasedIDS] = None, ml_weight: float = 0.3):
        self.rule_based_ids = rule_based_ids
        self.ml_based_ids = ml_based_ids
        self.ml_weight = ml_weight
        
        # ML tespit sayacı
        self.ml_detection_count = 0
        self.total_ml_checks = 0
        
        logger.info(f"Hybrid IDS başlatıldı (ML weight={ml_weight})")
    
    def check_can_frame(
        self,
        can_id: int,
        data: List[int],
        timestamp: float
    ) -> Tuple[Optional[object], Optional[float]]:
        """
        CAN frame'i hem rule-based hem ML-based kontrol et.
        
        Returns:
            (Alert object or None, ML anomaly score or None)
        """
        # 1. Rule-based check
        alert = self.rule_based_ids.check_can_frame(can_id, data, timestamp)
        
        # 2. ML-based check
        ml_score = None
        if self.ml_based_ids and self.ml_based_ids.is_trained:
            self.total_ml_checks += 1
            is_ml_anomaly, ml_score = self.ml_based_ids.predict(can_id, data, timestamp)
            
            # ML anomali bulduysa ve Rule-Based bulmadıysa alert üret
            if is_ml_anomaly and not alert:
                self.ml_detection_count += 1
                # ML-based alert oluştur
                alert = self.rule_based_ids._create_alert(
                    alert_type="ML_ANOMALY_DETECTED",
                    severity="MEDIUM",
                    description=f"ML modeli anomali tespit etti (score={ml_score:.3f})",
                    source="ML",
                    data={
                        "can_id": hex(can_id),
                        "data": [hex(b) for b in data],
                        "ml_score": ml_score
                    }
                )
                logger.info(f"🤖 ML-IDS Alert: {alert.description}")
        
        return alert, ml_score
