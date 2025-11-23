"""
Anomali Senaryoları Template
Kendi senaryolarınızı bu formatta ekleyebilirsiniz.
"""

# Senaryolarınızı buraya ekleyin
ANOMALY_SCENARIOS = [
    {
        "id": 1,
        "name": "Replay Attack - OCPP Seviyesi",
        "category": "Replay",
        "severity": "HIGH",
        "description": "Daha önce gönderilmiş bir OCPP mesajını aynı timestamp ile tekrar göndererek sistemi yanıltma",
        "attack_steps": [
            "1. Normal bir RemoteStartTransaction mesajını yakala",
            "2. 5 saniye bekle",
            "3. Aynı mesajı tekrar gönder (timestamp değiştirmeden)",
        ],
        "expected_detection": {
            "method": "Rule-based IDS",
            "rule": "OCPP_TIMESTAMP_ANOMALY",
            "alert_severity": "MEDIUM"
        },
        "implementation": "attack_simulator.replay_attack()",
        "success_criteria": [
            "IDS alert üretmeli",
            "Blockchain'e alert kaydedilmeli",
            "Dashboard'da kırmızı uyarı görünmeli"
        ]
    },
    
    {
        "id": 2,
        "name": "CAN Flood Attack",
        "category": "DoS",
        "severity": "CRITICAL",
        "description": "1 saniyede 200+ CAN frame göndererek bus'ı doyurma (Denial of Service)",
        "attack_steps": [
            "1. CAN ID 0x201 seç",
            "2. 2 saniye boyunca saniyede 200 frame gönder",
            "3. Her frame rastgele payload içersin"
        ],
        "expected_detection": {
            "method": "Rule-based IDS",
            "rule": "CAN_FLOOD_ATTACK",
            "alert_severity": "CRITICAL"
        },
        "implementation": "attack_simulator.can_flood(duration=2.0, rate=200)",
        "success_criteria": [
            "100. frame'de IDS tetiklenmeli",
            "CRITICAL severity alert üretilmeli",
            "Dashboard'da flood grafiği spike göstermeli"
        ]
    },
    
    {
        "id": 3,
        "name": "Unauthorized CAN Injection",
        "category": "Injection",
        "severity": "HIGH",
        "description": "Bridge tarafından gönderilmemiş (yetkisiz) CAN frame enjeksiyonu",
        "attack_steps": [
            "1. CAN ID 0x200 seç (normalde RemoteStartTransaction için)",
            "2. Bridge'e OCPP komutu GÖNDERMEDEN direkt CAN frame gönder",
            "3. Payload: [0xFF, 0xFF, 0xFF, 0xFF, 0xDE, 0xAD, 0xBE, 0xEF]"
        ],
        "expected_detection": {
            "method": "Rule-based IDS",
            "rule": "UNAUTHORIZED_CAN_INJECTION",
            "alert_severity": "HIGH"
        },
        "implementation": "attack_simulator.unauthorized_injection()",
        "success_criteria": [
            "IDS frame'i unauthorized olarak işaretlemeli",
            "Blockchain'e ALERT bloğu eklenmeli",
            "Dashboard'da 'Unauthorized Injection' alert'i görünmeli"
        ]
    },
    
    {
        "id": 4,
        "name": "Invalid CAN ID Attack",
        "category": "Injection",
        "severity": "MEDIUM",
        "description": "Whitelist'te olmayan CAN ID ile frame gönderme",
        "attack_steps": [
            "1. İzin listesinde OLMAYAN bir ID seç (örn. 0x9FF)",
            "2. 10 adet frame gönder",
            "3. Payload rastgele"
        ],
        "expected_detection": {
            "method": "Rule-based IDS",
            "rule": "INVALID_CAN_ID",
            "alert_severity": "MEDIUM"
        },
        "implementation": "attack_simulator.invalid_can_id(invalid_id=0x9FF)",
        "success_criteria": [
            "Her frame için INVALID_CAN_ID alert'i",
            "Dashboard'da geçersiz ID listede görünmeli"
        ]
    },
    
    {
        "id": 5,
        "name": "High Entropy Payload Attack",
        "category": "ML Anomaly",
        "severity": "MEDIUM",
        "description": "Tamamen rastgele (yüksek entropy) payload ile normal bir CAN ID'ye frame gönderme. ML-IDS tespit etmeli.",
        "attack_steps": [
            "1. Normal bir CAN ID seç (0x200)",
            "2. Her byte tamamen rastgele (0-255)",
            "3. 15 frame gönder"
        ],
        "expected_detection": {
            "method": "ML-based IDS",
            "rule": "ML_ANOMALY_DETECTED",
            "alert_severity": "MEDIUM"
        },
        "implementation": "attack_simulator.high_entropy_attack()",
        "success_criteria": [
            "ML-IDS anomaly score > threshold",
            "Dashboard'da ML detection göstergesi",
            "Entropy feature'ı yüksek değer göstermeli"
        ]
    },
    
    # SENİN 10 SENARYONDAN İLK 5'İNİ EKLE
    # Kalan 5'i için template:
    
    {
        "id": 6,
        "name": "[Senaryo 6 Adı]",
        "category": "[Replay / DoS / Injection / Spoofing / ML]",
        "severity": "[LOW / MEDIUM / HIGH / CRITICAL]",
        "description": "[Saldırının detaylı açıklaması]",
        "attack_steps": [
            "Adım 1",
            "Adım 2",
            "Adım 3"
        ],
        "expected_detection": {
            "method": "[Rule-based / ML-based / Hybrid]",
            "rule": "[KURAL_ADI]",
            "alert_severity": "[SEVERITY]"
        },
        "implementation": "[Fonksiyon çağrısı]",
        "success_criteria": [
            "Kriter 1",
            "Kriter 2"
        ]
    },
    
    # 7-10 için devamını ekle...
]


# Senaryo validator
def validate_scenario(scenario: dict) -> bool:
    """Senaryo formatını doğrula"""
    required_keys = ["id", "name", "category", "severity", "description", 
                    "attack_steps", "expected_detection", "success_criteria"]
    
    for key in required_keys:
        if key not in scenario:
            print(f"❌ Eksik alan: {key}")
            return False
    
    return True


# Test
if __name__ == "__main__":
    print("="*60)
    print("ANOMALİ SENARYOLARI VALİDASYONU")
    print("="*60)
    
    for scenario in ANOMALY_SCENARIOS:
        print(f"\n[{scenario['id']}] {scenario['name']}")
        
        if validate_scenario(scenario):
            print(f"  ✅ Geçerli")
            print(f"  Kategori: {scenario['category']}")
            print(f"  Severity: {scenario['severity']}")
        else:
            print(f"  ❌ Geçersiz format!")
    
    print(f"\nToplam {len(ANOMALY_SCENARIOS)} senaryo tanımlandı.")

