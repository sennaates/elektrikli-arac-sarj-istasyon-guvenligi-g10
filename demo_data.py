#!/usr/bin/env python3
"""
Demo Data Generator - Dashboard için örnek veri oluşturur
"""
import requests
import time
import random
from datetime import datetime

API_URL = "http://localhost:8000"

def generate_demo_alerts():
    """Demo alert'leri oluştur"""
    alerts = [
        {
            "alert_id": f"DEMO-{int(time.time())}-{i}",
            "timestamp": time.time() - (i * 300),  # Her 5 dakikada bir
            "severity": random.choice(["CRITICAL", "HIGH", "MEDIUM", "LOW"]),
            "alert_type": random.choice([
                "UNAUTHORIZED_CAN_FRAME",
                "OCPP_FLOODING",
                "TIMING_ANOMALY",
                "BLOCKCHAIN_VALIDATION_FAILED",
                "ML_ANOMALY_DETECTED"
            ]),
            "description": f"Demo alert #{i+1} - Güvenlik testi",
            "source": "DEMO_GENERATOR"
        }
        for i in range(10)
    ]
    return alerts

def generate_demo_transactions():
    """Demo transaction'ları oluştur"""
    transactions = [
        {
            "transaction_id": f"TX-{1000+i}",
            "charge_point_id": f"CP-DEMO-{(i % 3) + 1:03d}",
            "reservation_id": f"RES-{2000+i}",
            "id_tag": f"USER-{100+i}",
            "start_time": datetime.now().isoformat(),
            "active": random.choice([True, False])
        }
        for i in range(15)
    ]
    return transactions

def generate_demo_chargepoints():
    """Demo charge point'leri oluştur"""
    chargepoints = [
        {
            "charge_point_id": f"CP-DEMO-{i+1:03d}",
            "connected": random.choice([True, False]),
            "is_connected": random.choice([True, False])
        }
        for i in range(5)
    ]
    return chargepoints

def generate_demo_statistics():
    """Demo istatistikleri oluştur"""
    return {
        "connected_charge_points": 3,
        "total_transactions": 15,
        "active_transactions": 8,
        "inactive_transactions": 7
    }

def send_demo_data():
    """Demo verilerini API'ye gönder"""
    print("🎭 Demo verileri oluşturuluyor...")
    
    # Alert'leri gönder
    alerts = generate_demo_alerts()
    for alert in alerts:
        try:
            response = requests.post(f"{API_URL}/api/alerts", json=alert)
            if response.status_code == 200:
                print(f"✅ Alert gönderildi: {alert['alert_type']} ({alert['severity']})")
            else:
                print(f"❌ Alert gönderilemedi: {response.status_code}")
        except Exception as e:
            print(f"❌ Alert gönderim hatası: {e}")
    
    # BSG verilerini gönder
    bsg_data = {
        "transactions": generate_demo_transactions(),
        "charge_points": generate_demo_chargepoints(),
        "statistics": generate_demo_statistics()
    }
    
    try:
        response = requests.post(f"{API_URL}/api/bsg/register", json=bsg_data)
        if response.status_code == 200:
            print(f"✅ BSG verileri gönderildi: {len(bsg_data['transactions'])} transaction, {len(bsg_data['charge_points'])} charge point")
        else:
            print(f"❌ BSG verileri gönderilemedi: {response.status_code}")
    except Exception as e:
        print(f"❌ BSG veri gönderim hatası: {e}")
    
    print("🎉 Demo verileri başarıyla oluşturuldu!")
    print("📊 Dashboard'ı yenileyin: http://localhost:8501")

if __name__ == "__main__":
    # API'nin çalışıp çalışmadığını kontrol et
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Server çalışıyor")
            send_demo_data()
        else:
            print("❌ API Server çalışmıyor")
    except Exception as e:
        print(f"❌ API Server'a bağlanılamıyor: {e}")
        print("Önce API Server'ı başlatın: ./start.sh")