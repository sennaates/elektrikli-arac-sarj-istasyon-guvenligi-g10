"""
SENARYO #4: OCPP MESAJ YOĞUNLUĞU SALDIRISI (DoS Hazırlığı) - Gelişmiş Versiyon

Bu senaryo, bir elektrikli araç şarj istasyonundan (CP) merkezi yönetim sistemine (CSMS) 
doğru, normalin çok üzerinde ve kısa süreliğine yüksek hacimli, anlamsız OCPP iletişim 
mesajlarının gönderilmesi durumunu inceler. Temel hedef, CSMS'nin iletişim kaynaklarını 
tüketerek hizmet reddine (DoS) yol açmak veya diğer istasyonların kritik iletişimini engellemektir.

Tehdit Sınıflandırması:
- Saldırı Tipi: Hizmet Reddi (Denial of Service - DoS)
- Hedeflenen Varlık: Merkezi Yönetim Sistemi (CSMS)
- Etkilenen Özellik: Erişilebilirlik (Availability)
- Kategori: Siber Tehditler (Gelişmiş Tehdit)

STRIDE Modeli Analizi:
- Denial of Service (D): Ağırlıklı tehdit
- Tampering (T): Mesaj içeriği manipüle edilebilir
- Information Disclosure (I): Sistem kaynaklarının durumu açığa çıkabilir
- Spoofing (S): Sahte istemci kullanımı
"""

