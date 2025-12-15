"""
API Server stats'ını güncelle - Test trafiği için
"""
import requests
import time

def update_api_stats_with_traffic():
    """API stats'ına trafik verileri ekle"""
    
    # Önce mevcut alert'leri al
    alerts = requests.get('http://localhost:8000/api/alerts?count=100').json()
    
    # Trafik istatistikleri hesapla
    ocpp_count = 0
    can_count = 0
    
    # Alert'lerden trafik bilgisi çıkar
    for alert in alerts:
        source = alert.get('source', '')
        if source == 'OCPP':
            ocpp_count += 1
        elif source == 'CAN':
            can_count += 1
    
    # Test trafiği ekle (simülasyondan)
    ocpp_count += 3  # StartTransaction, MeterValues x2
    can_count += 3   # CAN frame'ler
    
    # API'ye stats gönder (bridge register endpoint'i kullan)
    stats = {
        "ids": {
            "total_ocpp_messages": ocpp_count,
            "total_can_frames": can_count,
            "authorized_can_frames": can_count,
            "unauthorized_can_frames": 0,
            "total_alerts": len(alerts),
            "alert_breakdown": {
                "LOW": len([a for a in alerts if a.get('severity') == 'LOW']),
                "MEDIUM": len([a for a in alerts if a.get('severity') == 'MEDIUM']),
                "HIGH": len([a for a in alerts if a.get('severity') == 'HIGH']),
                "CRITICAL": len([a for a in alerts if a.get('severity') == 'CRITICAL'])
            },
            "can_id_frequency": {"0x200": 1, "0x201": 1, "0x202": 1},
            "ocpp_action_frequency": {
                "StartTransaction": 1,
                "MeterValues": 2
            }
        },
        "blockchain": {
            "total_blocks": 1,
            "is_valid": True,
            "block_types": {"OCPP": 1}
        },
        "ml": {
            "is_trained": False,
            "training_samples": 0,
            "contamination": 0.1
        }
    }
    
    try:
        response = requests.post('http://localhost:8000/api/bridge/register', json=stats, timeout=3)
        if response.status_code == 200:
            print("✅ API stats güncellendi")
            print(f"   OCPP Mesajlar: {ocpp_count}")
            print(f"   CAN Frame'ler: {can_count}")
            print(f"   Toplam Alert: {len(alerts)}")
            return True
        else:
            print(f"⚠️  Stats güncellenemedi: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("API STATS GÜNCELLEME")
    print("=" * 60)
    update_api_stats_with_traffic()
    print("\n📋 Dashboard'u yenileyin: http://localhost:8501")

