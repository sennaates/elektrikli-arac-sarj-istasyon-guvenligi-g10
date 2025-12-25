"""
SENARYO #5: SAHTE REZERVASYON (A4: Duplicate Booking) KULLANARAK YETKİSİZ ŞARJ ERİŞİMİ

Tehdit Sınıflandırması:
- Saldırı Tipi: Insecure Direct Object References (OWASP A4)
- Hedeflenen Varlık: OCPP ReserveNow Mekanizması
- Etkilenen Özellik: Rezervasyon Yönetimi + Yetkilendirme
- Kategori: Authorization Bypass / Access Control Violation

STRIDE Modeli Analizi:
- Spoofing (S): Saldırgan kendini meşru kullanıcı olarak tanıtır
- Tampering (T): Rezervasyon verileri manipüle edilir
- Repudiation (R): Çift rezervasyon nedeniyle log tutarsızlığı
- Information Disclosure (I): Rezervasyon ID'leri ve connector bilgileri ifşa olur
- Denial of Service (D): Aynı connector için çoklu rezervasyon
- Elevation of Privilege (E): Yetkisiz kullanıcı şarj erişimi kazanır
"""

import time
from typing import Dict, List, Optional

# SENARYO PARAMETRELERİ
SCENARIO_CONFIG = {
    "id": "SCENARIO-05",
    "name": "Sahte Rezervasyon (A4: Duplicate Booking) Kullanarak Yetkisiz Şarj Erişimi",
    "severity": "CRITICAL",
    "category": "Authorization Bypass / Access Control Violation",
    
    # Normal Davranış
    "normal_behavior": {
        "reservation_unique": True,  # Her rezervasyon benzersiz ID'ye sahip
        "connector_single_reservation": True,  # Bir connector'a aynı anda tek rezervasyon
        "reservation_validation": True,  # Rezervasyon ID doğrulaması yapılır
        "id_tag_verification": True,  # idTag doğrulaması yapılır
        "expiry_time_check": True,  # Rezervasyon süresi kontrol edilir
        "connector_availability_check": True  # Connector müsaitlik kontrolü
    },
    
    # Anomali Davranış (Duplicate Booking)
    "anomaly_behavior": {
        "reservation_unique": False,  # Aynı rezervasyon ID birden fazla kez kullanılır
        "connector_single_reservation": False,  # Aynı connector'a çoklu rezervasyon
        "reservation_validation": False,  # Rezervasyon ID doğrulaması atlanır
        "id_tag_verification": False,  # idTag doğrulaması atlanır
        "expiry_time_check": False,  # Süre kontrolü atlanır
        "connector_availability_check": False,  # Müsaitlik kontrolü atlanır
        "duplicate_reservation_created": True,  # Çift rezervasyon oluşturuldu
        "unauthorized_charge_access": True  # Yetkisiz şarj erişimi sağlandı
    },
    
    # Saldırı Parametreleri
    "attack": {
        "type": "Duplicate Booking / Reservation Manipulation",
        "target": "OCPP ReserveNow Mechanism",
        "method": "Aynı rezervasyon ID'si veya connector ile çoklu rezervasyon oluşturma",
        "steps": [
            "1. Meşru bir ReserveNow isteği yakala (reservationId, connectorId, idTag)",
            "2. Aynı reservationId ile ikinci bir ReserveNow isteği gönder",
            "3. Veya aynı connectorId ile farklı idTag ile rezervasyon oluştur",
            "4. Rezervasyon doğrulaması atlanır, çift rezervasyon kabul edilir",
            "5. Yetkisiz kullanıcı şarj işlemini başlatır",
            "6. Gelir kaybı ve güvenlik ihlali oluşur"
        ],
        "duration": 300.0,  # saniye (5 dakika saldırı)
        "detection_window": 10.0  # saniye (10 saniye içinde tespit edilmeli)
    },
    
    # Tespit Kuralları
    "detection": {
        # Kural-1: Duplicate Reservation ID Tespiti
        "rule_1": {
            "id": "DUPLICATE_RESERVATION_ID",
            "name": "Çift Rezervasyon ID Tespiti",
            "condition": "Aynı reservationId ile birden fazla ReserveNow isteği",
            "threshold": 1,  # Tek bir çift bile kritik
            "severity": "CRITICAL",
            "window": 60.0  # saniye (1 dakika içinde)
        },
        
        # Kural-2: Multiple Reservations for Same Connector
        "rule_2": {
            "id": "MULTIPLE_CONNECTOR_RESERVATIONS",
            "name": "Aynı Connector İçin Çoklu Rezervasyon",
            "condition": "Aynı connectorId için aktif rezervasyon sayısı > 1",
            "threshold": 1,  # 1'den fazla aktif rezervasyon
            "severity": "CRITICAL",
            "window": 5.0  # saniye (çok hızlı tespit)
        },
        
        # Kural-3: Reservation ID Reuse Pattern
        "rule_3": {
            "id": "RESERVATION_ID_REUSE",
            "name": "Rezervasyon ID Tekrar Kullanımı",
            "condition": "Daha önce kullanılmış reservationId tekrar kullanıldı",
            "threshold": 1,
            "severity": "HIGH",
            "window": 300.0  # saniye (5 dakika)
        },
        
        # Kural-4: Unauthorized Reservation Access
        "rule_4": {
            "id": "UNAUTHORIZED_RESERVATION_ACCESS",
            "name": "Yetkisiz Rezervasyon Erişimi",
            "condition": "Rezervasyon olmadan veya geçersiz idTag ile şarj başlatma",
            "threshold": 1,
            "severity": "CRITICAL",
            "window": 10.0  # saniye
        },
        
        # Kural-5: Reservation-Transaction Mismatch
        "rule_5": {
            "id": "RESERVATION_TRANSACTION_MISMATCH",
            "name": "Rezervasyon-İşlem Uyuşmazlığı",
            "condition": "StartTransaction'da kullanılan idTag, rezervasyondaki idTag ile eşleşmiyor",
            "threshold": 1,
            "severity": "CRITICAL",
            "window": 30.0  # saniye
        },
        
        # ML-based detection features
        "ml_features": [
            "reservation_id_frequency",  # Rezervasyon ID kullanım sıklığı
            "connector_reservation_count",  # Connector başına rezervasyon sayısı
            "id_tag_reservation_ratio",  # idTag başına rezervasyon oranı
            "reservation_expiry_pattern",  # Rezervasyon süresi pattern'i
            "reservation_to_transaction_time",  # Rezervasyon-şarj başlatma süresi
            "duplicate_reservation_rate"  # Çift rezervasyon oranı
        ]
    },
    
    # Test Senaryoları
    "test_cases": [
        {
            "id": "TC-05-001",
            "name": "Duplicate Reservation ID Attack",
            "description": "Aynı reservationId ile iki ReserveNow isteği gönder",
            "expected_alert": "DUPLICATE_RESERVATION_ID",
            "expected_severity": "CRITICAL"
        },
        {
            "id": "TC-05-002",
            "name": "Multiple Connector Reservations",
            "description": "Aynı connectorId için birden fazla aktif rezervasyon oluştur",
            "expected_alert": "MULTIPLE_CONNECTOR_RESERVATIONS",
            "expected_severity": "CRITICAL"
        },
        {
            "id": "TC-05-003",
            "name": "Reservation ID Reuse",
            "description": "Daha önce kullanılmış bir reservationId'yi tekrar kullan",
            "expected_alert": "RESERVATION_ID_REUSE",
            "expected_severity": "HIGH"
        },
        {
            "id": "TC-05-004",
            "name": "Unauthorized Charge Start",
            "description": "Geçersiz rezervasyon ile şarj başlat",
            "expected_alert": "UNAUTHORIZED_RESERVATION_ACCESS",
            "expected_severity": "CRITICAL"
        },
        {
            "id": "TC-05-005",
            "name": "Reservation-Transaction Mismatch",
            "description": "Rezervasyondaki idTag ile farklı idTag ile şarj başlat",
            "expected_alert": "RESERVATION_TRANSACTION_MISMATCH",
            "expected_severity": "CRITICAL"
        }
    ],
    
    # Etkiler
    "impacts": {
        "functional": "Sistem rezervasyon mekanizmasını bypass eder, yetkisiz kullanıcılar şarj yapabilir",
        "operational": "Rezervasyon yönetimi bozulur, connector çakışmaları oluşur",
        "financial": "Ücretsiz şarj işlemleri nedeniyle doğrudan gelir kaybı",
        "safety": "Yetkisiz erişim, güvenlik politikası ihlali",
        "reputation": "Sistemin kötüye kullanılması güven kaybına neden olur",
        "user_experience": "Meşru kullanıcılar rezervasyon yapamaz, hizmet kalitesi düşer"
    },
    
    # CWE/OWASP Sınıflandırması
    "vulnerability_classification": {
        "CWE": ["CWE-639", "CWE-284", "CWE-285"],
        "CWE-639": "Authorization Bypass Through User-Controlled Key",
        "CWE-284": "Improper Access Control",
        "CWE-285": "Improper Authorization",
        "OWASP": "A01:2021 - Broken Access Control (A4: Insecure Direct Object References)"
    },
    
    # Risk Değerlendirmesi
    "risk_assessment": {
        "likelihood": "MEDIUM",
        "impact": "CRITICAL",
        "risk_score": 8.5,  # /10
        "risk_level": "CRITICAL"
    },
    
    # Önerilen Düzeltmeler
    "recommended_fixes": [
        "1. Rezervasyon ID'lerinin benzersizliğini garanti et (UUID kullan)",
        "2. Aynı connector için aynı anda tek rezervasyon politikası uygula",
        "3. Rezervasyon ID doğrulaması yap (daha önce kullanılmış mı kontrol et)",
        "4. StartTransaction'da rezervasyon-idTag eşleşmesini zorunlu kıl",
        "5. Rezervasyon süresi ve expiry kontrolü yap",
        "6. Connector müsaitlik kontrolü yap (zaten rezerve edilmiş mi?)",
        "7. Rezervasyon loglarını blockchain'e kaydet (non-repudiation)",
        "8. Rate limiting: Aynı idTag için çok fazla rezervasyon isteğini engelle"
    ]
}


