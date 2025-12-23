"""
Senaryo #4: Fail-Open Davranışı Test Scripti
Auth servis kapalıyken şarj başlatma simülasyonu
"""
import time
import requests
from utils.ids import RuleBasedIDS

def test_fail_open_scenario():
    """Fail-Open davranışını simüle et"""
    print("=" * 60)
    print("SENARYO #4: FAIL-OPEN DAVRANIŞI TESTİ")
    print("=" * 60)
    
    # IDS oluştur
    ids = RuleBasedIDS()
    print("✅ IDS başlatıldı\n")
    
    current_time = time.time()
    
    # Adım 1: Auth Servis'e DoS saldırısı simülasyonu
    print("📡 [1/4] Auth Servis'e DoS saldırısı başlatılıyor...")
    print("   → Auth servis erişilemez hale geliyor\n")
    
    # 5 ardışık auth timeout oluştur
    for i in range(5):
        alert = ids.check_auth_failure("TIMEOUT", current_time + i)
        if alert:
            print(f"   ⚠️  Alert: {alert.alert_type} ({alert.severity})")
        time.sleep(0.5)
    
    print("\n📊 [2/4] Auth timeout pattern tespit edildi")
    print("   → Ardışık timeout sayısı:", ids.stats.consecutive_auth_timeouts)
    
    # Adım 3: Fail-Open davranışı - Auth olmadan şarj başlatma
    print("\n🚨 [3/4] FAIL-OPEN DAVRANIŞI TETİKLENİYOR...")
    print("   → Auth durumu: TIMEOUT")
    print("   → Şarj başlatılıyor (Fail-Open davranışı)\n")
    
    # Auth başarısız ama şarj başlatılıyor
    alert = ids.check_charge_without_auth(
        charge_started=True,
        auth_status="TIMEOUT",
        timestamp=current_time + 10
    )
    
    if alert:
        print(f"   🚨 CRITICAL ALERT: {alert.alert_type}")
        print(f"   📝 Açıklama: {alert.description}")
        print(f"   ⚠️  Severity: {alert.severity}\n")
    else:
        print("   ⚠️  Alert oluşmadı (Fail-Open davranışı tespit edilemedi!)\n")
    
    # Adım 4: API'ye alert gönder
    print("📤 [4/4] Alert'ler API'ye gönderiliyor...")
    
    alerts = ids.get_recent_alerts(10)
    api_url = "http://localhost:8000/api/alerts"
    
    for alert in alerts:
        try:
            alert_dict = alert.to_dict()
            response = requests.post(api_url, json=alert_dict, timeout=2)
            if response.status_code == 200:
                print(f"   ✅ Alert gönderildi: {alert.alert_type}")
            else:
                print(f"   ⚠️  Alert gönderilemedi: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Hata: {str(e)[:50]}")
    
    # İstatistikler
    print("\n" + "=" * 60)
    print("📊 İSTATİSTİKLER")
    print("=" * 60)
    stats = ids.get_stats()
    print(f"   Toplam Alert: {stats['total_alerts']}")
    print(f"   Auth Başarısızlık: {stats['auth_failure_count']}")
    print(f"   Ardışık Timeout: {stats['consecutive_auth_timeouts']}")
    print(f"   Auth Olmadan Şarj: {stats['charge_starts_without_auth']}")
    
    alert_breakdown = stats.get('alert_breakdown', {})
    print(f"\n   Alert Dağılımı:")
    for severity, count in alert_breakdown.items():
        if count > 0:
            print(f"      {severity}: {count}")
    
    print("\n" + "=" * 60)
    print("✅ Senaryo #4 testi tamamlandı!")
    print("=" * 60)
    print("\n📋 Dashboard'da kontrol edin:")
    print("   → http://localhost:8501")
    print("   → Alert sayısı artmalı")
    print("   → FAIL_OPEN_BEHAVIOR alert'i görünmeli")
    print("   → CRITICAL severity alert'leri görünmeli\n")

if __name__ == "__main__":
    test_fail_open_scenario()

