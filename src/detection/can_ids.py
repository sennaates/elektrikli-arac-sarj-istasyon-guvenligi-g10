"""
CAN Intrusion Detection System (IDS)

CAN trafiğindeki anomali ve saldırıları tespit eder
"""

import logging
from typing import Dict, List, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics
import hashlib

from src.can_bus.can_simulator import CANMessage

logger = logging.getLogger(__name__)


class CANIntrusionDetector:
    """
    CAN saldırı tespit sistemi
    
    Özellikler:
    - FREkans analizi
    - Beklenmeyen CAN ID tespiti
    - Temporal pattern analizi
    - Entropy analizi
    """
    
    def __init__(self, window_size: int = 100):
        """
        Args:
            window_size: Analiz penceresi boyutu
        """
        self.window_size = window_size
        
        # İstatistikler
        self.message_history: deque = deque(maxlen=window_size)
        self.id_frequency: Dict[int, int] = defaultdict(int)
        self.id_timestamps: Dict[int, List[datetime]] = defaultdict(list)
        
        # Tespit edilen anomali
        self.anomalies: List[Dict] = []
        
        # Baseline (normal davranış)
        self.baseline: Optional[Dict] = None
        self.baseline_mode = 'learning'  # 'learning' veya 'detection'
        
        # Eşikler
        self.thresholds = {
            'min_frequency': 0.01,  # En az frekans
            'max_frequency': 0.5,    # Maksimum frekans
            'new_id_threshold': 3    # Yeni ID için mesaj sayısı
        }
    
    def analyze_message(self, can_msg: CANMessage) -> Optional[Dict]:
        """
        CAN mesajını analiz et
        
        Args:
            can_msg: CAN mesajı
            
        Returns:
            Optional[Dict]: Anomali tespit edilirse detaylar, yoksa None
        """
        self.message_history.append(can_msg)
        self.id_frequency[can_msg.can_id] += 1
        self.id_timestamps[can_msg.can_id].append(can_msg.timestamp)
        
        # Baseline öğrenme modu
        if self.baseline_mode == 'learning':
            return None  # Anomali gösterme, öğren
        
        # Anomali tespiti
        anomaly = None
        
        # 1. Beklenmeyen CAN ID tespiti
        if self._is_unexpected_id(can_msg.can_id):
            anomaly = {
                'type': 'unexpected_id',
                'can_id': hex(can_msg.can_id),
                'message': f"Beklenmeyen CAN ID: {hex(can_msg.can_id)}",
                'severity': 'high'
            }
        
        # 2. Frekans anomali tespiti
        elif self._is_frequency_anomaly(can_msg.can_id):
            anomaly = {
                'type': 'frequency_anomaly',
                'can_id': hex(can_msg.can_id),
                'message': f"Anormal frekans: {hex(can_msg.can_id)}",
                'severity': 'medium'
            }
        
        # 3. Burst attack tespiti
        elif self._is_burst_attack(can_msg.can_id):
            anomaly = {
                'type': 'burst_attack',
                'can_id': hex(can_msg.can_id),
                'message': f"Burst saldırısı: {hex(can_msg.can_id)}",
                'severity': 'high'
            }
        
        if anomaly:
            anomaly['timestamp'] = can_msg.timestamp
            self.anomalies.append(anomaly)
            logger.warning(f"🚨 ANOMALI TESPİT EDİLDİ: {anomaly['message']}")
        
        return anomaly
    
    def _is_unexpected_id(self, can_id: int) -> bool:
        """Beklenmeyen CAN ID mi?"""
        if self.baseline:
            # Baseline'da bu ID var mı?
            if can_id not in self.baseline.get('known_ids', set()):
                return True
        return False
    
    def _is_frequency_anomaly(self, can_id: int) -> bool:
        """Frekans anomali var mı?"""
        if not self.baseline:
            return False
        
        baseline = self.baseline
        current_freq = self.id_frequency[can_id] / len(self.message_history)
        
        if can_id in baseline.get('id_frequency', {}):
            expected_freq = baseline['id_frequency'][can_id]
            
            # %50'den fazla sapma
            if abs(current_freq - expected_freq) > (expected_freq * 0.5):
                return True
        
        return False
    
    def _is_burst_attack(self, can_id: int) -> bool:
        """Burst saldırısı mı? (saniyede çok fazla mesaj)"""
        if can_id not in self.id_timestamps:
            return False
        
        timestamps = self.id_timestamps[can_id]
        
        # Son 1 saniyede 10'dan fazla mesaj mı?
        now = datetime.now()
        recent_messages = [ts for ts in timestamps if (now - ts).total_seconds() < 1.0]
        
        if len(recent_messages) > 10:
            return True
        
        return False
    
    def learn_baseline(self, duration_seconds: int = 30):
        """
        Normal davranışı öğren (baseline oluştur)
        
        Args:
            duration_seconds: Öğrenme süresi (saniye)
        """
        logger.info(f"📚 Baseline öğreniliyor: {duration_seconds} saniye...")
        self.baseline_mode = 'learning'
        
        # Duration'dan sonra otomatik geçiş
        # (gerçek uygulamada timer kullanılabilir)
    
    def finalize_baseline(self):
        """Baseline'ı finalize et"""
        logger.info("✅ Baseline finalize ediliyor...")
        
        if len(self.message_history) == 0:
            logger.error("❌ Mesaj geçmişi yok")
            return
        
        total_messages = len(self.message_history)
        
        # Frekans hesapla
        id_frequency = {}
        for can_id, count in self.id_frequency.items():
            id_frequency[can_id] = count / total_messages
        
        self.baseline = {
            'known_ids': set(self.id_frequency.keys()),
            'id_frequency': id_frequency,
            'total_messages': total_messages,
            'created_at': datetime.now()
        }
        
        self.baseline_mode = 'detection'
        
        logger.info(f"✅ Baseline oluşturuldu: {len(self.baseline['known_ids'])} CAN ID")
    
    def get_detection_stats(self) -> Dict:
        """Tespit istatistiklerini döndür"""
        return {
            'total_messages': len(self.message_history),
            'unique_ids': len(self.id_frequency),
            'anomalies_detected': len(self.anomalies),
            'baseline_mode': self.baseline_mode,
            'has_baseline': self.baseline is not None,
            'recent_anomalies': self.anomalies[-10:] if self.anomalies else []
        }
    
    def reset(self):
        """IDS'yi sıfırla"""
        self.message_history.clear()
        self.id_frequency.clear()
        self.id_timestamps.clear()
        self.anomalies.clear()
        self.baseline = None
        self.baseline_mode = 'learning'
        logger.info("🧹 IDS sıfırlandı")


