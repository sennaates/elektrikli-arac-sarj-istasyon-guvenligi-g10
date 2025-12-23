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
    
    Features:
    1. CAN ID
    2. Payload length
    3. Payload entropy
    4. Inter-arrival time (son mesajdan bu yana geçen süre)
    5. CAN ID frequency (son 10 saniyede kaç kez görüldü)
    6. Payload byte ortalaması
    7. Payload byte std deviation
    8. Time of day (0-86400 saniye)
    9. OCPP message rate (Senaryo #2)
    10. Burst detection (ani artış tespiti - Senaryo #2)
    """
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        
        # Son mesajların timestamp'leri (CAN ID bazında)
        self.last_timestamps: Dict[int, float] = {}
        
        # CAN ID frekans kuyruğu (timestamp, can_id)
        self.frequency_window: deque = deque(maxlen=1000)
        
        # Senaryo #2: OCPP mesaj rate tracking
        self.ocpp_timestamps: deque = deque(maxlen=1000)
        self.ocpp_action_counts: Dict[str, int] = {}
        
        # Senaryo #3: Sampling & energy tracking
        self.meter_values: deque = deque(maxlen=1000)  # (timestamp, value)
        self.meter_timestamps: deque = deque(maxlen=1000)
    
    def extract_can_features(
        self,
        can_id: int,
        data: List[int],
        timestamp: float
    ) -> np.ndarray:
        """CAN frame'den feature vector çıkar"""
        
        # Feature 1: CAN ID (normalized)
        feature_can_id = can_id / 2048.0  # Max CAN ID: 0x7FF (2048)
        
        # Feature 2: Payload length
        feature_payload_len = len(data) / 8.0  # Max: 8 byte
        
        # Feature 3: Payload entropy
        feature_entropy = self._calculate_entropy(data)
        
        # Feature 4: Inter-arrival time
        last_time = self.last_timestamps.get(can_id, timestamp - 0.1)
        feature_inter_arrival = min(timestamp - last_time, 10.0) / 10.0  # Cap at 10s
        self.last_timestamps[can_id] = timestamp
        
        # Feature 5: CAN ID frequency (son 10 saniyede)
        self.frequency_window.append((timestamp, can_id))
        recent_count = sum(1 for t, cid in self.frequency_window 
                          if cid == can_id and timestamp - t <= 10.0)
        feature_frequency = min(recent_count / 100.0, 1.0)  # Normalize
        
        # Feature 6: Payload byte ortalaması
        feature_mean = np.mean(data) / 255.0 if data else 0.0
        
        # Feature 7: Payload byte std deviation
        feature_std = (np.std(data) / 255.0) if len(data) > 1 else 0.0
        
        # Feature 8: Time of day (cyclical encoding)
        time_of_day = timestamp % 86400  # Saniye cinsinden
        feature_time_sin = np.sin(2 * np.pi * time_of_day / 86400)
        feature_time_cos = np.cos(2 * np.pi * time_of_day / 86400)
        
        # Feature vector oluştur
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
    
    def extract_ocpp_rate_features(
        self,
        action: str,
        timestamp: float,
        window: float = 1.0
    ) -> Tuple[float, float]:
        """
        OCPP mesaj rate'i için feature çıkar (Senaryo #2).
        
        Returns:
            (message_rate, burst_score)
            - message_rate: Son window içinde mesaj/saniye
            - burst_score: Ani artış skoru (0-1)
        """
        # Timestamp'i kaydet
        self.ocpp_timestamps.append(timestamp)
        
        # Action count'u güncelle
        self.ocpp_action_counts[action] = self.ocpp_action_counts.get(action, 0) + 1
        
        # Son window içindeki mesajları say
        recent_messages = [t for t in self.ocpp_timestamps if timestamp - t <= window]
        message_rate = len(recent_messages) / window if window > 0 else 0
        
        # Burst detection: Son 1 saniye vs önceki 10 saniye karşılaştırması
        recent_1s = sum(1 for t in self.ocpp_timestamps if timestamp - t <= 1.0)
        recent_10s = sum(1 for t in self.ocpp_timestamps if timestamp - t <= 10.0)
        
        avg_rate_10s = recent_10s / 10.0 if recent_10s > 0 else 0.1
        burst_score = min(recent_1s / (avg_rate_10s + 0.1), 10.0) / 10.0  # Normalize to [0, 1]
        
        return message_rate, burst_score
    
    def extract_sampling_features(
        self,
        meter_value: float,
        timestamp: float,
        window: float = 60.0
    ) -> Tuple[float, float, float]:
        """
        Enerji ölçüm sampling için feature çıkar (Senaryo #3).
        
        Returns:
            (sampling_rate, variance_score, inter_sample_time)
            - sampling_rate: sample/minute
            - variance_score: Rolling variance (normalized)
            - inter_sample_time: Son sample'dan beri geçen süre
        """
        # Timestamp ve değeri kaydet
        self.meter_values.append((timestamp, meter_value))
        self.meter_timestamps.append(timestamp)
        
        # Sampling rate: Son window içinde sample/minute
        recent_timestamps = [t for t in self.meter_timestamps if timestamp - t <= window]
        sampling_rate = len(recent_timestamps) / (window / 60.0) if window > 0 else 0
        
        # Variance score: Son N değerin varyansı
        recent_values = [v for t, v in self.meter_values if timestamp - t <= window]
        variance_score = 0.0
        if len(recent_values) >= 3:
            variance = np.var(recent_values)
            # Normalize (tipik varyans: 0.1-1.0 kWh^2)
            variance_score = min(variance / 1.0, 1.0)
        
        # Inter-sample time: Son sample'dan beri geçen süre
        if len(self.meter_timestamps) >= 2:
            inter_sample_time = self.meter_timestamps[-1] - self.meter_timestamps[-2]
        else:
            inter_sample_time = 0.0
        
        # Normalize (tipik: 1-5 saniye)
        inter_sample_normalized = min(inter_sample_time / 60.0, 1.0)
        
        return sampling_rate, variance_score, inter_sample_normalized
    
    def _calculate_entropy(self, data: List[int]) -> float:
        """Shannon entropy hesapla"""
        if not data:
            return 0.0
        
        # Byte frekansları
        counts = np.bincount(data, minlength=256)
        probabilities = counts / len(data)
        
        # Entropy
        entropy = -np.sum([p * np.log2(p) for p in probabilities if p > 0])
        
        # Normalize (max entropy = 8 bits)
        return entropy / 8.0


class MLBasedIDS:
    """
    Makine öğrenmesi tabanlı saldırı tespit sistemi.
    Isolation Forest algoritması kullanır.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        contamination: float = 0.1,  # Anomali oranı tahmini
        threshold: float = 0.7
    ):
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
        
        # Feature extraction
        features = self.feature_extractor.extract_can_features(can_id, data, timestamp)
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Prediction
        # Isolation Forest: -1 = anomaly, 1 = normal
        prediction = self.model.predict(features_scaled)[0]
        
        # Anomaly score (decision function)
        # Negatif değer = anomali, pozitif = normal
        score_raw = self.model.decision_function(features_scaled)[0]
        
        # Score'u 0-1 aralığına normalize et
        # score_raw genelde [-0.5, 0.5] arasında
        anomaly_score = max(0.0, min(1.0, 0.5 - score_raw))
        
        is_anomaly = prediction == -1 or anomaly_score >= self.threshold
        
        if is_anomaly:
            logger.debug(f"ML-IDS: Anomali tespit edildi (score={anomaly_score:.3f})")
        
        return is_anomaly, anomaly_score
    
    def add_training_sample(
        self,
        can_id: int,
        data: List[int],
        timestamp: float
    ) -> None:
        """Eğitim için örnek ekle"""
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
            
            # Scaler'ı fit et
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
        """Modeli ve scaler'ı yükle"""
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
    
    Karar mantığı:
    - Rule-based IDS HIGH/CRITICAL alert verirse → direkt alarm
    - ML-IDS anomali skoruif >= threshold → alarm
    - Her ikisi de normal derse → normal
    """
    
    def __init__(
        self,
        rule_based_ids,  # RuleBasedIDS instance
        ml_based_ids: Optional[MLBasedIDS] = None,
        ml_weight: float = 0.3  # ML skorunun ağırlığı (0-1)
    ):
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
        
        # 2. ML-based check (eğer model varsa ve eğitilmişse)
        ml_score = None
        if self.ml_based_ids and self.ml_based_ids.is_trained:
            self.total_ml_checks += 1
            is_ml_anomaly, ml_score = self.ml_based_ids.predict(can_id, data, timestamp)
            
            # ML anomali tespit ettiyse ve rule-based tespit etmediyse
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


if __name__ == "__main__":
    # Test
    logger.info("ML-Based IDS test ediliyor...")
    
    if not SKLEARN_AVAILABLE:
        print("❌ sklearn kurulu değil. Test yapılamıyor.")
        print("Kurmak için: pip install scikit-learn")
        exit(1)
    
    print("\n" + "="*50)
    print("FEATURE EXTRACTION TEST")
    print("="*50)
    
    extractor = FeatureExtractor()
    features = extractor.extract_can_features(
        can_id=0x200,
        data=[0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08],
        timestamp=time.time()
    )
    print(f"Feature vector boyutu: {len(features)}")
    print(f"Features: {features}")
    
    print("\n" + "="*50)
    print("ML MODEL TRAINING TEST")
    print("="*50)
    
    ml_ids = MLBasedIDS()
    
    # Normal trafik örnekleri ekle
    print("Normal trafik örnekleri ekleniyor...")
    for i in range(200):
        ml_ids.add_training_sample(
            can_id=0x200 + (i % 3),
            data=[i % 256, (i+1) % 256, (i+2) % 256, 0x00, 0x00, 0x00, 0x00, 0x00],
            timestamp=time.time() + i * 0.01
        )
    
    # Model eğit
    success = ml_ids.train(min_samples=100)
    if success:
        print("✓ Model başarıyla eğitildi")
        
        # Test
        print("\n" + "="*50)
        print("ANOMALY PREDICTION TEST")
        print("="*50)
        
        # Normal frame
        is_anom, score = ml_ids.predict(0x200, [0x01, 0x02, 0x03, 0x00], time.time())
        print(f"\nNormal frame: anomaly={is_anom}, score={score:.3f}")
        
        # Anormal frame (tamamen farklı)
        is_anom, score = ml_ids.predict(0x9FF, [0xFF] * 8, time.time())
        print(f"Anormal frame: anomaly={is_anom}, score={score:.3f}")
    else:
        print("❌ Model eğitimi başarısız")

