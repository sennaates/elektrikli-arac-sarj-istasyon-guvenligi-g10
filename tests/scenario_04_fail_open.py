"""
SENARYO #4: FAIL-OPEN DAVRANIŞI - AUTH SERVİS KAPALI

Tehdit Sınıflandırması:
- Saldırı Tipi: Denial of Service (DoS) + Authentication Bypass
- Hedeflenen Varlık: Auth Servis (CSMS) / Kimlik Doğrulama Akışı
- Etkilenen Özellik: Kimlik Doğrulama (Authentication) + Güvenlik Politikası
- Kategori: Güvenlik Politikası İhlali + Yetkisiz Erişim

STRIDE Modeli Analizi:
- Denial of Service (D): Auth Servis DoS saldırısı ile devre dışı bırakılır
- Elevation of Privilege (E): Yetkisiz kullanıcılar şarj işlemi başlatabilir
- Repudiation (R): Fail-open durumunda log kaydı eksik olabilir
- Tampering (T): Güvenlik politikası ihlal edilir (fail-closed yerine fail-open)
"""

import time
from typing import Dict, List, Optional

# SENARYO PARAMETRELERİ
SCENARIO_CONFIG = {
    "id": "SCENARIO-04",
    "name": "Fail-Open Davranışı - Auth Servis Kapalı",
    "severity": "CRITICAL",
    "category": "Authentication Bypass / Security Policy Violation",
    
    # Normal Davranış
    "normal_behavior": {
        "auth_service_available": True,
        "auth_response_time": 0.5,  # saniye (normal yanıt süresi)
        "fail_closed_policy": True,  # Auth başarısız olursa şarj başlamaz
        "auth_required": True,  # Her şarj için kimlik doğrulama gerekli
        "offline_cache_enabled": False,  # Offline cache kapalı
        "whitelist_enabled": False  # Whitelist kapalı
    },
    
    # Anomali Davranış (Fail-Open)
    "anomaly_behavior": {
        "auth_service_available": False,  # Auth Servis erişilemez
        "auth_response_time": None,  # Yanıt yok
        "fail_closed_policy": False,  # Fail-closed yerine fail-open
        "auth_required": False,  # Kimlik doğrulama atlanır
        "offline_cache_enabled": False,  # Cache yok ama yine de şarj başlar
        "whitelist_enabled": False,  # Whitelist yok
        "charge_started_without_auth": True  # Auth olmadan şarj başladı
    },
    
    # Saldırı Parametreleri
    "attack": {
        "type": "DoS + Authentication Bypass",
        "target": "Auth Servis (CSMS)",
        "method": "DoS saldırısı ile Auth Servis'i devre dışı bırak, fail-open davranışını tetikle",
        "steps": [
            "1. Auth Servis'e DoS saldırısı başlat (yüksek trafik, resource exhaustion)",
            "2. Auth Servis erişilemez hale gelir",
            "3. EVSE, Auth Servis'e istek gönderir ama yanıt alamaz",
            "4. Sistem fail-open davranışı gösterir (şarj başlar)",
            "5. Yetkisiz kullanıcı şarj işlemini başlatır",
            "6. Gelir kaybı ve güvenlik ihlali oluşur"
        ],
        "duration": 300.0,  # saniye (5 dakika DoS saldırısı)
        "detection_window": 60.0  # saniye (1 dakika içinde tespit edilmeli)
    },
    
    # Tespit Kuralları
    "detection": {
        # Kural-1: Auth Servis Erişilemezlik Tespiti
        "rule_1": {
            "id": "AUTH_SERVICE_UNAVAILABLE",
            "name": "Auth Servis Erişilemez",
            "condition": "auth_response_timeout_count >= 3 in 60 seconds",
            "threshold": 3,  # 3 başarısız deneme
            "severity": "HIGH",
            "window": 60.0  # saniye
        },
        
        # Kural-2: Fail-Open Davranış Tespiti
        "rule_2": {
            "id": "FAIL_OPEN_BEHAVIOR",
            "name": "Fail-Open Davranış Tespiti",
            "condition": "charge_started_without_auth == True AND auth_service_unavailable == True",
            "threshold": 1,  # Tek bir olay bile kritik
            "severity": "CRITICAL",
            "window": 10.0  # saniye (çok hızlı tespit gerekli)
        },
        
        # Kural-3: Auth Timeout Pattern
        "rule_3": {
            "id": "AUTH_TIMEOUT_PATTERN",
            "name": "Auth Timeout Pattern",
            "condition": "consecutive_auth_timeouts >= 5",
            "threshold": 5,  # 5 ardışık timeout
            "severity": "HIGH",
            "window": 30.0  # saniye
        },
        
        # Kural-4: Unauthorized Charge Start
        "rule_4": {
            "id": "UNAUTHORIZED_CHARGE_START",
            "name": "Yetkisiz Şarj Başlatma",
            "condition": "charge_started == True AND auth_status == 'FAILED'",
            "threshold": 1,
            "severity": "CRITICAL",
            "window": 5.0  # saniye
        },
        
        # ML-based detection features
        "ml_features": [
            "auth_response_time",  # Yanıt süresi (None ise timeout)
            "auth_success_rate",  # Başarı oranı (0-1)
            "consecutive_timeouts",  # Ardışık timeout sayısı
            "charge_without_auth",  # Auth olmadan şarj başlatma (0/1)
            "time_since_last_auth",  # Son başarılı auth'tan geçen süre
            "auth_request_frequency"  # Auth istek frekansı
        ]
    },
    
    # Test Senaryoları
    "test_cases": [
        {
            "id": "TC-04-001",
            "name": "Auth Servis DoS Saldırısı",
            "description": "Auth Servis'e DoS saldırısı yap, fail-open davranışını tetikle",
            "expected_alert": "FAIL_OPEN_BEHAVIOR",
            "expected_severity": "CRITICAL"
        },
        {
            "id": "TC-04-002",
            "name": "Auth Timeout Pattern",
            "description": "Ardışık auth timeout'ları oluştur",
            "expected_alert": "AUTH_TIMEOUT_PATTERN",
            "expected_severity": "HIGH"
        },
        {
            "id": "TC-04-003",
            "name": "Yetkisiz Şarj Başlatma",
            "description": "Auth başarısız olmasına rağmen şarj başlat",
            "expected_alert": "UNAUTHORIZED_CHARGE_START",
            "expected_severity": "CRITICAL"
        }
    ],
    
    # Etkiler
    "impacts": {
        "functional": "Sistem güvenlik politikasını ihlal eder, yetkisiz kullanıcılar şarj yapabilir",
        "operational": "Sunucu arızasında sistem güvenli modda kalamaz",
        "financial": "Ücretsiz şarj işlemleri nedeniyle doğrudan gelir kaybı",
        "safety": "Kimlik doğrulama atlanır, yetkisiz kullanım olur",
        "reputation": "Sistemin kötüye kullanılması güven kaybına neden olur"
    },
    
    # CWE/OWASP Sınıflandırması
    "vulnerability_classification": {
        "CWE": ["CWE-703", "CWE-287"],
        "CWE-703": "Improper Handling of Exceptional Conditions",
        "CWE-287": "Improper Authentication",
        "OWASP": "A07-2021: Identification and Authentication Failures"
    },
    
    # Risk Değerlendirmesi
    "risk_assessment": {
        "likelihood": "HIGH",
        "impact": "CRITICAL",
        "risk_score": 9.2,  # /10
        "risk_level": "CRITICAL"
    },
    
    # Önerilen Düzeltmeler
    "recommended_fixes": [
        "1. Sistem mantığı fail-closed davranışına geçmelidir",
        "2. Sadece belirli kullanıcılar için offline cache veya whitelist uygulanmalıdır",
        "3. DoS dayanıklılığı load balancer ve rate limitlerle güçlendirilmelidir",
        "4. Fail-open durumları için loglama ve alarm mekanizması eklenmelidir"
    ]
}


def validate_scenario() -> bool:
    """Senaryo yapılandırmasını doğrula"""
    required_keys = ["id", "name", "severity", "category", "attack", "detection"]
    for key in required_keys:
        if key not in SCENARIO_CONFIG:
            print(f"❌ Eksik anahtar: {key}")
            return False
    
    print(f"✅ Senaryo #4 doğrulandı: {SCENARIO_CONFIG['name']}")
    print(f"   Severity: {SCENARIO_CONFIG['severity']}")
    print(f"   Risk Score: {SCENARIO_CONFIG['risk_assessment']['risk_score']}/10")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("SENARYO #4: FAIL-OPEN DAVRANIŞI - AUTH SERVİS KAPALI")
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
        
        print("\n✅ Senaryo yapılandırması geçerli!")

