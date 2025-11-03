"""
ÖRNEK: Kendi Anomali Senaryonuz İçin Şablon

Bu dosyayı kopyalayıp, kendi senaryonuzu yazabilirsiniz.

KULLANIM:
1. Bu dosyayı kopyalayın
2. test_my_scenario fonksiyonunu düzenleyin
3. pytest ile çalıştırın: pytest tests/your_file.py -v
"""

import pytest
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

# Temel importlar
from src.ocpp.central_system.simulator import CSMSimulator
from src.ocpp.charge_point.simulator import ChargePointSimulator
from src.detection.can_ids import CANIntrusionDetector
from src.can_bus.can_simulator import CANMessage, CANBusSimulator
from src.attacks.mitm_proxy import MitMProxy

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_my_custom_scenario():
    """
    KENDİ ANOMALİ SENARYONUZU BURAYA YAZIN
    
    Adımlar:
    1. CSMS ve CP başlat
    2. Senaryonuzu uygula
    3. Anomali tespit et
    4. Sonucu doğrula
    """
    print("\n" + "="*80)
    print("KENDİ ANOMALİ SENARYONUZ")
    print("="*80)
    
    # ==========================================
    # ADIM 1: SİMÜLE EDILEBILIR BILEŞENLER
    # ==========================================
    
    # CSMS başlat
    csms = CSMSimulator(host='localhost', port=9020, scenario='plain_ws')
    csms_task = asyncio.create_task(csms.start())
    await asyncio.sleep(2)  # Başlaması için bekle
    
    try:
        # CP başlat
        cp = ChargePointSimulator(
            cp_id='CP_CUSTOM',
            scenario='plain_ws',
            csms_url='ws://localhost:9020/charge_point/cp_custom'
        )
        cp_task = asyncio.create_task(cp.start())
        await asyncio.sleep(3)  # Bağlantı kurulmasını bekle
        
        # CAN IDS başlat
        detector = CANIntrusionDetector()
        
        # ==========================================
        # ADIM 2: SENARYONU UYGULA
        # ==========================================
        
        # ÖRNEK: RemoteStart gönder, sonra aniden durdur
        logger.info("📤 RemoteStartTransaction gönderiliyor...")
        await csms.send_remote_start('cp_custom', connector_id=1)
        await asyncio.sleep(0.5)
        
        # Saldırı: Hemen stop
        logger.warning("🚨 SALDIRI: Hemen RemoteStopTransaction!")
        await csms.send_remote_stop('cp_custom', transaction_id=1)
        await asyncio.sleep(1)
        
        # ==========================================
        # ADIM 3: ANOMALİ TESPİT ET
        # ==========================================
        
        # Gateway stats kontrol et
        cp_stats = cp.get_stats()
        gateway_stats = cp_stats.get('gateway_stats', {})
        
        logger.info(f"📊 Gateway Stats: {gateway_stats}")
        
        # Test: En az 2 mesaj gönderilmiş olmalı
        assert gateway_stats.get('ocpp_to_can', 0) >= 2, "Mesaj gönderilmedi!"
        
        # ==========================================
        # ADIM 4: SONUÇ DOĞRULA
        # ==========================================
        
        logger.warning("✅ Senin Senaryon başarılı!")
        
        # Durdur
        await cp.stop()
        await csms.stop()
        cp_task.cancel()
        csms_task.cancel()
        
    except Exception as e:
        logger.error(f"❌ Senaryo hatası: {e}")
        await csms.stop()
        csms_task.cancel()
        raise


@pytest.mark.asyncio
async def test_mitm_message_manipulation():
    """
    ÖRNEK SENARYO: MitM Mesaj Manipülasyonu
    
    Bu örnek senaryonuzu kopyalayıp değiştirebilirsiniz.
    """
    print("\n" + "="*80)
    print("MITM MESAJ MANİPÜLASYON SENARYOSU")
    print("="*80)
    
    # Setup
    csms = CSMSimulator(host='localhost', port=9021, scenario='plain_ws')
    csms_task = asyncio.create_task(csms.start())
    await asyncio.sleep(2)
    
    try:
        cp = ChargePointSimulator(
            cp_id='CP_MITM_TEST',
            scenario='plain_ws',
            csms_url='ws://localhost:9021/charge_point/cp_mitm_test'
        )
        cp_task = asyncio.create_task(cp.start())
        await asyncio.sleep(3)
        
        # MitM proxy başlat
        # proxy = MitMProxy(proxy_port=9091, target_port=9021)
        # proxy_task = asyncio.create_task(proxy.start())
        # await asyncio.sleep(1)
        
        # Normal Start gönder
        await csms.send_remote_start('cp_mitm_test', connector_id=1)
        await asyncio.sleep(2)
        
        # İstatistikleri kontrol et
        stats = cp.get_stats()
        logger.info(f"📊 Final stats: {stats}")
        
        # Test
        gateway_stats = stats.get('gateway_stats', {})
        assert gateway_stats.get('ocpp_to_can', 0) > 0, "CAN mesajı gönderilmedi!"
        
        logger.info("✅ MitM senaryo başarılı!")
        
        await cp.stop()
        await csms.stop()
        cp_task.cancel()
        csms_task.cancel()
        
    except Exception as e:
        logger.error(f"❌ Senaryo hatası: {e}")
        await csms.stop()
        csms_task.cancel()
        raise


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    pytest.main([__file__, '-v', '-s'])

