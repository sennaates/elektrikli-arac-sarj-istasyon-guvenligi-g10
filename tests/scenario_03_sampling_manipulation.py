"""
SENARYO #3: ADAPTİF ÖRNEKLEME MANİPÜLASYONU (Sampling Manipulation)

Tehdit Sınıflandırması:
- Saldırı Tipi: Data Manipulation / Energy Theft
- Hedeflenen Varlık: MeterValues / Energy Metering System
- Etkilenen Özellik: Bütünlük (Integrity) + Faturalandırma
- Kategori: Siber Tehditler + Ekonomik Zarar

STRIDE Modeli Analizi:
- Tampering (T): Ağırlıklı tehdit (veri manipülasyonu)
- Repudiation (R): Eksik kayıt → inkar edilebilir işlem
- Information Disclosure (I): Gerçek tüketim gizlenir
"""

import numpy as np

# SENARYO PARAMETRELERİ
SCENARIO_CONFIG = {
    "id": "SCENARIO-03",
    "name": "Adaptive Sampling Manipulation",
    "severity": "CRITICAL",
    "category": "Data Manipulation / Energy Theft",
    
    # Normal Davranış
    "normal_behavior": {
        "sampling_rate": 60,  # sample/minute (her saniye 1 sample)
        "sampling_interval": 1.0,  # saniye
        "variance_range": (0.3, 1.5),  # kWh^2 (normal varyans aralığı)
        "peak_visibility": True,  # Peak değerler görünür
        "buffer_ratio": 1.0  # raw/sent = 1:1
    },
    
    # Anomali Davranış
    "anomaly_behavior": {
        "sampling_rate": 1,  # sample/minute (her 60 saniyede 1 sample)
        "sampling_interval": 60.0,  # saniye
        "variance_range": (0.01, 0.1),  # kWh^2 (çok düşük varyans)
        "peak_visibility": False,  # Peak'ler gizlenir
        "buffer_ratio": 30.0  # raw/sent = 30:1 (çok fazla veri birikimi)
    },
    
    # Saldırı Parametreleri
    "attack": {
        "scenarios": [
            {
                "id": "rate_drop",
                "name": "Sampling Rate Drop",
                "description": "Örnekleme oranını 1s → 60s düşür",
                "duration": 120.0,  # saniye
                "detection_metric": "samples_per_minute"
            },
            {
                "id": "peak_smoothing",
                "name": "Peak Smoothing",
                "description": "Yüksek değerleri ortala ve gizle",
                "duration": 120.0,
                "detection_metric": "energy_variance"
            },
            {
                "id": "buffer_manipulation",
                "name": "Buffer Manipulation",
                "description": "Ham veriyi buffer'da tut, gönderme",
                "duration": 120.0,
                "detection_metric": "raw_sent_ratio"
            }
        ]
    },
    
    # Tespit Kuralları
    "detection": {
        # Kural-1: Sampling Rate Drop
        "rule_1": {
            "id": "SAMPLING_RATE_DROP",
            "condition": "samples_per_minute < 30",
            "threshold": 30,  # minimum sample/minute
            "severity": "HIGH",
            "window": 60.0  # saniye
        },
        
        # Kural-2: Variance Drop (Energy Flatness)
        "rule_2": {
            "id": "ENERGY_VARIANCE_DROP",
            "condition": "current_variance < historical_variance * 0.30",
            "threshold": 0.30,  # %30 drop
            "severity": "CRITICAL",
            "window": 300.0  # saniye (5 dakika)
        },
        
        # Kural-3: Buffer Mismatch
        "rule_3": {
            "id": "BUFFER_MANIPULATION",
            "condition": "raw_buffer_size / sent_count > 2.0",
            "threshold": 2.0,  # 2x ratio
            "severity": "CRITICAL"
        },
        
        # ML-based detection
        "ml_features": [
            "sampling_rate",  # sample/minute
            "variance_score",  # Rolling variance
            "inter_sample_time",  # Sample'lar arası süre
            "peak_count",  # Yüksek değer sayısı
            "smoothness"  # Veri düzgünlüğü
        ],
        "ml_threshold": 0.75
    },
    
    # Beklenen Etkiler
    "impacts": {
        "financial": {
            "severity": "CRITICAL",
            "description": "Gelir kaybı (eksik ücretlendirme)",
            "estimated_loss": "15-30% of actual energy cost",
            "examples": [
                "10 kWh gerçek tüketim → 7 kWh faturalandırıldı",
                "Peak saatlerde yüksek tüketim gizlendi",
                "Aylık 1000 € yerine 700 € tahsil edildi"
            ]
        },
        "operational": {
            "severity": "HIGH",
            "description": "Kapasite planlama hatası",
            "effects": [
                "Peak load yanlış tahmin edilir",
                "Şebeke dengeleme sorunları",
                "Transformatör aşırı yüklenmesi"
            ]
        },
        "security": {
            "severity": "MEDIUM",
            "description": "Koruma sistemleri bypass",
            "effects": [
                "Ani yük artışı algılanamaz",
                "Otomatik kesici tetiklenmez",
                "Şebeke koruma devre dışı"
            ]
        }
    },
    
    # Tespit Örneği
    "detection_example": {
        "timestamp": "2025-11-23 12:34:56",
        "session_id": "SESSION-12345",
        "alerts": [
            {
                "rule": "SAMPLING_RATE_DROP",
                "samples_per_minute": 5,
                "threshold": 30,
                "message": "Örnekleme oranı düştü: 5 sample/min (min: 30)"
            },
            {
                "rule": "ENERGY_VARIANCE_DROP",
                "current_variance": 0.08,
                "historical_variance": 0.65,
                "drop_ratio": 0.12,
                "message": "Enerji varyansı anormal düştü (peak gizleniyor olabilir)"
            },
            {
                "rule": "BUFFER_MANIPULATION",
                "raw_buffer_size": 180,
                "sent_count": 5,
                "ratio": 36.0,
                "message": "Ham veri buffer anormali (yerelde veri birikiyor)"
            }
        ]
    },
    
    # Test Senaryoları
    "test_cases": [
        {
            "id": "TC-03-001",
            "name": "Sampling Rate Drop Detection",
            "description": "1 saniye → 60 saniye örnekleme düşüşü",
            "params": {
                "scenario": "rate_drop",
                "duration": 120.0,
                "normal_rate": 60,
                "manipulated_rate": 1
            },
            "expected_alerts": ["SAMPLING_RATE_DROP"],
            "expected_detection_time": "< 60 seconds"
        },
        {
            "id": "TC-03-002",
            "name": "Peak Smoothing Detection",
            "description": "Yüksek değerleri ortalama ile gizleme",
            "params": {
                "scenario": "peak_smoothing",
                "duration": 120.0,
                "real_power_range": (7.0, 15.0),
                "sent_power_range": (9.5, 10.5)
            },
            "expected_alerts": ["ENERGY_VARIANCE_DROP"],
            "expected_detection_time": "< 300 seconds"
        },
        {
            "id": "TC-03-003",
            "name": "Buffer Manipulation Detection",
            "description": "Veri buffer'da tutulup gönderilmeme",
            "params": {
                "scenario": "buffer_manipulation",
                "duration": 120.0,
                "raw_rate": 60,
                "sent_rate": 2,
                "expected_ratio": 30.0
            },
            "expected_alerts": ["BUFFER_MANIPULATION"],
            "expected_detection_time": "< 30 seconds"
        },
        {
            "id": "TC-03-004",
            "name": "Combined Manipulation",
            "description": "Rate + variance + buffer manipülasyonu",
            "params": {
                "scenarios": ["rate_drop", "peak_smoothing", "buffer_manipulation"],
                "duration": 180.0
            },
            "expected_alerts": [
                "SAMPLING_RATE_DROP",
                "ENERGY_VARIANCE_DROP",
                "BUFFER_MANIPULATION"
            ],
            "expected_detection_time": "< 60 seconds"
        }
    ],
    
    # Performans Gereksinimleri
    "performance_requirements": {
        "detection_accuracy": 0.95,  # ≥%95
        "false_positive_rate": 0.03,  # ≤%3
        "detection_latency": {
            "rate_drop": 60.0,  # < 60 saniye
            "variance_drop": 300.0,  # < 5 dakika
            "buffer_mismatch": 30.0  # < 30 saniye
        },
        "data_overhead": 0.05  # < %5 ek veri
    },
    
    # Mitigasyon Stratejileri
    "mitigations": {
        "preventive": {
            "priority": 1,
            "measures": [
                "Minimum örnekleme zorunluluğu (firmware seviyesi)",
                "Sampling parametrelerinin imzalanması (anti-tampering)",
                "Firmware bütünlük kontrolü (secure boot)",
                "Örnekleme değişikliklerini loglama"
            ]
        },
        "detective": {
            "priority": 1,
            "measures": [
                "Varyans + percentile tabanlı anomaly detection (p95, p99)",
                "Çapraz doğrulama: Araç BMS vs CP ölçümü",
                "Zaman serisi analizi (trend, seasonality)",
                "Buffer size monitoring"
            ]
        },
        "corrective": {
            "priority": 2,
            "measures": [
                "Anomali tespit edilince yüksek frekanslı örneklemeye geç",
                "Şüpheli session'ı işaretle ve detaylı log tut",
                "Operatöre real-time alarm gönder",
                "Otomatik düzeltme: Eksik enerji tahmin et ve fatura düzelt"
            ]
        },
        "reactive": {
            "priority": 3,
            "measures": [
                "Forensic analiz için raw data backup",
                "Manipüle edilen session'ları izole et",
                "Firmware rollback",
                "Yasal işlem için kanıt toplama"
            ]
        }
    }
}


