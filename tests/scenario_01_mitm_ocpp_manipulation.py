"""
Anomali Senaryosu #1: Man-in-the-Middle OCPP Manipulation
OCPP mesajlarının transit sırasında değiştirilmesi ve CAN-Bus'a yanlış komutların iletilmesi.
"""

SCENARIO_01 = {
    "id": 1,
    "name": "Man-in-the-Middle (MitM) OCPP Mesaj Manipülasyonu",
    "category": "Tampering / Spoofing",
    "severity": "CRITICAL",
    
    "description": """
    CSMS ile CP arasındaki OCPP iletişimine sızan saldırgan, mesajları 
    manipüle ederek CP'nin CAN-Bus'a yanlış komutlar göndermesine sebep olur.
    
    Örnek: RemoteStartTransaction → RemoteStopTransaction değiştirme
    Örnek: Authorize mesajında idTag manipülasyonu
    """,
    
    "threat_classification_stride": {
        "S_Spoofing": "Saldırgan kendini meşru CSMS olarak tanıtır",
        "T_Tampering": "OCPP mesaj içerikleri transit sırasında değiştirilir",
        "R_Repudiation": "Sahte idTag ile yetkilendirme, tespiti zor",
        "I_Information_Disclosure": "Oturum bilgileri ve idTag ifşa olur",
        "D_Denial_of_Service": "Sürekli manipüle komutlarla hizmet aksatılır",
        "E_Elevation_of_Privilege": "Yetkisiz aktör uzaktan kontrol kazanır"
    },
    
    "prerequisites": [
        "Güvensiz iletişim kanalı (Unsecured Transport veya zayıf TLS)",
        "CP'nin gelen OCPP mesajlarını doğrulamadan CAN'e map etmesi",
        "Yetersiz kayıt ve zaman senkronizasyonu (NTP eksikliği)",
        "Saldırganın ağ trafiğine erişimi (ARP spoofing, sahte AP, DNS poisoning)"
    ],
    
    "attack_steps": [
        "1. Erişim Sağlama: CSMS-CP arası ağ yoluna sızma (ARP spoofing, proxy)",
        "2. Trafiği Yakalama: WebSocket/HTTP trafiğini proxy ile yakalama",
        "3. Mesaj Manipülasyonu: RemoteStartTransaction → RemoteStopTransaction",
        "4. İletim: Manipüle edilmiş mesajı CP'ye iletme",
        "5. CAN Yayını: CP, yanlış CAN frame'i yayınlar (0x201 instead of 0x200)",
        "6. Sonuç: Şarj durur, sistem logları tutarsız kalır"
    ],
    
    "expected_detection": {
        "method": "Hybrid (Rule-based + Statistical)",
        
        "rule_based": {
            "K1_timing_mismatch": {
                "rule": "RemoteStart sonrası 2 saniye içinde RemoteStop",
                "severity": "HIGH",
                "description": "Zaman aşımı ve eylem uyuşmazlığı"
            },
            "K2_session_inconsistency": {
                "rule": "Aynı idTag için IP veya session fingerprint değişimi",
                "severity": "CRITICAL",
                "description": "Oturum ele geçirme girişimi"
            },
            "K3_ocpp_can_mismatch": {
                "rule": "OCPP eylemi ile CAN frame uyuşmazlığı",
                "severity": "CRITICAL",
                "description": "Start komutu geldi ama Stop CAN frame'i görüldü"
            }
        },
        
        "statistical": {
            "can_frequency_analysis": {
                "method": "Normal frekans aralığından sapma (µ ± 3σ)",
                "threshold": "CAN ID frekansı > µ + 3σ",
                "description": "Anormal Stop komutu frekansı"
            },
            "mapping_ratio": {
                "method": "OCPP-CAN eşleşme oranı izleme",
                "normal_baseline": "95%",
                "alert_threshold": "70%",
                "window": "5 dakika",
                "description": "Eşleşme oranında ani düşüş"
            },
            "tls_handshake_anomaly": {
                "method": "TLS handshake sıklığı analizi",
                "description": "Sürekli yeniden bağlanma, zayıf şifrelemeye zorlama"
            }
        },
        
        "ml_features": [
            "OCPP mesaj sırası anomalisi",
            "Zaman damgası sapmaları",
            "Payload entropy değişimi",
            "Session fingerprint churn rate",
            "Inter-message timing patterns"
        ]
    },
    
    "implementation": {
        "simulation": "attack_simulator.mitm_ocpp_manipulation()",
        "detection": "ids.check_ocpp_can_mismatch() + ml_ids.predict()",
        "logging": "blockchain.add_block(alert, 'ALERT')"
    },
    
    "success_criteria": [
        "IDS, OCPP-CAN uyuşmazlığını tespit etmeli (K3 kuralı)",
        "CRITICAL severity alert üretilmeli",
        "Blockchain'e ALERT bloğu eklenmeli",
        "Dashboard'da kırmızı alarm görünmeli",
        "SIEM korelasyon kuralı tetiklenmeli (K2 + K3 → CRITICAL)",
        "Manipüle edilmiş mesaj reddedilmeli (whitelist ile)"
    ],
    
    "impacts": {
        "functional": [
            "Şarj işlemlerinin beklenmedik şekilde durması",
            "Yetkisiz kişilerce şarj başlatılması",
            "Kullanıcı memnuniyetsizliği ve erişim hataları"
        ],
        "operational": [
            "Şarj istasyonu güvenilirliğinde azalma",
            "Sorun teşhis zorluğu",
            "Bakım maliyetlerinde artış"
        ],
        "economic": [
            "Hizmet kesintisinden gelir kaybı",
            "Güven kaybı nedeniyle dolaylı zararlar",
            "Yetkisiz şarj işlemlerinden mali kayıplar"
        ],
        "safety": [
            "Kritik filo operasyonlarında risk (ambulans, lojistik)",
            "Acil durum araçlarının şarjının kesilmesi",
            "Operasyonel güvenlik riskleri (TC-3, TC-5 etkileri)"
        ]
    },
    
    "mitigation_strategies": {
        "1_mutual_tls": {
            "priority": "CRITICAL",
            "description": "OCPP Security Profile 3: Zorunlu mTLS",
            "implementation": "CSMS ve CP'nin karşılıklı sertifika doğrulaması",
            "effectiveness": "MitM saldırılarını %95+ engeller"
        },
        "2_payload_signing": {
            "priority": "HIGH",
            "description": "OCPP JSON payload'larını HMAC/dijital imza ile imzalama",
            "implementation": "CP, mesajı işlemeden önce imzayı doğrular",
            "effectiveness": "Tampering'i %99+ önler"
        },
        "3_gateway_whitelist": {
            "priority": "HIGH",
            "description": "CP gateway'inde OCPP→CAN mapping whitelist",
            "implementation": "Bilinmeyen eşleşmeler reddedilir",
            "effectiveness": "CAN injection'ları %90+ engeller"
        },
        "4_siem_correlation": {
            "priority": "MEDIUM",
            "description": "K2 + K3 kurallarını birleştiren korelasyon",
            "implementation": "Çoklu anomali = CRITICAL alarm",
            "effectiveness": "False positive oranını düşürür"
        },
        "5_audit_logging": {
            "priority": "MEDIUM",
            "description": "Detaylı ve değiştirilemez audit log + NTP senkronizasyonu",
            "implementation": "Tüm OCPP ve CAN mesajları imzalı loglanır",
            "effectiveness": "Non-repudiation sağlar"
        },
        "6_rate_limiting": {
            "priority": "LOW",
            "description": "Anormal komut frekansında hız sınırlama",
            "implementation": "CP, çok fazla Stop komutu gelirse güvenli moda geçer",
            "effectiveness": "DoS saldırılarını azaltır"
        }
    },
    
    "test_configuration": {
        "csms_ip": "192.168.1.100",
        "cp_ip": "192.168.1.101",
        "attacker_ip": "192.168.1.50",
        "transport": "ws://",  # Unsecured
        "vcan_interface": "vcan0",
        "test_duration": "300s",
        "expected_alerts": [
            "OCPP_CAN_MISMATCH",
            "SESSION_FINGERPRINT_CHANGE",
            "TIMING_ANOMALY"
        ]
    },
    
    "references": {
        "ocpp_spec": "OCPP v2.0.1 - Part 2: Specification (Section 15.3 Security)",
        "stride_model": "Microsoft STRIDE Threat Modeling",
        "mitigation": "ISO 15118-20 (Vehicle-to-Grid Communication Security)",
        "related_cve": [
            "CVE-2021-31800 (EV Charging MitM)",
            "CVE-2020-8858 (OCPP Authentication Bypass)"
        ]
    },
    
    "severity_matrix": {
        "likelihood": "HIGH",  # Zayıf TLS konfigürasyonu yaygın
        "impact": "CRITICAL",  # Hizmet kesintisi + safety riski
        "overall_risk": "CRITICAL",
        "cvss_v3_score": 8.5,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:H"
    }
}