# SENARYO PARAMETRELERİ
SCENARIO_CONFIG = {
    "id": "SCENARIO-04",
    "name": "OCPP Advanced Message Flooding (DoS Preparation)",
    "severity": "CRITICAL",
    "category": "Denial of Service",
    
    # Senaryo Özeti
    "summary": {
        "description": "CP'den CSMS'e doğru, normalin çok üzerinde ve kısa süreliğine yüksek hacimli, anlamsız OCPP iletişim mesajlarının gönderilmesi",
        "objective": "CSMS'nin iletişim kaynaklarını tüketerek hizmet reddine (DoS) yol açmak veya diğer istasyonların kritik iletişimini engellemek",
        "scope": {
            "protocol": "OCPP (Open Charge Point Protocol), özellikle Heartbeat.req, StatusNotification.req gibi düşük değerli mesajlar",
            "components": "Şarj İstasyonu (CP), Merkezi Yönetim Sistemi (CSMS)",
            "channel": "CP ile CSMS arasındaki ağ bağlantısı",
            "measurement_period": "Saniyelik veya birkaç saniyelik mikro aralıklar"
        }
    },
    
    # Gerekli Koşullar
    "prerequisites": [
        "Saldırganın, hedef şarj istasyonunun (CP) yazılımına veya donanımına fiziksel ya da siber olarak erişim sağlamış olması (Ele geçirilmiş cihaz)",
        "CP'nin mesaj gönderme hızına (rate limit) dair etkili bir kısıtlamanın olmaması veya bu kısıtlamanın atlanabilmesi",
        "Saldırganın, OCPP mesaj yapısını ve temel iletişim mekanizmasını biliyor olması"
    ],
    
    # Saldırı Parametreleri
    "attack": {
        "type": "OCPP_ADVANCED_MESSAGE_FLOODING",
        "target": "CSMS",
        "protocol": "OCPP 1.6",
        "transport": "WebSocket",
        
        # Rate parametreleri
        "normal_rate": 0.5,  # Normal: 0.5 mesaj/saniye (1 mesaj her 2 saniyede)
        "threshold_rate": 5.0,  # Eşik: 5 mesaj/saniye (≥%95 doğruluk için)
        "attack_rate": 20.0,  # Saldırı: 20 mesaj/saniye (4x eşik)
        "extreme_rate": 100.0,  # Aşırı saldırı: 100 mesaj/saniye
        
        # Saldırı mesaj tipleri (düşük değerli mesajlar)
        "message_types": [
            "Heartbeat",           # En düşük değerli, en yaygın
            "StatusNotification",  # Sık kullanılan, düşük maliyet
            "BootNotification",    # Orta maliyet
            "MeterValues"          # Orta-yüksek maliyet
        ],
        
        # Saldırı yöntemleri
        "methods": {
            "high_frequency": {
                "description": "Yüksek Frekanslı Mesaj Gönderimi",
                "technique": "Bir script veya kötü amaçlı yazılım kullanarak, saniyelik bazda yüzlerce gereksiz veya tekrarlayıcı mesajı CSMS'e pompalamak",
                "rate": 20.0,
                "duration": 5.0
            },
            "botnet_like": {
                "description": "Botnet Benzeri Yöntem",
                "technique": "Ele geçirilmiş birden fazla CP'den eş zamanlı olarak düşük yoğunluklu mesajlar göndererek (DDoS), merkezi sistemi dağıtık olarak aşırı yüklemek",
                "rate_per_cp": 3.0,  # Her CP'den 3 mesaj/s
                "cp_count": 10,  # 10 CP'den
                "total_rate": 30.0,  # Toplam 30 mesaj/s
                "duration": 10.0
            },
            "spoofed_client": {
                "description": "Sahte İstemci Kullanımı",
                "technique": "Saldırganın ağ üzerinden, kendisini geçerli bir şarj istasyonu gibi göstererek yüksek yoğunluklu trafik oluşturması",
                "rate": 25.0,
                "duration": 8.0,
                "fake_cp_ids": ["CP_FAKE_001", "CP_FAKE_002", "CP_FAKE_003"]
            }
        },
        
        # Saldırı süreleri
        "short_burst": 2.0,   # Kısa burst: 2 saniye
        "medium_attack": 5.0,  # Orta saldırı: 5 saniye
        "sustained_attack": 30.0  # Sürekli saldırı: 30 saniye
    },
    
    # Tespit Yöntemleri
    "detection": {
        # Davranışsal Analiz
        "behavioral_analysis": {
            "threshold_check": {
                "rule_id": "OCPP_RATE_LIMIT",
                "rule_name": "OCPP Message Rate Limiter",
                "threshold": 5.0,  # mesaj/saniye
                "window": 1.0,     # saniye
                "severity": "CRITICAL",
                "description": "Saniyelik veya dakikalık bazda gelen mesaj sayısının (Rate) tarihsel ortalamanın çok üzerine çıkmasını (örneğin > 5 mesaj/s) kural tabanlı olarak tespit etmek"
            },
            "anomaly_detection": {
                "method": "Yapay Zeka (ML-based)",
                "description": "Geçmiş verilerden öğrenilen normal iletişim profiline göre, mesaj hacmindeki ani ve hızlı artışların (Spike) ≥%95 doğrulukla tespit edilmesi (Sapma tespiti)",
                "ml_features": [
                    "message_rate",      # Mesaj/saniye
                    "burst_score",       # Ani artış skoru
                    "action_diversity",  # Mesaj tipi çeşitliliği
                    "payload_size_avg",  # Ortalama payload boyutu
                    "inter_arrival_time" # Mesajlar arası süre
                ],
                "ml_threshold": 0.7,  # Anomali skoru eşiği
                "required_accuracy": 0.95  # ≥%95 doğruluk
            }
        },
        
        # Veri Bütünlüğü Analizi
        "data_integrity_analysis": {
            "description": "Mesajların içeriklerinin (payload) mantıksal olarak tutarlı olup olmadığının kontrol edilmesi (çok sayıda aynı veya anlamsız mesaj)",
            "checks": [
                "Aynı mesaj içeriğinin tekrarı",
                "Anlamsız payload değerleri",
                "Tutarsız mesaj sırası"
            ]
        },
        
        # İletişim Kalite İzleme
        "communication_quality_monitoring": {
            "description": "Ağ gecikmesindeki (latency) ve paket kaybı (packet loss) oranındaki ani bozulmaları izleme",
            "metrics": [
                "latency_spike",  # Gecikme artışı
                "packet_loss_rate",  # Paket kaybı oranı
                "connection_drops"  # Bağlantı kopmaları
            ]
        }
    },
    
    # Beklenen Etkiler
    "impacts": {
        "csms_availability": {
            "severity": "HIGH",
            "description": "CSMS erişilebilirliği kaybı",
            "effects": [
                "Kritik şarj seans yönetiminin (yetkilendirme, seans sonlandırma) yavaşlaması veya tamamen durması",
                "Yetkilendirme işlemlerinin gecikmesi",
                "Seans sonlandırma problemleri"
            ]
        },
        "operational_disruption": {
            "severity": "HIGH",
            "description": "Operasyonel kesinti",
            "effects": [
                "Diğer sağlıklı şarj istasyonlarının CSMS ile iletişim kuramaması veya gecikmeli kurması",
                "Şarj işlemlerinin aksaması",
                "Kullanıcı deneyiminin bozulması"
            ]
        },
        "resource_exhaustion": {
            "severity": "CRITICAL",
            "description": "Kaynak tüketimi",
            "effects": [
                "CSMS sunucusunda yüksek CPU kullanımı",
                "Bellek tükenmesi",
                "Ağ bandı genişliği tüketimi"
            ]
        },
        "data_loss": {
            "severity": "MEDIUM",
            "description": "Veri kaybı",
            "effects": [
                "Yoğunluk nedeniyle CSMS'in bazı kritik mesajları (örneğin arıza bildirimleri) görmezden gelmesi veya işleyememesi",
                "Log verilerinin kaybolması"
            ]
        }
    },
    
    # Önlemler ve Mitigasyon
    "mitigations": {
        "real_time_intervention": {
            "priority": 1,
            "description": "Gerçek Zamanlı Müdahale",
            "actions": [
                "Anomali tespit edildiği anda, saldırgan IP adresinin veya şarj istasyonunun iletişiminin geçici olarak kısıtlanması (throttling/karaliste)",
                "Saldırgan CP'yi karaliste ekle",
                "Tamamen engellenmesi",
                "Acil durum modu aktif et"
            ],
            "response_time": "< 30 saniye",  # Tespitten sonra 30 saniye içinde
            "required": True
        },
        "rate_limiting": {
            "priority": 1,
            "description": "Rate Limiting Uygulanması",
            "description_detail": "CSMS tarafında, her bir şarj istasyonundan veya IP adresinden gelen saniyelik mesaj sayısına katı bir üst sınır (Rate Limit) koyulması",
            "config": {
                "per_cp_limit": 5,  # mesaj/saniye/CP
                "per_ip_limit": 10,  # mesaj/saniye/IP
                "global_limit": 100,  # mesaj/saniye (tüm sistem)
                "burst_allowance": 10  # Kısa süreli burst toleransı
            }
        },
        "secure_communication": {
            "priority": 2,
            "description": "Güvenilir İletişim Protokolleri",
            "description_detail": "İletişimin güvenli tüneller veya kriptografik protokoller üzerinden yapılması, ancak bu saldırı tipinde trafik hacmi asıl sorundur",
            "techniques": [
                "Mutual TLS zorunlu kılınması",
                "API key/token kontrolü",
                "CP sertifika doğrulaması"
            ]
        },
        "logging_and_analysis": {
            "priority": 3,
            "description": "Olay Kaydı ve Analiz",
            "description_detail": "Yoğunluk yaşanan trafik verilerinin detaylı loglanarak gelecekteki analizler için kullanılması",
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
            "id": "TC-04-001",
            "name": "High Frequency Heartbeat Flooding",
            "description": "Sadece Heartbeat mesajlarıyla yüksek frekanslı yoğunluk",
            "params": {
                "message_type": "Heartbeat",
                "rate": 20.0,
                "duration": 5.0
            },
            "expected_alerts": ["OCPP_RATE_LIMIT_EXCEEDED"],
            "expected_severity": "CRITICAL",
            "expected_detection_time": "< 1 saniye",
            "expected_intervention_time": "< 30 saniye"
        },
        {
            "id": "TC-04-002",
            "name": "Botnet-like Distributed Attack",
            "description": "Birden fazla CP'den eş zamanlı düşük yoğunluklu mesajlar (DDoS)",
            "params": {
                "message_types": ["Heartbeat", "StatusNotification"],
                "rate_per_cp": 3.0,
                "cp_count": 10,
                "total_rate": 30.0,
                "duration": 10.0
            },
            "expected_alerts": ["OCPP_RATE_LIMIT_EXCEEDED", "ML_ANOMALY", "DISTRIBUTED_ATTACK"],
            "expected_severity": "CRITICAL",
            "expected_detection_time": "< 2 saniye",
            "expected_intervention_time": "< 30 saniye"
        },
        {
            "id": "TC-04-003",
            "name": "Spoofed Client Attack",
            "description": "Sahte istemci kullanarak yüksek yoğunluklu trafik",
            "params": {
                "message_type": "StatusNotification",
                "rate": 25.0,
                "duration": 8.0,
                "fake_cp_ids": ["CP_FAKE_001", "CP_FAKE_002", "CP_FAKE_003"]
            },
            "expected_alerts": ["OCPP_RATE_LIMIT_EXCEEDED", "SPOOFED_CLIENT_DETECTED"],
            "expected_severity": "CRITICAL",
            "expected_detection_time": "< 1 saniye",
            "expected_intervention_time": "< 30 saniye"
        },
        {
            "id": "TC-04-004",
            "name": "Sustained Low-Rate Attack",
            "description": "Düşük ama sürekli yoğunluk (eşiğin hemen üstü)",
            "params": {
                "message_type": "StatusNotification",
                "rate": 6.0,  # Eşik: 5, bu biraz üstü
                "duration": 30.0
            },
            "expected_alerts": ["OCPP_RATE_LIMIT_EXCEEDED"],
            "expected_severity": "HIGH",
            "expected_detection_time": "< 5 saniye",
            "expected_intervention_time": "< 30 saniye"
        }
    ],
    
    # Performans Gereksinimleri
    "performance_requirements": {
        "detection_accuracy": {
            "minimum": 0.95,  # ≥%95 doğruluk
            "target": 0.98,
            "description": "Yapay zeka tabanlı Anomali Tespit Sistemi'nin, davranışsal eşik aşımlarını ≥%95 doğrulukla ve hızlı bir şekilde tespit etme yeteneği"
        },
        "response_time": {
            "detection": "< 2 saniye",
            "intervention": "< 30 saniye",
            "description": "Gerçek Zamanlı İzleme ve Müdahale Modülü'nün, tespitten sonra 30 saniye içinde proaktif bir önleme aksiyonu alabilmesi"
        }
    }
}


