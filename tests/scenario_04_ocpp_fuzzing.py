"""
SENARYO #04: FUZZING İLE OCPP PROTOKOL ZAFİYET TESPİTİ

Tehdit Sınıflandırması:
- Saldırı Tipi: Fuzzing / Protocol Anomaly
- Hedeflenen Varlık: CSMS (Central System)
- Etkilenen Özellik: Sağlamlık (Robustness), Kullanılabilirlik (Availability)
- Kategori: Protokol Manipülasyonu

Açıklama:
Bu senaryo, OCPP mesajlarına kasıtlı olarak bozulmuş, beklenmedik tipte veya
aşırı uzunlukta veriler (payload) göndererek (Fuzzing), hedef sistemin (CSMS)
hatalı durum yönetimini, çökme (crash) veya kaynak tüketimi (resource exhaustion)
gibi zafiyetlerini tespit etmeyi amaçlar.
"""

SCENARIO_CONFIG = {
    "id": "SCENARIO-04",
    "name": "OCPP Protocol Fuzzing",
    "severity": "HIGH",
    "category": "Protocol Manipulation",
    
    # Normal Davranış: Standart JSON formatında, doğru tiplerde veriler
    "normal_behavior": {
        "message_format": "Valid JSON",
        "data_types": "Correct (String, Integer, etc.)",
        "payload_size": "Standard (< 1KB)",
        "message_sequence": "Ordered (Boot -> Start -> Stop)"
    },
    
    # Anomali Davranış: Bozuk format, yanlış tipler, aşırı yük
    "anomaly_behavior": {
        "message_format": "Malformed JSON / XML / Binary",
        "data_types": "Mismatch (String instead of Int)",
        "payload_size": "Excessive (> 1MB - Buffer Overflow attempt)",
        "message_sequence": "Disordered / Invalid Commands"
    },
    
    # Saldırı Parametreleri
    "attack": {
        "type": "Fuzzing",
        "target": "CSMS Application Layer",
        "method": "Mutation-based Fuzzing (Type, Length, Format)",
    },
    
    # Tespit Kuralları
    "detection": {
        "rule_1": {
            "id": "RULE-04-01",
            "name": "F1 - Hedef Çökmesi (Crash)",
            "condition": "Unhandled Exception logs or Connection Drop after malformed payload",
            "severity": "CRITICAL",
            "threshold": "1 occurrence"
        },
        "rule_2": {
            "id": "RULE-04-02",
            "name": "F2 - Yanıt Vermeme (Hang/DoS)",
            "condition": "No response for > 10s",
            "severity": "HIGH",
            "threshold": "10 seconds timeout"
        },
        "rule_3": {
            "id": "RULE-04-03",
            "name": "F3 - Kaynak Tüketimi",
            "condition": "CPU/RAM spike > 95%",
            "severity": "MEDIUM",
            "threshold": "95% Usage"
        }
    },
    
    # Test Senaryoları
    "test_cases": [
        {
            "id": "TC-04-001",
            "name": "Type Mutation Fuzzing",
            "description": "Sending String to Integer field (e.g. connectorId)",
            "expected_alert": "OCPP_PROTOCOL_ERROR"
        },
        {
            "id": "TC-04-002",
            "name": "Length Mutation Fuzzing",
            "description": "Sending 1MB payload to vendorId field",
            "expected_alert": "PAYLOAD_SIZE_ANOMALY"
        },
        {
            "id": "TC-04-003",
            "name": "Format Mutation Fuzzing",
            "description": "Sending Malformed JSON",
            "expected_alert": "JSON_PARSE_ERROR"
        }
    ],
    
    # Etkiler
    "impacts": {
        "functional": "Sistem çökmesi veya hatalı işlem yürütme",
        "operational": "Şarj hizmetinin kesintiye uğraması (DoS)",
        "financial": "Faturalandırma hataları veya hizmet kaybı",
        "safety": "Beklenmedik donanım durumu (nadir)"
    }
}

if __name__ == "__main__":
    print(f"Senaryo #04: {SCENARIO_CONFIG['name']}")
    print(f"Severity: {SCENARIO_CONFIG['severity']}")