def validate_scenario() -> bool:
    """Senaryo yapılandırmasını doğrula"""
    required_keys = ["id", "name", "severity", "category", "attack", "detection"]
    for key in required_keys:
        if key not in SCENARIO_CONFIG:
            print(f"❌ Eksik anahtar: {key}")
            return False
    
    print(f"✅ Senaryo #5 doğrulandı: {SCENARIO_CONFIG['name']}")
    print(f"   Severity: {SCENARIO_CONFIG['severity']}")
    print(f"   Risk Score: {SCENARIO_CONFIG['risk_assessment']['risk_score']}/10")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("SENARYO #5: SAHTE REZERVASYON (A4: Duplicate Booking)")
    print("=" * 60)
    
    if validate_scenario():
        print("\n📋 Senaryo Detayları:")
        print(f"   ID: {SCENARIO_CONFIG['id']}")
        print(f"   İsim: {SCENARIO_CONFIG['name']}")
        print(f"   Kategori: {SCENARIO_CONFIG['category']}")
        print(f"   Severity: {SCENARIO_CONFIG['severity']}")
        
        print("\n🎯 Saldırı Tipi:")
        print(f"   {SCENARIO_CONFIG['attack']['type']}")
        print(f"   Hedef: {SCENARIO_CONFIG['attack']['target']}")
        
        print("\n🔍 Tespit Kuralları:")
        for rule_id, rule in SCENARIO_CONFIG['detection'].items():
            if isinstance(rule, dict) and 'id' in rule:
                print(f"   - {rule['id']}: {rule.get('name', 'N/A')} (Severity: {rule.get('severity', 'N/A')})")
        
        print("\n📊 Risk Değerlendirmesi:")
        risk = SCENARIO_CONFIG['risk_assessment']
        print(f"   Olasılık: {risk['likelihood']}")
        print(f"   Etki: {risk['impact']}")
        print(f"   Risk Skoru: {risk['risk_score']}/10 - {risk['risk_level']}")
        
        print("\n🛡️ Önerilen Düzeltmeler:")
        for i, fix in enumerate(SCENARIO_CONFIG['recommended_fixes'], 1):
            print(f"   {i}. {fix}")
        
        print("\n✅ Senaryo yapılandırması geçerli!")

