"""
IDS'i direkt test etmek için script.
OCPP mesajlarını simüle eder, bridge'in IDS'ine direkt erişir.
Bu script, OCPP mesajlarının bridge'e ulaşmadan IDS'i test eder.
"""
import sys
import os
import time
import requests
import json
sys.path.insert(0, os.path.dirname(__file__))

from utils.ids import RuleBasedIDS
from utils.blockchain import Blockchain
from loguru import logger

# Logger config
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>"
)


def send_alert_to_api(alert_dict: dict, api_url: str = "http://localhost:8000"):
    """Alert'i API server'a gönder"""
    try:
        response = requests.post(
            f"{api_url}/api/alerts",
            json=alert_dict,
            timeout=2
        )
        if response.status_code == 200:
            logger.debug(f"   ✓ Alert API'ye gönderildi")
            return True
    except Exception as e:
        logger.debug(f"   ⚠ API'ye gönderilemedi: {e}")
    return False


def test_scenario_1_timing_anomaly(send_to_api: bool = True):
    """Senaryo #1: Timing Anomaly"""
    print("="*60)
    print("SENARYO #1: Timing Anomaly Test")
    print("="*60)
    
    ids = RuleBasedIDS()
    alerts_found = []
    
    # 1. RemoteStartTransaction gönder
    timestamp1 = time.time()
    alert1 = ids.check_ocpp_message(
        "RemoteStartTransaction",
        {"connector_id": 1, "id_tag": "TEST_001"},
        timestamp1
    )
    logger.info(f"✓ RemoteStartTransaction gönderildi (alert: {alert1 is not None})")
    
    # 2. 1 saniye sonra RemoteStopTransaction (K1 kuralı tetiklenmeli)
    time.sleep(1.0)
    timestamp2 = time.time()
    alert2 = ids.check_ocpp_message(
        "RemoteStopTransaction",
        {"transaction_id": 1},
        timestamp2
    )
    
    if alert2:
        logger.success(f"✅ ALERT TESPİT EDİLDİ: {alert2.alert_type}")
        logger.info(f"   Severity: {alert2.severity}")
        logger.info(f"   Description: {alert2.description}")
        alerts_found.append(alert2)
        
        if send_to_api:
            send_alert_to_api(alert2.to_dict())
        return True
    else:
        logger.error("❌ Alert tespit edilmedi!")
        logger.info("   Not: K1 kuralı (timing mismatch) tetiklenmeli")
        return False


def test_scenario_2_ocpp_flooding(send_to_api: bool = True):
    """Senaryo #2: OCPP Message Flooding"""
    print("\n" + "="*60)
    print("SENARYO #2: OCPP Message Flooding Test")
    print("="*60)
    
    ids = RuleBasedIDS()
    alerts = []
    
    logger.info("20 mesaj/saniye gönderiliyor (eşik: 5 mesaj/s)...")
    
    # 20 mesaj/saniye gönder (eşik: 5 mesaj/s)
    for i in range(20):
        alert = ids.check_ocpp_message(
            "Heartbeat",
            {},
            time.time()
        )
        if alert:
            alerts.append(alert)
            logger.warning(f"   [{i+1}] Alert tespit edildi: {alert.alert_type}")
        time.sleep(0.05)  # 20 mesaj/saniye
    
    if alerts:
        logger.success(f"✅ {len(alerts)} ALERT TESPİT EDİLDİ")
        for alert in alerts:
            logger.info(f"   - {alert.alert_type} ({alert.severity})")
            if send_to_api:
                send_alert_to_api(alert.to_dict())
        return True
    else:
        logger.error("❌ Alert tespit edilmedi!")
        logger.info("   Not: OCPP_RATE_LIMIT_EXCEEDED alert'i bekleniyor")
        return False