def simulate_advanced_flooding_attack(
    method: str = "high_frequency",
    rate: float = 20.0,
    duration: float = 5.0,
    message_type: str = "Heartbeat"
):
    """
    Senaryo #4: Gelişmiş OCPP Mesaj Yoğunluğu Saldırısı Simülasyonu
    
    Args:
        method: Saldırı yöntemi ("high_frequency", "botnet_like", "spoofed_client")
        rate: Mesaj gönderme hızı (mesaj/saniye)
        duration: Saldırı süresi (saniye)
        message_type: Mesaj tipi
    """
    import time
    from utils.ids import RuleBasedIDS
    
    print(f"\n{'='*70}")
    print(f"SENARYO #4: GELİŞMİŞ OCPP MESAJ YOĞUNLUĞU SALDIRISI")
    print(f"{'='*70}")
    print(f"\n📋 Saldırı Parametreleri:")
    print(f"  - Yöntem: {method}")
    print(f"  - Rate: {rate} mesaj/saniye")
    print(f"  - Süre: {duration} saniye")
    print(f"  - Mesaj Tipi: {message_type}")
    print(f"  - Eşik: {SCENARIO_CONFIG['attack']['threshold_rate']} mesaj/saniye")
    
    ids = RuleBasedIDS()
    alerts = []
    start_time = time.time()
    message_count = 0
    
    print(f"\n🚨 Saldırı başlatılıyor...")
    
    while time.time() - start_time < duration:
        # OCPP mesajı simüle et
        alert = ids.check_ocpp_message(
            message_type,
            {},
            time.time()
        )
        
        if alert:
            alerts.append(alert)
            print(f"  ⚠️  Alert tespit edildi: {alert.alert_type} ({alert.severity})")
        
        message_count += 1
        time.sleep(1.0 / rate)  # Rate'e göre bekle
    
    elapsed_time = time.time() - start_time
    actual_rate = message_count / elapsed_time if elapsed_time > 0 else 0
    
    print(f"\n{'='*70}")
    print(f"📊 Saldırı Sonuçları:")
    print(f"  - Gönderilen mesaj: {message_count}")
    print(f"  - Gerçek rate: {actual_rate:.2f} mesaj/saniye")
    print(f"  - Tespit edilen alert: {len(alerts)}")
    print(f"  - Süre: {elapsed_time:.2f} saniye")
    
    if alerts:
        print(f"\n✅ BAŞARILI: {len(alerts)} alert tespit edildi")
        for alert in alerts[:5]:  # İlk 5 alert'i göster
            print(f"  - {alert.alert_type} ({alert.severity})")
        if len(alerts) > 5:
            print(f"  ... ve {len(alerts) - 5} alert daha")
    else:
        print(f"\n❌ BAŞARISIZ: Alert tespit edilmedi")
    
    return alerts


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SENARYO #4: GELİŞMİŞ OCPP MESAJ YOĞUNLUĞU SALDIRISI")
    print("="*70)
    
    print("\n📋 SENARYO BİLGİLERİ:")
    print(f"  - ID: {SCENARIO_CONFIG['id']}")
    print(f"  - İsim: {SCENARIO_CONFIG['name']}")
    print(f"  - Severity: {SCENARIO_CONFIG['severity']}")
    print(f"  - Kategori: {SCENARIO_CONFIG['category']}")
    
    print("\n🎯 SALDIRI YÖNTEMLERİ:")
    for method_key, method_data in SCENARIO_CONFIG['attack']['methods'].items():
        print(f"  [{method_key}]")
        print(f"    Açıklama: {method_data['description']}")
        print(f"    Teknik: {method_data['technique']}")
    
    print("\n🛡️ TESPİT YÖNTEMLERİ:")
    detection = SCENARIO_CONFIG['detection']
    print(f"  - Eşik Kontrolü: {detection['behavioral_analysis']['threshold_check']['threshold']} mesaj/s")
    print(f"  - ML Doğruluk: ≥{detection['behavioral_analysis']['anomaly_detection']['required_accuracy']*100}%")
    print(f"  - Veri Bütünlüğü Analizi: Aktif")
    print(f"  - İletişim Kalite İzleme: Aktif")
    
    print("\n📊 TEST SENARYOLARI:")
    for tc in SCENARIO_CONFIG['test_cases']:
        print(f"  [{tc['id']}] {tc['name']}")
        print(f"     → {tc['description']}")
        print(f"     → Beklenen Alert: {', '.join(tc['expected_alerts'])}")
        print(f"     → Müdahale Süresi: {tc['expected_intervention_time']}")
    
    print("\n💰 ETKİLER:")
    impacts = SCENARIO_CONFIG['impacts']
    for impact_key, impact_data in impacts.items():
        print(f"  {impact_data['description']}: {impact_data['severity']}")
    
    print("\n⚡ PERFORMANS GEREKSİNİMLERİ:")
    perf = SCENARIO_CONFIG['performance_requirements']
    print(f"  - Tespit Doğruluğu: ≥{perf['detection_accuracy']['minimum']*100}%")
    print(f"  - Tespit Süresi: {perf['response_time']['detection']}")
    print(f"  - Müdahale Süresi: {perf['response_time']['intervention']}")
    
    print("\n" + "="*70)
    print("\n💡 Test çalıştırmak için:")
    print("  python tests/scenario_04_ocpp_advanced_flooding.py")
    print("="*70 + "\n")

