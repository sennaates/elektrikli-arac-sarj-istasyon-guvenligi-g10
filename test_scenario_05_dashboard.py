#!/usr/bin/env python3
"""
Senaryo #5 (Duplicate Booking) test edip dashboard'da görünmesini sağla
"""
import requests
import time
import json
from datetime import datetime

API_URL = "http://localhost:8000"

def test_api_connection():
    """API bağlantısını test et"""
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ API Server çalışıyor")
            return True
        else:
            print(f"❌ API Server yanıt vermiyor: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Server'a bağlanılamıyor: {e}")
        return False

def get_current_stats():
    """Mevcut istatistikleri al"""
    try:
        response = requests.get(f"{API_URL}/api/stats", timeout=2)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"❌ Stats alınamadı: {e}")
        return None

def get_current_alerts():
    """Mevcut alert'leri al"""
    try:
        response = requests.get(f"{API_URL}/api/alerts?count=100", timeout=2)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"❌ Alerts alınamadı: {e}")
        return []

def create_test_alert(alert_type, severity, description):
    """Test alert'i oluştur (API'ye gönder)"""
    alert_data = {
        "alert_id": f"TEST-{int(time.time())}",
        "timestamp": time.time(),
        "timestamp_iso": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "severity": severity,
        "alert_type": alert_type,
        "description": description,
        "source": "OCPP",
        "data": {
            "test": True,
            "scenario": "SCENARIO-05"
        }
    }
    
    try:
        response = requests.post(f"{API_URL}/api/alerts", json=alert_data, timeout=2)
        if response.status_code == 200:
            print(f"  ✅ Alert oluşturuldu: {alert_type}")
            return True
        else:
            print(f"  ❌ Alert oluşturulamadı: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Alert gönderilemedi: {e}")
        return False

def main():
    print("=" * 70)
    print("SENARYO #5: DUPLICATE BOOKING - Dashboard Test")
    print("=" * 70)
    print()
    
    # API bağlantısını test et
    if not test_api_connection():
        print("\n❌ API Server çalışmıyor!")
        print("   Önce API server'ı başlatın: python api_server.py")
        return
    
    print()
    
    # Mevcut durumu göster
    print("📊 Mevcut Durum:")
    stats = get_current_stats()
    if stats:
        blockchain = stats.get("blockchain", {})
        ids = stats.get("ids", {})
        print(f"  - Blockchain Bloklar: {blockchain.get('total_blocks', 0)}")
        print(f"  - Toplam Alert: {ids.get('total_alerts', 0)}")
        print(f"  - CAN Frame: {ids.get('total_can_frames', 0)}")
        print(f"  - OCPP Mesaj: {ids.get('total_ocpp_messages', 0)}")
    else:
        print("  ⚠️  Veri yok (Bridge çalışmıyor olabilir)")
    
    print()
    
    # Mevcut alert'leri göster
    alerts = get_current_alerts()
    print(f"🚨 Mevcut Alert'ler: {len(alerts)}")
    if alerts:
        for alert in alerts[:5]:
            print(f"  - [{alert.get('severity')}] {alert.get('alert_type')}")
    else:
        print("  ⚠️  Hiç alert yok")
    
    print()
    print("=" * 70)
    print("Test Alert'leri Oluşturuluyor (Senaryo #5)...")
    print("=" * 70)
    print()
    
    # Senaryo #5 alert'lerini oluştur
    test_alerts = [
        ("DUPLICATE_RESERVATION_ID", "CRITICAL", 
         "Çift rezervasyon ID tespit edildi: RESERVATION-001 (önceki rezervasyon 1.2s önce)"),
        ("MULTIPLE_CONNECTOR_RESERVATIONS", "CRITICAL",
         "Aynı connector (1) için 2 aktif rezervasyon tespit edildi"),
        ("RESERVATION_ID_REUSE", "HIGH",
         "Rezervasyon ID tekrar kullanımı: RESERVATION-REUSED daha önce kullanılmış"),
        ("RESERVATION_TRANSACTION_MISMATCH", "CRITICAL",
         "Rezervasyon-İşlem uyuşmazlığı: Rezervasyondaki idTag (LEGITIMATE_TAG) ile StartTransaction'daki idTag (ATTACKER_TAG) eşleşmiyor"),
    ]
    
    created = 0
    for alert_type, severity, description in test_alerts:
        if create_test_alert(alert_type, severity, description):
            created += 1
        time.sleep(0.5)
    
    print()
    print("=" * 70)
    print(f"✅ {created} test alert'i oluşturuldu")
    print("=" * 70)
    print()
    print("📊 Dashboard'u yenileyin: http://localhost:8501")
    print()
    print("Beklenen Görünüm:")
    print("  - 🚨 Real-Time Alerts bölümünde yeni alert'ler görünmeli")
    print("  - 🔴 CRITICAL alert'ler kırmızı badge ile görünmeli")
    print("  - Severity dağılımında sayılar artmalı")
    print()

if __name__ == "__main__":
    main()