def demo():
    """Demo"""
    import time
    
    detector = CANIntrusionDetector(window_size=100)
    
    print("CAN Intrusion Detection System Demo")
    print("=" * 50)
    
    # Baseline öğren
    detector.learn_baseline(duration_seconds=10)
    
    # Normal mesajlar (simülasyon)
    from src.can_bus.can_simulator import CANMessage
    import random
    
    print("\n1. Normal mesajlar gönderiliyor...")
    for i in range(20):
        can_id = random.choice([0x200, 0x201, 0x300])
        msg = CANMessage(can_id=can_id, data=bytes([i % 256]), timestamp=datetime.now())
        detector.analyze_message(msg)
        time.sleep(0.1)
    
    # Baseline finalize
    detector.finalize_baseline()
    
    # Anomali test
    print("\n2. Anomali tespiti test ediliyor...")
    
    # Beklenmeyen CAN ID
    anomaly_msg = CANMessage(can_id=0x9FF, data=b"ATTACK", timestamp=datetime.now())
    result = detector.analyze_message(anomaly_msg)
    
    if result:
        print(f"   ✅ Anomali tespit edildi: {result['message']}")
    
    # İstatistikler
    stats = detector.get_detection_stats()
    print(f"\n📊 İstatistikler:")
    print(f"   Toplam mesaj: {stats['total_messages']}")
    print(f"   Benzersiz ID: {stats['unique_ids']}")
    print(f"   Anomali sayısı: {stats['anomalies_detected']}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    demo()