# Test fonksiyonu
def validate_scenario():
    """Senaryo formatını doğrula"""
    required_keys = [
        "id", "name", "category", "severity", "description",
        "attack_steps", "expected_detection", "success_criteria",
        "impacts", "mitigation_strategies"
    ]
    
    for key in required_keys:
        if key not in SCENARIO_01:
            print(f"❌ Eksik alan: {key}")
            return False
    
    print("✅ Senaryo #1 formatı geçerli")
    
    # Detayları yazdır
    print(f"\n📋 Senaryo: {SCENARIO_01['name']}")
    print(f"🔴 Severity: {SCENARIO_01['severity']}")
    print(f"📊 CVSS Score: {SCENARIO_01['severity_matrix']['cvss_v3_score']}")
    print(f"\n🎯 Tespit Kuralları:")
    for rule_name, rule_data in SCENARIO_01['expected_detection']['rule_based'].items():
        print(f"  - {rule_name}: {rule_data['description']} ({rule_data['severity']})")
    
    print(f"\n🛡️ Azaltma Stratejileri:")
    for strat_name, strat_data in SCENARIO_01['mitigation_strategies'].items():
        print(f"  - {strat_data['description']} (Priority: {strat_data['priority']})")
    
    return True


if __name__ == "__main__":
    print("="*60)
    print("ANOMALİ SENARYOSU #1: MitM OCPP Manipulation")
    print("="*60)
    validate_scenario()

