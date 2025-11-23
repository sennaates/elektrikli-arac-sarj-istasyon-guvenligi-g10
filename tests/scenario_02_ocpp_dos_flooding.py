"""
SENARYO #2: OCPP MESAJ YOĞUNLUĞU SALDIRISI (DoS Hazırlığı)

Tehdit Sınıflandırması:
- Saldırı Tipi: Hizmet Reddi (Denial of Service - DoS)
- Hedeflenen Varlık: Merkezi Yönetim Sistemi (CSMS)
- Etkilenen Özellik: Erişilebilirlik (Availability)
- Kategori: Siber Tehditler (Gelişmiş Tehdit)

STRIDE Modeli Analizi:
- Denial of Service (D): Ağırlıklı tehdit
- Tampering (T): Mesaj içeriği manipüle edilebilir
- Information Disclosure (I): Sistem kaynaklarının durumu açığa çıkabilir
"""

# SENARYO PARAMETRELERİ
SCENARIO_CONFIG = {
    "id": "SCENARIO-02",
    "name": "OCPP Message Flooding (DoS Preparation)",
    "severity": "CRITICAL",
    "category": "Denial of Service",
    
    # Saldırı Parametreleri
    "attack": {
        "type": "OCPP_MESSAGE_FLOODING",
        "target": "CSMS",
        "protocol": "OCPP 1.6",
        "transport": "WebSocket",
        
        # Rate parametreleri
        "normal_rate": 0.5,  # Normal: 0.5 mesaj/saniye (1 mesaj her 2 saniyede)
        "threshold_rate": 5.0,  # Eşik: 5 mesaj/saniye
        "attack_rate": 20.0,  # Saldırı: 20 mesaj/saniye (4x eşik)
        
        # Saldırı mesaj tipleri
        "message_types": [
            "Heartbeat",           # En düşük değerli, en yaygın
            "StatusNotification",  # Sık kullanılan, düşük maliyet
            "BootNotification",    # Orta maliyet
            "MeterValues"          # Orta-yüksek maliyet
        ],
        
        # Saldırı süreleri
        "short_burst": 2.0,   # Kısa burst: 2 saniye
        "medium_attack": 5.0,  # Orta saldırı: 5 saniye
        "sustained_attack": 30.0  # Sürekli saldırı: 30 saniye
    },
    
    # Tespit Kuralları
    "detection": {
        # Rule-based IDS
        "rule_id": "OCPP_RATE_LIMIT",
        "rule_name": "OCPP Message Rate Limiter",
        "threshold": 5.0,  # mesaj/saniye
        "window": 1.0,     # saniye
        "severity": "CRITICAL",
        
        # ML-based IDS
        "ml_features": [
            "message_rate",      # Mesaj/saniye
            "burst_score",       # Ani artış skoru
            "action_diversity",  # Mesaj tipi çeşitliliği
            "payload_size_avg",  # Ortalama payload boyutu
            "inter_arrival_time" # Mesajlar arası süre
        ],
        "ml_threshold": 0.7,  # Anomali skoru eşiği
        "required_accuracy": 0.95  # ≥%95 doğruluk
    },
    
    # Beklenen Etkiler
    "impacts": {
        "csms_availability": {
            "severity": "HIGH",
            "description": "CSMS erişilebilirliği kaybı",
            "effects": [
                "Kritik şarj seans yönetiminin yavaşlaması",
                "Yetkilendirme işlemlerinin gecikmesi",
                "Seans sonlandırma problemleri"
            ]
        },
        "operational_disruption": {
            "severity": "HIGH",
            "description": "Operasyonel kesinti",
            "effects": [
                "Diğer istasyonların iletişim sorunu",
                "Şarj işlemlerinin aksaması",
                "Kullanıcı deneyiminin bozulması"
            ]
        },
        "resource_exhaustion": {
            "severity": "CRITICAL",
            "description": "Kaynak tüketimi",
            "effects": [
                "Yüksek CPU kullanımı",
                "Bellek tükenmesi",
                "Ağ bandı genişliği tüketimi"
            ]
        },
        "data_loss": {
            "severity": "MEDIUM",
            "description": "Veri kaybı",
            "effects": [
                "Kritik mesajların göz ardı edilmesi",
                "Arıza bildirimlerinin işlenememesi",
                "Log verilerinin kaybolması"
            ]
        }
    },
    
    # Önlemler ve Mitigasyon
    "mitigations": {
        "real_time_intervention": {
            "priority": 1,
            "description": "Gerçek zamanlı müdahale",
            "actions": [
                "Anomali tespit edilen IP'yi geçici engelle",
                "Saldırgan CP'yi karaliste ekle",
                "Throttling uygula (rate limiting)",
                "Acil durum modu aktif et"
            ],
            "response_time": "< 30 saniye"
        },
        "rate_limiting": {
            "priority": 1,
            "description": "Rate limiting uygulaması",
            "config": {
                "per_cp_limit": 5,  # mesaj/saniye/CP
                "per_ip_limit": 10,  # mesaj/saniye/IP
                "global_limit": 100,  # mesaj/saniye (tüm sistem)
                "burst_allowance": 10  # Kısa süreli burst toleransı
            }
        },
        "traffic_shaping": {
            "priority": 2,
            "description": "Trafik şekillendirme",
            "techniques": [
                "Token bucket algorithm",
                "Leaky bucket algorithm",
                "Priority queuing (kritik mesajlar önce)"
            ]
        },
        "authentication_strengthening": {
            "priority": 2,
            "description": "Kimlik doğrulama güçlendirme",
            "measures": [
                "Mutual TLS zorunlu kılınması",
                "API key/token kontrolü",
                "CP sertifika doğrulaması",
                "Anomali tespitinde 2FA"
            ]
        },
        "logging_and_monitoring": {
            "priority": 3,
            "description": "Loglama ve izleme",
            "requirements": [
                "Yoğun trafik logları",
                "Real-time alerting",
                "Anomali pattern analizi",
                "Post-mortem analiz için veri saklama"
            ]
        }
    },
    
    # Test Senaryoları
    "test_cases": [
        {
            "id": "TC-02-001",
            "name": "Heartbeat Flooding",
            "description": "Sadece Heartbeat mesajlarıyla yoğunluk",
            "params": {
                "message_type": "Heartbeat",
                "rate": 20,
                "duration": 5.0
            },
            "expected_alerts": ["OCPP_RATE_LIMIT_EXCEEDED"],
            "expected_severity": "CRITICAL"
        },
        {
            "id": "TC-02-002",
            "name": "Mixed Message Flooding",
            "description": "Karışık mesaj tipleriyle yoğunluk",
            "params": {
                "message_types": ["Heartbeat", "StatusNotification", "BootNotification"],
                "rate": 15,
                "duration": 10.0
            },
            "expected_alerts": ["OCPP_RATE_LIMIT_EXCEEDED", "ML_ANOMALY"],
            "expected_severity": "CRITICAL"
        },
        {
            "id": "TC-02-003",
            "name": "Sustained Low-Rate Attack",
            "description": "Düşük ama sürekli yoğunluk (eşiğin hemen üstü)",
            "params": {
                "message_type": "StatusNotification",
                "rate": 6,  # Eşik: 5, bu biraz üstü
                "duration": 30.0
            },
            "expected_alerts": ["OCPP_RATE_LIMIT_EXCEEDED"],
            "expected_severity": "HIGH"
        },
        {
            "id": "TC-02-004",
            "name": "Burst Attack",
            "description": "Kısa süreli ani burst (2 saniye)",
            "params": {
                "message_type": "Heartbeat",
                "rate": 50,  # Çok yüksek
                "duration": 2.0
            },
            "expected_alerts": ["OCPP_RATE_LIMIT_EXCEEDED", "ML_BURST_DETECTED"],
            "expected_severity": "CRITICAL"
        },
        {
            "id": "TC-02-005",
            "name": "Distributed Flooding (DDoS Simulation)",
            "description": "Birden fazla CP'den eşzamanlı yoğunluk",
            "params": {
                "cp_count": 5,
                "rate_per_cp": 4,  # Her biri eşiğin altında
                "total_rate": 20,  # Toplam yüksek
                "duration": 10.0
            },
            "expected_alerts": ["GLOBAL_RATE_EXCEEDED", "DDOS_PATTERN"],
            "expected_severity": "CRITICAL"
        }
    ],
    
    # Performans Gereksinimleri
    "performance_requirements": {
        "detection_accuracy": 0.95,  # ≥%95
        "false_positive_rate": 0.05,  # ≤%5
        "detection_latency": 1.0,     # < 1 saniye
        "response_time": 30.0,        # < 30 saniye
        "system_overhead": 0.10       # < %10 CPU/memory overhead
    }
}


