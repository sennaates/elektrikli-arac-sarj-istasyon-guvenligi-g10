"""
ML Model Eğitim Scripti
Normal CAN-Bus trafiğinden Isolation Forest modelini eğitir.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
from loguru import logger
from utils.ml_ids import MLBasedIDS, SKLEARN_AVAILABLE


def generate_normal_traffic(count: int = 1000):
    """
    Normal CAN-Bus trafiği simüle et.
    Gerçek bir sistemde, bu veri gerçek trafikten toplanmalıdır.
    
    Args:
        count: Üretilecek örnek sayısı
    
    Returns:
        List of (can_id, data, timestamp) tuples
    """
    logger.info(f"Normal trafik üretiliyor ({count} örnek)...")
    
    samples = []
    start_time = time.time()
    
    # Normal CAN ID'ler ve paternleri
    normal_patterns = {
        0x200: lambda i: [0x01, i % 256, (i >> 8) % 256, 0x00, 0x00, 0x00, 0x00, 0x00],
        0x201: lambda i: [0x02, (i >> 16) % 256, (i >> 8) % 256, i % 256, 0x00, 0x00, 0x00, 0x00],
        0x210: lambda i: [0x03, i % 10, 32 + (i % 10), 0x00, 0x00, 0x00, 0x00, 0x00],
        0x300: lambda i: [0x10, (i * 10) % 256, (i * 5) % 256, 0x00, 0x00, 0x00, 0x00, 0x00],
    }
    
    for i in range(count):
        # Rastgele bir normal CAN ID seç
        can_id = random.choice(list(normal_patterns.keys()))
        
        # Patern fonksiyonunu çağır
        data = normal_patterns[can_id](i)
        
        # Timestamp (inter-arrival time ~10-100ms)
        timestamp = start_time + i * random.uniform(0.01, 0.1)
        
        samples.append((can_id, data, timestamp))
    
    logger.info(f"✓ {count} normal trafik örneği üretildi")
    return samples


def generate_anomaly_traffic(count: int = 100):
    """
    Anomali CAN-Bus trafiği simüle et.
    
    Args:
        count: Üretilecek anomali sayısı
    
    Returns:
        List of (can_id, data, timestamp) tuples
    """
    logger.info(f"Anomali trafik üretiliyor ({count} örnek)...")
    
    samples = []
    start_time = time.time()
    
    for i in range(count):
        # Anomali tipleri:
        anomaly_type = random.choice([
            "invalid_id",
            "high_entropy",
            "unusual_frequency"
        ])
        
        if anomaly_type == "invalid_id":
            # İzin listesinde olmayan ID
            can_id = random.choice([0x9FF, 0xABC, 0x7FF])
            data = [random.randint(0, 255) for _ in range(8)]
        
        elif anomaly_type == "high_entropy":
            # Normal ID ama tamamen rastgele payload
            can_id = random.choice([0x200, 0x201, 0x210])
            data = [random.randint(0, 255) for _ in range(8)]
        
        else:  # unusual_frequency
            # Normal ID ve pattern ama çok hızlı
            can_id = 0x200
            data = [0x01, i % 256, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        
        timestamp = start_time + i * random.uniform(0.001, 0.01)  # Daha hızlı
        samples.append((can_id, data, timestamp))
    
    logger.info(f"✓ {count} anomali örneği üretildi")
    return samples


def train_model(
    normal_count: int = 1000,
    save_path: str = "./models/isolation_forest.pkl"
):
    """
    Isolation Forest modelini eğit ve kaydet.
    
    Args:
        normal_count: Normal trafik örnek sayısı
        save_path: Model kayıt yolu
    """
    if not SKLEARN_AVAILABLE:
        logger.error("scikit-learn kurulu değil!")
        logger.info("Kurmak için: pip install scikit-learn")
        return False
    
    logger.info("="*60)
    logger.info("ML MODEL EĞİTİMİ BAŞLIYOR")
    logger.info("="*60)
    
    # ML-IDS oluştur
    ml_ids = MLBasedIDS(contamination=0.1)
    
    # Normal trafik üret ve ekle
    normal_samples = generate_normal_traffic(normal_count)
    
    logger.info("Normal örnekler ML-IDS'e ekleniyor...")
    for can_id, data, timestamp in normal_samples:
        ml_ids.add_training_sample(can_id, data, timestamp)
    
    # Modeli eğit
    logger.info(f"Model eğitiliyor ({len(ml_ids.training_buffer)} örnek)...")
    success = ml_ids.train(min_samples=100)
    
    if not success:
        logger.error("❌ Model eğitimi başarısız!")
        return False
    
    logger.info("✓ Model başarıyla eğitildi")
    
    # Test et
    logger.info("\n" + "="*60)
    logger.info("MODEL TESTİ")
    logger.info("="*60)
    
    # Normal örneklerle test
    test_normal = generate_normal_traffic(50)
    normal_predictions = []
    
    for can_id, data, timestamp in test_normal:
        is_anomaly, score = ml_ids.predict(can_id, data, timestamp)
        normal_predictions.append(is_anomaly)
    
    normal_accuracy = (len([x for x in normal_predictions if not x]) / len(normal_predictions)) * 100
    logger.info(f"Normal trafik: {normal_accuracy:.1f}% doğru sınıflandırıldı (normal olarak)")
    
    # Anomali örneklerle test
    test_anomaly = generate_anomaly_traffic(50)
    anomaly_predictions = []
    
    for can_id, data, timestamp in test_anomaly:
        is_anomaly, score = ml_ids.predict(can_id, data, timestamp)
        anomaly_predictions.append(is_anomaly)
    
    anomaly_accuracy = (len([x for x in anomaly_predictions if x]) / len(anomaly_predictions)) * 100
    logger.info(f"Anomali trafik: {anomaly_accuracy:.1f}% doğru sınıflandırıldı (anomali olarak)")
    
    # Modeli kaydet
    logger.info(f"\nModel kaydediliyor: {save_path}")
    
    # Dizin yoksa oluştur
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    if ml_ids.save_model(save_path):
        logger.info(f"✓ Model kaydedildi: {save_path}")
        logger.info("\n" + "="*60)
        logger.info("EĞİTİM TAMAMLANDI!")
        logger.info("="*60)
        return True
    else:
        logger.error("❌ Model kaydetme başarısız!")
        return False


def main():
    """Ana entry point"""
    # Logger config
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>"
    )
    
    # Model eğit
    success = train_model(
        normal_count=1000,
        save_path="./models/isolation_forest.pkl"
    )
    
    if success:
        logger.info("\n✓ secure_bridge.py başlatıldığında bu model otomatik yüklenecek.")
    else:
        logger.error("\n❌ Eğitim başarısız!")
        sys.exit(1)


if __name__ == "__main__":
    main()