# SİMÜLASYON FONKSİYONLARI
def simulate_normal_sampling(duration: float = 60.0):
    """Normal örnekleme davranışını simüle et."""
    import time
    samples = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # Normal: Her saniye ölçüm, yüksek varyans
        energy = 10.0 + np.random.normal(0, 1.5)  # kWh, yüksek varyans
        samples.append(energy)
        time.sleep(1.0)
    
    print(f"Normal Sampling: {len(samples)} samples")
    print(f"  - Rate: {len(samples)/duration*60:.1f} sample/min")
    print(f"  - Variance: {np.var(samples):.4f} kWh²")
    print(f"  - Peak: {max(samples):.2f} kWh")
    
    return samples


def simulate_manipulated_sampling(duration: float = 60.0, scenario: str = "rate_drop"):
    """Manipüle edilmiş örnekleme davranışını simüle et."""
    import time
    samples = []
    start_time = time.time()
    
    if scenario == "rate_drop":
        # Her 60 saniyede 1 sample
        while time.time() - start_time < duration:
            energy = 10.0 + np.random.normal(0, 0.3)  # Düşük varyans
            samples.append(energy)
            time.sleep(60.0)
    
    elif scenario == "peak_smoothing":
        # Peak'leri ortala
        buffer = []
        while time.time() - start_time < duration:
            real_energy = 10.0 + np.random.normal(0, 2.5)  # Yüksek varyans
            buffer.append(real_energy)
            
            if len(buffer) >= 10:
                # Ortalama gönder
                samples.append(np.mean(buffer))
                buffer.clear()
            
            time.sleep(1.0)
    
    print(f"Manipulated Sampling ({scenario}): {len(samples)} samples")
    print(f"  - Rate: {len(samples)/duration*60:.1f} sample/min")
    print(f"  - Variance: {np.var(samples):.4f} kWh²")
    print(f"  - 🚨 ANOMALY DETECTED")
    
    return samples


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SENARYO #3: ADAPTİF ÖRNEKLEME MANİPÜLASYONU")
    print("="*70)
    
    print("\n📋 SENARYO BİLGİLERİ:")
    print(f"  - ID: {SCENARIO_CONFIG['id']}")
    print(f"  - İsim: {SCENARIO_CONFIG['name']}")
    print(f"  - Severity: {SCENARIO_CONFIG['severity']}")
    print(f"  - Kategori: {SCENARIO_CONFIG['category']}")
    
    print("\n🎯 NORMAL vs ANOMALİ:")
    normal = SCENARIO_CONFIG['normal_behavior']
    anomaly = SCENARIO_CONFIG['anomaly_behavior']
    print(f"  Normal:")
    print(f"    - Sampling Rate: {normal['sampling_rate']} sample/min")
    print(f"    - Variance: {normal['variance_range']}")
    print(f"    - Peak Visible: {normal['peak_visibility']}")
    print(f"  Anomali:")
    print(f"    - Sampling Rate: {anomaly['sampling_rate']} sample/min ⚠️")
    print(f"    - Variance: {anomaly['variance_range']} ⚠️")
    print(f"    - Peak Visible: {anomaly['peak_visibility']} ⚠️")
    
    print("\n🛡️ TESPİT KURALLARI:")
    for rule_key in ['rule_1', 'rule_2', 'rule_3']:
        rule = SCENARIO_CONFIG['detection'][rule_key]
        print(f"  [{rule['id']}]")
        print(f"    Koşul: {rule['condition']}")
        print(f"    Severity: {rule['severity']}")
    
    print("\n📊 TEST SENARYOLARI:")
    for tc in SCENARIO_CONFIG['test_cases']:
        print(f"  [{tc['id']}] {tc['name']}")
        print(f"     → {tc['description']}")
    
    print("\n💰 ETKİLER:")
    impacts = SCENARIO_CONFIG['impacts']
    print(f"  Finansal: {impacts['financial']['estimated_loss']}")
    print(f"  Operasyonel: Kapasite planlama hatası")
    print(f"  Güvenlik: Koruma sistemleri bypass")
    
    print("\n" + "="*70)