# SALDIRI SİMÜLASYONU
def simulate_ocpp_flooding():
    """
    OCPP flooding saldırısını simüle eder.
    
    Kullanım:
        python attack_simulator.py --attack ocpp_flood --ocpp-rate 20 --ocpp-duration 5.0
    """
    from attack_simulator import AttackSimulator
    
    simulator = AttackSimulator()
    
    # Test Case 1: Heartbeat Flooding
    print("\n" + "="*60)
    print("TEST CASE 1: Heartbeat Flooding")
    print("="*60)
    simulator.ocpp_message_flooding(
        csms_url="ws://localhost:9000",
        rate=20,
        duration=5.0,
        message_type="Heartbeat"
    )
    
    # Test Case 4: Burst Attack
    print("\n" + "="*60)
    print("TEST CASE 4: Burst Attack")
    print("="*60)
    simulator.ocpp_message_flooding(
        csms_url="ws://localhost:9000",
        rate=50,
        duration=2.0,
        message_type="Heartbeat"
    )


# BEKLENEN IDS DAVRANIŞI
EXPECTED_IDS_BEHAVIOR = """
RULE-BASED IDS:
================
1. Alert Tipi: OCPP_RATE_LIMIT_EXCEEDED
2. Severity: CRITICAL
3. Tespit Koşulu: message_rate > 5.0 mesaj/saniye
4. Tespit Süresi: < 1 saniye
5. Log Detayları:
   - messages_per_second: 20.0
   - threshold: 5.0
   - time_window: 1.0s
   - message_count: 20+
   - source_ip: 127.0.0.1

ML-BASED IDS:
=============
1. Feature'lar:
   - message_rate: 20.0 (çok yüksek → anomali)
   - burst_score: 0.9+ (ani artış → anomali)
   - inter_arrival_time: 0.05s (çok kısa → anomali)
2. Anomaly Score: 0.85+ (eşik: 0.7)
3. Prediction: -1 (anomali)
4. Detection Accuracy: ≥%95

DASHBOARD GÖRÜNTÜLENMESİ:
=========================
1. Alert Box: 🚨 KIRMIZI ALARM
2. Mesaj: "OCPP mesaj yoğunluğu saldırısı tespit edildi"
3. Grafik: OCPP rate spike (ani artış)
4. Action: "CP-001 geçici olarak engellendi"
5. Timestamp: Gerçek zamanlı güncelleme
"""


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SENARYO #2: OCPP MESAJ YOĞUNLUĞU SALDIRISI")
    print("="*70)
    
    print("\n📋 SENARYO BİLGİLERİ:")
    print(f"  - ID: {SCENARIO_CONFIG['id']}")
    print(f"  - İsim: {SCENARIO_CONFIG['name']}")
    print(f"  - Severity: {SCENARIO_CONFIG['severity']}")
    print(f"  - Kategori: {SCENARIO_CONFIG['category']}")
    
    print("\n🎯 SALDIRI PARAMETRELERİ:")
    attack = SCENARIO_CONFIG['attack']
    print(f"  - Normal Rate: {attack['normal_rate']} mesaj/s")
    print(f"  - Eşik Rate: {attack['threshold_rate']} mesaj/s")
    print(f"  - Saldırı Rate: {attack['attack_rate']} mesaj/s")
    
    print("\n🛡️ TESPİT KURALLARI:")
    detection = SCENARIO_CONFIG['detection']
    print(f"  - Kural ID: {detection['rule_id']}")
    print(f"  - Eşik: {detection['threshold']} mesaj/s")
    print(f"  - Pencere: {detection['window']} saniye")
    print(f"  - ML Doğruluk: ≥{detection['required_accuracy']*100:.0f}%")
    
    print("\n📊 TEST SENARYOLARI:")
    for tc in SCENARIO_CONFIG['test_cases']:
        print(f"  [{tc['id']}] {tc['name']}")
        print(f"     → {tc['description']}")
    
    print("\n✅ PERFORMANS GEREKSİNİMLERİ:")
    perf = SCENARIO_CONFIG['performance_requirements']
    print(f"  - Tespit Doğruluğu: ≥{perf['detection_accuracy']*100:.0f}%")
    print(f"  - Yanlış Pozitif: ≤{perf['false_positive_rate']*100:.0f}%")
    print(f"  - Tespit Gecikmesi: < {perf['detection_latency']} saniye")
    print(f"  - Müdahale Süresi: < {perf['response_time']} saniye")
    
    print("\n" + "="*70)

