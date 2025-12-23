"""
ML Model Eğitim Scripti - Gelişmiş Versiyon
9 Farklı Saldırı Senaryosu için Hibrit Model Eğitimi

Senaryolar:
1. MitM OCPP Manipulation
2. OCPP DoS Flooding
3. Sampling Manipulation
4. Fail-Open Attack
5. Ransomware/Firmware Attack
6. Latency Exploit
7. OCPP Advanced Flooding
8. OCPP Protocol Fuzzing
9. Sensor Data Poisoning
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
import numpy as np
from loguru import logger
from utils.ml_ids import MLBasedIDS, SKLEARN_AVAILABLE


# ============================================================================
# NORMAL TRAFİK ÜRETİMİ
# ============================================================================

def generate_normal_traffic(count: int = 2000):
    """
    Normal CAN-Bus trafiği simüle et.
    Gerçek şarj istasyonu trafiğine benzer paternler üretir.
    """
    logger.info(f"Normal trafik üretiliyor ({count} örnek)...")
    
    samples = []
    start_time = time.time()
    
    # Normal CAN ID'ler ve paternleri (Şarj istasyonu protokolü)
    normal_patterns = {
        # Şarj kontrolü
        0x200: lambda i: [0x01, i % 256, (i >> 8) % 256, 0x00, 0x00, 0x00, 0x00, 0x00],  # Start
        0x201: lambda i: [0x02, (i >> 16) % 256, (i >> 8) % 256, i % 256, 0x00, 0x00, 0x00, 0x00],  # Stop
        
        # Durum bilgisi
        0x210: lambda i: [0x03, i % 10, 32 + (i % 10), 0x00, 0x00, 0x00, 0x00, 0x00],  # Status
        0x220: lambda i: [0x04, min(100, i % 101), 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # Battery %
        
        # Enerji ölçümü
        0x230: lambda i: [0x05, (i * 10) % 256, (i * 10 >> 8) % 256, 0x00, 0x00, 0x00, 0x00, 0x00],  # Voltage
        0x231: lambda i: [0x06, (i * 5) % 256, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],  # Current
        
        # Heartbeat
        0x300: lambda i: [0x10, (i * 10) % 256, (i * 5) % 256, 0x00, 0x00, 0x00, 0x00, 0x00],
    }
    
    for i in range(count):
        # Ağırlıklı seçim (bazı mesajlar daha sık)
        weights = [0.15, 0.15, 0.2, 0.1, 0.15, 0.1, 0.15]
        can_id = random.choices(list(normal_patterns.keys()), weights=weights)[0]
        
        # Patern fonksiyonunu çağır
        data = normal_patterns[can_id](i)
        
        # Normal timestamp (inter-arrival time ~10-100ms, düzgün dağılım)
        timestamp = start_time + i * random.uniform(0.01, 0.1)
        
        samples.append((can_id, data, timestamp, "normal"))
    
    logger.info(f"✓ {count} normal trafik örneği üretildi")
    return samples


# ============================================================================
# SENARYO BAZLI ANOMALİ ÜRETİMİ
# ============================================================================

def generate_scenario_1_mitm(count: int = 50):
    """Senaryo #1: MitM OCPP Manipulation"""
    logger.info(f"  Senaryo #1 (MitM): {count} örnek üretiliyor...")
    samples = []
    start_time = time.time()
    
    for i in range(count):
        # Timing anomaly: Start sonrası çok hızlı Stop
        if i % 2 == 0:
            can_id = 0x200  # Start
            data = [0x01, 0x01, 0xAB, 0xCD, 0x00, 0x00, 0x00, 0x00]
        else:
            can_id = 0x201  # Stop (hemen ardından)
            data = [0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        
        # Çok kısa inter-arrival time (500ms - 1s arası, normal 60s+ olmalı)
        timestamp = start_time + i * random.uniform(0.5, 1.0)
        samples.append((can_id, data, timestamp, "mitm"))
    
    return samples


def generate_scenario_2_dos_flood(count: int = 100):
    """Senaryo #2: OCPP DoS Flooding - CAN Bus flood"""
    logger.info(f"  Senaryo #2 (DoS Flood): {count} örnek üretiliyor...")
    samples = []
    start_time = time.time()
    
    for i in range(count):
        can_id = random.choice([0x200, 0x201, 0x210])
        data = [random.randint(0, 255) for _ in range(8)]
        
        # Çok yüksek frekans (1-5ms arası, normal 10-100ms)
        timestamp = start_time + i * random.uniform(0.001, 0.005)
        samples.append((can_id, data, timestamp, "flood"))
    
    return samples


def generate_scenario_3_sampling(count: int = 50):
    """Senaryo #3: Sampling Manipulation"""
    logger.info(f"  Senaryo #3 (Sampling): {count} örnek üretiliyor...")
    samples = []
    start_time = time.time()
    
    for i in range(count):
        can_id = 0x230  # Energy meter
        
        # Peak smoothing: Değerleri ortalamaya çek (düşük varyans)
        smoothed_value = 128 + random.randint(-5, 5)  # Çok dar aralık
        data = [0x05, smoothed_value, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        
        # Düşük sampling rate (60s arası, normal 1-5s)
        timestamp = start_time + i * random.uniform(30.0, 60.0)
        samples.append((can_id, data, timestamp, "sampling"))
    
    return samples


def generate_scenario_4_fail_open(count: int = 50):
    """Senaryo #4: Fail-Open Attack"""
    logger.info(f"  Senaryo #4 (Fail-Open): {count} örnek üretiliyor...")
    samples = []
    start_time = time.time()
    
    for i in range(count):
        # Auth olmadan şarj başlatma simülasyonu
        can_id = 0x200  # Start command
        
        # Auth flag'i 0 (unauthorized)
        data = [0x01, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF]  # FF = error marker
        
        # Timeout sonrası hızlı retry
        timestamp = start_time + i * random.uniform(0.1, 0.5)
        samples.append((can_id, data, timestamp, "fail_open"))
    
    return samples


def generate_scenario_5_ransomware(count: int = 50):
    """Senaryo #5: Ransomware/Firmware Attack"""
    logger.info(f"  Senaryo #5 (Ransomware): {count} örnek üretiliyor...")
    samples = []
    start_time = time.time()
    
    # Anormal CAN ID'ler (firmware update ID'leri)
    firmware_ids = [0x7FF, 0x7FE, 0x777, 0x666]
    
    for i in range(count):
        can_id = random.choice(firmware_ids)
        
        # Yüksek entropi payload (şifreli/rastgele veri)
        data = [random.randint(0, 255) for _ in range(8)]
        
        timestamp = start_time + i * random.uniform(0.01, 0.05)
        samples.append((can_id, data, timestamp, "ransomware"))
    
    return samples


def generate_scenario_6_latency(count: int = 50):
    """Senaryo #6: Latency Exploit"""
    logger.info(f"  Senaryo #6 (Latency): {count} örnek üretiliyor...")
    samples = []
    start_time = time.time()
    
    for i in range(count):
        can_id = random.choice([0x200, 0x201])
        data = [0x01, i % 256, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        
        # Çok düzensiz timing (0.1ms - 10s arası)
        if i % 3 == 0:
            timestamp = start_time + i * random.uniform(5.0, 10.0)  # Çok yavaş
        else:
            timestamp = start_time + i * random.uniform(0.0001, 0.001)  # Çok hızlı
        
        samples.append((can_id, data, timestamp, "latency"))
    
    return samples


def generate_scenario_7_advanced_flood(count: int = 100):
    """Senaryo #7: OCPP Advanced Flooding (Burst pattern)"""
    logger.info(f"  Senaryo #7 (Advanced Flood): {count} örnek üretiliyor...")
    samples = []
    start_time = time.time()
    
    burst_size = 20
    for i in range(count):
        can_id = 0x210  # Status
        data = [0x03, i % 256, random.randint(0, 255), 0x00, 0x00, 0x00, 0x00, 0x00]
        
        # Burst pattern: 20 mesaj çok hızlı, sonra bekleme
        burst_index = i % burst_size
        if burst_index < burst_size - 1:
            timestamp = start_time + (i // burst_size) * 5.0 + burst_index * 0.001
        else:
            timestamp = start_time + (i // burst_size) * 5.0 + 4.0
        
        samples.append((can_id, data, timestamp, "advanced_flood"))
    
    return samples


def generate_scenario_8_fuzzing(count: int = 50):
    """Senaryo #8: OCPP Protocol Fuzzing"""
    logger.info(f"  Senaryo #8 (Fuzzing): {count} örnek üretiliyor...")
    samples = []
    start_time = time.time()
    
    for i in range(count):
        # Rastgele CAN ID (geçerli ve geçersiz karışık)
        if i % 3 == 0:
            can_id = random.randint(0, 2047)  # Tamamen rastgele
        else:
            can_id = random.choice([0x200, 0x201]) ^ random.randint(0, 15)  # Bit flip
        
        # Farklı DLC değerleri (normal 8, fuzz: 0-8)
        dlc = random.randint(0, 8)
        data = [random.randint(0, 255) for _ in range(dlc)] + [0x00] * (8 - dlc)
        
        timestamp = start_time + i * random.uniform(0.01, 0.1)
        samples.append((can_id, data, timestamp, "fuzzing"))
    
    return samples


def generate_scenario_9_poisoning(count: int = 50):
    """Senaryo #9: Sensor Data Poisoning"""
    logger.info(f"  Senaryo #9 (Poisoning): {count} örnek üretiliyor...")
    samples = []
    start_time = time.time()
    
    # Baseline değer
    baseline = 100
    
    for i in range(count):
        can_id = 0x230  # Energy meter
        
        # Kademeli drift: Her örnekte %5 sapma
        drift_factor = 1.0 + (i / count) * 0.5  # %0 -> %50 drift
        poisoned_value = int(baseline * drift_factor)
        
        data = [0x05, poisoned_value % 256, (poisoned_value >> 8) % 256, 
                0x00, 0x00, 0x00, 0x00, 0x00]
        
        timestamp = start_time + i * random.uniform(1.0, 5.0)
        samples.append((can_id, data, timestamp, "poisoning"))
    
    return samples


def generate_all_anomaly_traffic():
    """Tüm senaryolar için anomali trafiği üret"""
    logger.info("="*60)
    logger.info("9 SENARYO İÇİN ANOMALİ TRAFİĞİ ÜRETİLİYOR")
    logger.info("="*60)
    
    all_samples = []
    
    # Her senaryo için anomali üret
    all_samples.extend(generate_scenario_1_mitm(50))
    all_samples.extend(generate_scenario_2_dos_flood(100))
    all_samples.extend(generate_scenario_3_sampling(50))
    all_samples.extend(generate_scenario_4_fail_open(50))
    all_samples.extend(generate_scenario_5_ransomware(50))
    all_samples.extend(generate_scenario_6_latency(50))
    all_samples.extend(generate_scenario_7_advanced_flood(100))
    all_samples.extend(generate_scenario_8_fuzzing(50))
    all_samples.extend(generate_scenario_9_poisoning(50))
    
    logger.info(f"✓ Toplam {len(all_samples)} anomali örneği üretildi")
    return all_samples


# ============================================================================
# MODEL EĞİTİMİ
# ============================================================================

def train_model(
    normal_count: int = 2000,
    save_path: str = "./models/isolation_forest.pkl"
):
    """
    Isolation Forest modelini eğit ve kaydet.
    Hibrit yaklaşım: Normal trafik üzerinde unsupervised eğitim.
    """
    if not SKLEARN_AVAILABLE:
        logger.error("scikit-learn kurulu değil!")
        logger.info("Kurmak için: pip install scikit-learn")
        return False
    
    logger.info("="*60)
    logger.info("ML MODEL EĞİTİMİ BAŞLIYOR")
    logger.info("Yaklaşım: Hibrit (Rule-based + ML)")
    logger.info("Algoritma: Isolation Forest (Unsupervised)")
    logger.info("="*60)
    
    # ML-IDS oluştur (contamination = anomali oranı tahmini)
    ml_ids = MLBasedIDS(contamination=0.1)
    
    # Normal trafik üret ve ekle
    normal_samples = generate_normal_traffic(normal_count)
    
    logger.info("\nNormal örnekler ML-IDS'e ekleniyor...")
    for can_id, data, timestamp, _ in normal_samples:
        ml_ids.add_training_sample(can_id, data, timestamp)
    
    # Modeli eğit
    logger.info(f"\nModel eğitiliyor ({len(ml_ids.training_buffer)} örnek)...")
    success = ml_ids.train(min_samples=100)
    
    if not success:
        logger.error("❌ Model eğitimi başarısız!")
        return False
    
    logger.success("✓ Model başarıyla eğitildi")
    
    # ========== TEST ==========
    logger.info("\n" + "="*60)
    logger.info("MODEL TESTİ - 9 SENARYO")
    logger.info("="*60)
    
    # Normal trafik testi
    test_normal = generate_normal_traffic(200)
    normal_correct = 0
    
    for can_id, data, timestamp, _ in test_normal:
        is_anomaly, score = ml_ids.predict(can_id, data, timestamp)
        if not is_anomaly:
            normal_correct += 1
    
    normal_accuracy = (normal_correct / len(test_normal)) * 100
    logger.info(f"\n📊 Normal Trafik: {normal_accuracy:.1f}% doğru (normal olarak sınıflandı)")
    
    # Anomali trafik testi (senaryo bazlı)
    anomaly_samples = generate_all_anomaly_traffic()
    
    # Senaryo bazlı sonuçları topla
    scenario_results = {}
    for can_id, data, timestamp, scenario in anomaly_samples:
        is_anomaly, score = ml_ids.predict(can_id, data, timestamp)
        
        if scenario not in scenario_results:
            scenario_results[scenario] = {"total": 0, "detected": 0}
        
        scenario_results[scenario]["total"] += 1
        if is_anomaly:
            scenario_results[scenario]["detected"] += 1
    
    # Sonuçları yazdır
    logger.info("\n📊 Senaryo Bazlı Tespit Oranları:")
    logger.info("-" * 50)
    
    total_detected = 0
    total_samples = 0
    
    scenario_names = {
        "mitm": "Senaryo #1 (MitM)",
        "flood": "Senaryo #2 (DoS Flood)",
        "sampling": "Senaryo #3 (Sampling)",
        "fail_open": "Senaryo #4 (Fail-Open)",
        "ransomware": "Senaryo #5 (Ransomware)",
        "latency": "Senaryo #6 (Latency)",
        "advanced_flood": "Senaryo #7 (Adv. Flood)",
        "fuzzing": "Senaryo #8 (Fuzzing)",
        "poisoning": "Senaryo #9 (Poisoning)"
    }
    
    for scenario, results in scenario_results.items():
        accuracy = (results["detected"] / results["total"]) * 100
        total_detected += results["detected"]
        total_samples += results["total"]
        
        status = "✅" if accuracy >= 70 else "⚠️" if accuracy >= 50 else "❌"
        name = scenario_names.get(scenario, scenario)
        logger.info(f"  {status} {name}: {accuracy:.1f}% ({results['detected']}/{results['total']})")
    
    overall_accuracy = (total_detected / total_samples) * 100
    logger.info("-" * 50)
    logger.info(f"  📈 Genel Anomali Tespit Oranı: {overall_accuracy:.1f}%")
    
    # Modeli kaydet
    logger.info(f"\n💾 Model kaydediliyor: {save_path}")
    
    # Dizin yoksa oluştur
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    if ml_ids.save_model(save_path):
        logger.success(f"✓ Model kaydedildi: {save_path}")
        
        # Özet
        logger.info("\n" + "="*60)
        logger.info("EĞİTİM ÖZETİ")
        logger.info("="*60)
        logger.info(f"  📊 Normal Trafik Doğruluğu: {normal_accuracy:.1f}%")
        logger.info(f"  📊 Anomali Tespit Oranı: {overall_accuracy:.1f}%")
        logger.info(f"  💾 Model Konumu: {save_path}")
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
    
    logger.info("\n")
    logger.info("🤖 Elektrikli Araç Şarj İstasyonu Güvenlik Sistemi")
    logger.info("📚 ML Model Eğitim Scripti - 9 Senaryo Desteği")
    logger.info("\n")
    
    # Model eğit
    success = train_model(
        normal_count=2000,
        save_path="./models/isolation_forest.pkl"
    )
    
    if success:
        logger.success("\n✅ Model eğitimi tamamlandı!")
        logger.info("   secure_bridge.py başlatıldığında bu model otomatik yüklenecek.")
        logger.info("   Dashboard'da ML-IDS: True olarak görünecek.")
    else:
        logger.error("\n❌ Eğitim başarısız!")
        sys.exit(1)


if __name__ == "__main__":
    main()
