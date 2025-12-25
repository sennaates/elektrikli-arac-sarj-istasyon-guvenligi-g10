"""
Test Script for Senaryo #5: Duplicate Booking Attack
Bu script, duplicate booking saldırısını test eder ve IDS'in tespit edip etmediğini kontrol eder.
"""

import asyncio
import sys
import time
from pathlib import Path

# Proje root'unu path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from attack_simulator import AttackSimulator
from loguru import logger


async def test_duplicate_booking_scenarios():
    """Tüm duplicate booking senaryolarını test et"""
    
    logger.info("=" * 70)
    logger.info("SENARYO #5: DUPLICATE BOOKING ATTACK TEST")
    logger.info("=" * 70)
    
    simulator = AttackSimulator(interface="vcan0")
    
    # CSMS URL'i
    csms_url = "ws://localhost:9000"
    
    test_scenarios = [
        ("duplicate_id", "Aynı reservationId ile iki ReserveNow isteği"),
        ("multiple_connector", "Aynı connectorId için çoklu rezervasyon"),
        ("id_reuse", "Daha önce kullanılmış reservationId tekrar kullanımı"),
        ("mismatch_transaction", "Rezervasyondaki idTag ile farklı idTag ile şarj başlatma")
    ]
    
    for scenario, description in test_scenarios:
        logger.info("\n" + "=" * 70)
        logger.info(f"TEST: {scenario.upper()}")
        logger.info(f"Açıklama: {description}")
        logger.info("=" * 70)
        
        try:
            await simulator.duplicate_booking_attack_async(
                csms_url=csms_url,
                scenario=scenario
            )
            
            logger.success(f"✓ {scenario} testi tamamlandı")
            
            # Senaryolar arası bekleme
            await asyncio.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ {scenario} testi başarısız: {e}")
            logger.exception(e)
    
    logger.info("\n" + "=" * 70)
    logger.info("TÜM TESTLER TAMAMLANDI")
    logger.info("=" * 70)
    logger.info("\nBeklenen IDS Alerts:")
    logger.info("  - DUPLICATE_RESERVATION_ID (Kural-1) - CRITICAL")
    logger.info("  - MULTIPLE_CONNECTOR_RESERVATIONS (Kural-2) - CRITICAL")
    logger.info("  - RESERVATION_ID_REUSE (Kural-3) - HIGH")
    logger.info("  - RESERVATION_TRANSACTION_MISMATCH (Kural-5) - CRITICAL")
    logger.info("\nDashboard'da kırmızı alarmlar görünmeli!")


def main():
    """Ana entry point"""
    # Logger config
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>"
    )
    
    logger.warning("⚠️  ÖNEMLİ: CSMS simülatörü çalışıyor olmalı!")
    logger.info("   CSMS'i başlatmak için: python csms_simulator.py")
    logger.info("   Bridge'i başlatmak için: python secure_bridge.py")
    logger.info("")
    
    try:
        asyncio.run(test_duplicate_booking_scenarios())
    except KeyboardInterrupt:
        logger.warning("\n⚠ Test durduruldu (Ctrl+C)")
    except Exception as e:
        logger.error(f"\n❌ Test hatası: {e}")
        logger.exception(e)


if __name__ == "__main__":
    main()

