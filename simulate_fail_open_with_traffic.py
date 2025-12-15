"""
Senaryo #4: Fail-Open Davranışı - Trafik Simülasyonu ile
Auth servis kapalıyken şarj başlatma + CAN/OCPP trafiği
"""
import time
import requests
import asyncio
import websockets
import json
from utils.ids import RuleBasedIDS
from utils.can_handler import CANBusHandler

def simulate_charging_traffic(ids, duration=10):
    """Şarj sırasında normal trafik simülasyonu"""
    print("\n📡 Şarj trafiği simüle ediliyor...")
    
    # OCPP mesajları
    ocpp_messages = [
        ("StartTransaction", {"connectorId": 1, "idTag": "UNAUTHORIZED", "meterStart": 0}),
        ("MeterValues", {"connectorId": 1, "meterValue": [{"timestamp": time.time(), "sampledValue": [{"value": "5.5", "context": "Sample.Periodic"}]}]}),
        ("MeterValues", {"connectorId": 1, "meterValue": [{"timestamp": time.time(), "sampledValue": [{"value": "10.2", "context": "Sample.Periodic"}]}]}),
    ]
    
    # CAN frame'leri
    can_frames = [
        (0x200, [0x01, 0x01, 0xAB, 0xCD, 0x00, 0x00, 0x00, 0x00]),  # Start
        (0x201, [0x05, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),  # Power
        (0x202, [0x0A, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),  # More power
    ]
    
    start_time = time.time()
    message_count = 0
    
    while time.time() - start_time < duration:
        # OCPP mesajı gönder
        if message_count < len(ocpp_messages):
            action, payload = ocpp_messages[message_count % len(ocpp_messages)]
            alert = ids.check_ocpp_message(action, payload, time.time())
            if alert:
                print(f"   ⚠️  OCPP Alert: {alert.alert_type}")
        
        # CAN frame gönder
        if message_count < len(can_frames):
            can_id, data = can_frames[message_count % len(can_frames)]
            ids.register_authorized_can_frame(can_id, data)
            alert = ids.check_can_frame(can_id, data, time.time())
            if alert:
                print(f"   ⚠️  CAN Alert: {alert.alert_type}")
        
        message_count += 1
        time.sleep(0.5)
    
    print(f"   ✅ {message_count} mesaj simüle edildi\n")

def test_fail_open_with_traffic():
    """Fail-Open davranışını trafik ile simüle et"""
    print("=" * 60)
    print("SENARYO #4: FAIL-OPEN DAVRANIŞI + TRAFİK SİMÜLASYONU")
    print("=" * 60)
    
    # IDS oluştur
    ids = RuleBasedIDS()
    print("✅ IDS başlatıldı\n")
    
    current_time = time.time()
    
    # Adım 1: Auth Servis'e DoS saldırısı
    print("📡 [1/5] Auth Servis'e DoS saldırısı başlatılıyor...")
    for i in range(5):
        ids.check_auth_failure("TIMEOUT", current_time + i)
        time.sleep(0.3)
    print("   ✅ 5 ardışık auth timeout oluşturuldu\n")
    
    # Adım 2: Fail-Open davranışı
    print("🚨 [2/5] FAIL-OPEN DAVRANIŞI TETİKLENİYOR...")
    alert = ids.check_charge_without_auth(True, "TIMEOUT", current_time + 5)
    if alert:
        print(f"   🚨 CRITICAL: {alert.alert_type}\n")
    
    # Adım 3: Şarj trafiği başlat (Fail-Open durumunda)
    print("⚡ [3/5] Şarj başlatıldı - Trafik akışı başlıyor...")
    simulate_charging_traffic(ids, duration=8)
    
    # Adım 4: Alert'leri API'ye gönder
    print("📤 [4/5] Alert'ler API'ye gönderiliyor...")
    alerts = ids.get_recent_alerts(20)
    api_url = "http://localhost:8000/api/alerts"
    
    sent_count = 0
    for alert in alerts:
        try:
            response = requests.post(api_url, json=alert.to_dict(), timeout=2)
            if response.status_code == 200:
                sent_count += 1
        except:
            pass
    
    print(f"   ✅ {sent_count} alert API'ye gönderildi\n")
    
    # Adım 5: İstatistikler
    print("📊 [5/5] İSTATİSTİKLER")
    print("=" * 60)
    stats = ids.get_stats()
    
    print(f"   OCPP Mesajlar: {stats['total_ocpp_messages']}")
    print(f"   CAN Frame'ler: {stats['total_can_frames']}")
    print(f"   Toplam Alert: {stats['total_alerts']}")
    print(f"   Auth Olmadan Şarj: {stats['charge_starts_without_auth']}")
    
    alert_breakdown = stats.get('alert_breakdown', {})
    print(f"\n   Alert Dağılımı:")
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = alert_breakdown.get(severity, 0)
        if count > 0:
            print(f"      {severity}: {count}")
    
    print("\n" + "=" * 60)
    print("✅ Senaryo #4 simülasyonu tamamlandı!")
    print("=" * 60)
    print("\n📋 Dashboard'da şunları görmelisiniz:")
    print("   ✅ CAN Frame sayısı artmış olmalı")
    print("   ✅ OCPP Mesaj sayısı artmış olmalı")
    print("   ✅ FAIL_OPEN_BEHAVIOR alert'i (CRITICAL)")
    print("   ✅ AUTH_SERVICE_UNAVAILABLE alert'leri (HIGH)")
    print("   ✅ Toplam Alert sayısı > 0")
    print("\n🌐 Dashboard: http://localhost:8501\n")

if __name__ == "__main__":
    test_fail_open_with_traffic()