def test_scenario_3_sampling_manipulation(send_to_api: bool = True):
    """Senaryo #3: Sampling Rate Drop"""
    print("\n" + "="*60)
    print("SENARYO #3: Sampling Rate Drop Test")
    print("="*60)
    
    ids = RuleBasedIDS()
    alerts = []
    
    logger.info("Düşük örnekleme oranı simüle ediliyor...")
    
    # Önce normal örnekleme (yüksek rate) - geçmişte
    base_time = time.time() - 120  # 2 dakika öncesinden başla
    for i in range(60):
        alert = ids.check_meter_values(
            meter_value=10.0 + (i * 0.01),
            timestamp=base_time + (i * 1.0),  # Her saniye bir sample
            session_id="TEST_SESSION"
        )
        if alert:
            alerts.append(alert)
    
    logger.info("   ✓ 60 normal sample gönderildi (60 sample/min)")
    
    # Şimdi düşük rate (her 60 saniyede bir) - geçmişte
    current_time = time.time()
    for i in range(3):
        alert = ids.check_meter_values(
            meter_value=10.5 + (i * 0.1),
            timestamp=current_time - (60 * (2 - i)),  # Geriye doğru zaman
            session_id="TEST_SESSION"
        )
        if alert:
            alerts.append(alert)
        time.sleep(0.1)
    
    # Son sample (düşük rate tespit edilmeli) - şimdi
    alert = ids.check_meter_values(
        meter_value=10.5,
        timestamp=time.time(),
        session_id="TEST_SESSION"
    )
    
    if alert:
        alerts.append(alert)
    
    # Eğer hala alert yoksa, daha fazla düşük rate sample gönder
    if not alerts:
        logger.info("   Düşük rate sample'ları gönderiliyor...")
        for i in range(5):
            alert = ids.check_meter_values(
                meter_value=10.5 + (i * 0.01),
                timestamp=time.time() - (60 * (4 - i)),  # Her 60 saniyede bir
                session_id="TEST_SESSION"
            )
            if alert:
                alerts.append(alert)
            time.sleep(0.1)
    
    if alerts:
        logger.success(f"✅ {len(alerts)} ALERT TESPİT EDİLDİ")
        for alert in alerts:
            logger.info(f"   - {alert.alert_type} ({alert.severity})")
            logger.info(f"     {alert.description}")
            if send_to_api:
                send_alert_to_api(alert.to_dict())
        return True
    else:
        logger.error("❌ Alert tespit edilmedi!")
        logger.info("   Not: SAMPLING_RATE_DROP alert'i bekleniyor")
        logger.info("   Not: Minimum 30 sample/min gerekli, düşük rate tespit edilmeli")
        return False


def main():
    """Ana test fonksiyonu"""
    print("\n" + "="*70)
    print("IDS DİREKT TEST SCRIPTİ")
    print("="*70)
    print("\nBu script IDS'i direkt test eder, OCPP mesajlarını simüle eder.")
    print("Alert'ler API server'a gönderilir (http://localhost:8000)")
    print("\n" + "="*70 + "\n")
    
    results = []
    
    # Test 1
    try:
        results.append(("Senaryo #1 (Timing Anomaly)", test_scenario_1_timing_anomaly()))
    except Exception as e:
        logger.error(f"Senaryo #1 hatası: {e}")
        results.append(("Senaryo #1", False))
    
    time.sleep(2)
    
    # Test 2
    try:
        results.append(("Senaryo #2 (OCPP Flooding)", test_scenario_2_ocpp_flooding()))
    except Exception as e:
        logger.error(f"Senaryo #2 hatası: {e}")
        results.append(("Senaryo #2", False))
    
    time.sleep(2)
    
    # Test 3
    try:
        results.append(("Senaryo #3 (Sampling Manipulation)", test_scenario_3_sampling_manipulation()))
    except Exception as e:
        logger.error(f"Senaryo #3 hatası: {e}")
        results.append(("Senaryo #3", False))
    
    # Özet
    print("\n" + "="*70)
    print("TEST ÖZETİ")
    print("="*70)
    for name, result in results:
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{name}: {status}")
    
    success_count = sum(1 for _, result in results if result)
    print(f"\nToplam: {success_count}/{len(results)} test başarılı")
    
    print("\n" + "="*70)
    print("💡 Not: Alert'ler API server'a gönderildi.")
    print("   Dashboard'da görmek için: http://localhost:8501")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

