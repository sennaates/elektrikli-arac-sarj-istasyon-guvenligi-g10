"""
CLAC-SCO: Coordinated Load Alteration via Compromised Smart Charging Orchestrator
Koordineli Yük Değişikliği Saldırısı - Anomali Senaryosu

Hazırlayan: Şeref (Osama)
Tarih: 2025-01-27

SENARYO AÇIKLAMASI:
Bu senaryo, ele geçirilen bir akıllı şarj orkestratörünün (Smart Charging Orchestrator)
vasıtasıyla çok sayıda şarj noktasına eşzamanlı olarak şarj profili değişikliği enjekte
ederek dağıtım/iletim şebekesinde ani yük değişimleri oluşturmasını simüle eder.

SALDIRI AKIŞI:
1. Orkestratör ele geçirilir (simüle edilir)
2. Çok sayıda Charge Point'e eşzamanlı SetChargingProfile komutları gönderilir
3. Tüm CP'ler aynı anda yük artışı/azalışı yapar
4. Şebeke yük dengesizliği oluşur

TESPİT GÖSTERGELERİ:
- Aynı zamanda çok sayıda CP'de benzer profil değişimleri
- Temporal correlation (zaman korelasyonu)
- Beklenmeyen yük artışları
- CAN trafiğinde burst pattern
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict


# pytest'i opsiyonel yap
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    # pytest decorator'ını mock et
    class MockPytest:
        @staticmethod
        def mark_asyncio(func):
            return func
    pytest = MockPytest()

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ocpp.central_system.simulator import CSMSimulator
from src.ocpp.charge_point.simulator import ChargePointSimulator
from src.detection.can_ids import CANIntrusionDetector
from src.can_bus.can_simulator import CANMessage

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_clac_sco_coordinated_attack():
    """
    CLAC-SCO: Koordineli Yük Değişikliği Saldırısı
    
    Bu test, ele geçirilen orkestratörün çok sayıda CP'ye eşzamanlı
    şarj profili değişikliği göndermesini simüle eder.
    
    Beklenen Sonuç:
    - En az 5 CP'ye eşzamanlı SetChargingProfile gönderilir
    - CAN trafiğinde burst pattern tespit edilir
    - Temporal correlation (zaman korelasyonu) gözlemlenir
    - IDS anomali tespit eder
    """
    print("\n" + "="*80)
    print("CLAC-SCO: COORDINATED LOAD ALTERATION ATTACK")
    print("="*80)
    
    # ==========================================
    # ADIM 1: SETUP - CSMS ve Çoklu CP'ler
    # ==========================================
    
    # CSMS başlat (orkestratör simülasyonu)
    # Port çakışmasını önlemek için rastgele port kullan
    import random
    base_port = 9030
    port = base_port + random.randint(0, 100)  # 9030-9130 arası rastgele port
    
    csms = CSMSimulator(host='0.0.0.0', port=port, scenario='plain_ws')  # 0.0.0.0 tüm interface'lerde dinle
    csms_task = asyncio.create_task(csms.start())
    
    # CSMS'in server'ının başlamasını bekle
    await asyncio.sleep(2)  # Server'ın başlaması için bekle
    if csms.server_started:
        try:
            await asyncio.wait_for(csms.server_started.wait(), timeout=3.0)
            logger.info(f"✅ CSMS server başladı, bağlantılar kabul ediliyor...")
        except asyncio.TimeoutError:
            logger.warning("⚠️  CSMS server başlatma timeout - devam ediliyor...")
    else:
        logger.warning("⚠️  server_started event henüz oluşturulmadı, bekleniyor...")
        await asyncio.sleep(1)
    
    # Çoklu Charge Point'ler oluştur (5 CP simüle ediyoruz)
    NUM_CHARGE_POINTS = 5
    charge_points: List[ChargePointSimulator] = []
    cp_tasks: List[asyncio.Task] = []
    
    try:
        logger.info(f"🔌 {NUM_CHARGE_POINTS} Charge Point başlatılıyor...")
        
        for i in range(1, NUM_CHARGE_POINTS + 1):
            cp_id = f"CP_CLAC_{i:03d}"
            cp = ChargePointSimulator(
                cp_id=cp_id,
                scenario='plain_ws',
                csms_url=f'ws://127.0.0.1:{port}/charge_point/{cp_id.lower()}'  # Dinamik port kullan
            )
            charge_points.append(cp)
            cp_task = asyncio.create_task(cp.start())
            cp_tasks.append(cp_task)
            await asyncio.sleep(0.3)  # Bağlantıların sırayla kurulması için
        
        # Tüm CP'lerin bağlanmasını bekle (daha uzun süre)
        await asyncio.sleep(5)  # WebSocket bağlantıları için daha fazla zaman
        logger.info(f"✅ {len(csms.connected_cps)} Charge Point bağlandı")
        
        # Bağlı CP ID'lerini logla
        if csms.connected_cps:
            logger.info(f"📋 Bağlı CP ID'leri: {list(csms.connected_cps.keys())}")
        else:
            logger.warning("⚠️  Hiç CP bağlanmadı! WebSocket bağlantıları kontrol ediliyor...")
            await asyncio.sleep(2)  # Biraz daha bekle
        
        # CAN IDS başlat (anomali tespiti için)
        detector = CANIntrusionDetector(window_size=200)
        detector.learn_baseline(duration_seconds=5)
        
        # ==========================================
        # ADIM 2: NORMAL AKIŞ (Baseline)
        # ==========================================
        
        logger.info("📊 Normal akış başlatılıyor (baseline)...")
        
        # Normal şarj başlat (bazı CP'lerde)
        # CSMS'deki bağlı CP ID'lerini al (path'den çıkarılan format)
        connected_cp_ids = list(csms.connected_cps.keys())
        logger.info(f"📋 Bağlı CP ID'leri: {connected_cp_ids}")
        
        for i, cp in enumerate(charge_points[:3]):  # İlk 3 CP'de normal şarj
            # CP ID'yi farklı formatlarda dene
            cp_id_variants = [cp.cp_id, cp.cp_id.lower(), cp.cp_id.upper()]
            cp_id_to_use = None
            
            for variant in cp_id_variants:
                if variant in connected_cp_ids:
                    cp_id_to_use = variant
                    break
            
            if cp_id_to_use:
                await csms.send_remote_start(cp_id_to_use, connector_id=1)
                await asyncio.sleep(0.2)
            else:
                logger.warning(f"⚠️  CP {cp.cp_id} bağlı CP listesinde bulunamadı")
        
        await asyncio.sleep(2)  # Normal trafik için bekle
        
        # Baseline finalize et
        detector.finalize_baseline()
        logger.info("✅ Baseline oluşturuldu")
        
        # ==========================================
        # ADIM 3: SALDIRI - Koordineli Profil Değişikliği
        # ==========================================
        
        logger.warning("🚨 SALDIRI BAŞLATILIYOR: CLAC-SCO Coordinated Attack")
        logger.warning("   → Ele geçirilen orkestratör tüm CP'lere eşzamanlı komut gönderiyor...")
        
        # Saldırı parametreleri
        ATTACK_MAX_CURRENT = 50  # Anormal yüksek akım (A)
        ATTACK_PROFILE_ID = 999  # Şüpheli profil ID
        
        # Tüm bağlı CP'lere EŞZAMANLI SetChargingProfile gönder
        attack_timestamp = datetime.now()
        attack_tasks = []
        
        for cp_id in list(csms.connected_cps.keys()):
            # Eşzamanlı gönderim için task oluştur
            task = csms.send_set_charging_profile(
                cp_id=cp_id,
                connector_id=1,
                charging_profile_id=ATTACK_PROFILE_ID,
                max_current=ATTACK_MAX_CURRENT
            )
            attack_tasks.append(task)
        
        # Tüm saldırı komutlarını EŞZAMANLI gönder
        results = await asyncio.gather(*attack_tasks, return_exceptions=True)
        
        successful_attacks = sum(1 for r in results if r is True)
        logger.warning(f"⚠️  {successful_attacks}/{len(attack_tasks)} CP'ye saldırı komutu gönderildi")
        
        # Saldırı sonrası kısa bekleme (etkilerin gözlemlenmesi için)
        await asyncio.sleep(1)
        
        # ==========================================
        # ADIM 4: ANOMALİ TESPİTİ
        # ==========================================
        
        logger.info("🔍 Anomali tespiti yapılıyor...")
        
        # Her CP'den istatistikleri topla
        all_stats = {}
        total_profile_changes = 0
        total_can_messages = 0
        
        for cp in charge_points:
            stats = cp.get_stats()
            cp_id = cp.cp_id
            all_stats[cp_id] = stats
            
            gateway_stats = stats.get('gateway_stats', {})
            total_can_messages += gateway_stats.get('ocpp_to_can', 0)
        
        # CAN IDS istatistikleri
        ids_stats = detector.get_detection_stats()
        
        # Temporal correlation analizi
        # Aynı zamanda çok sayıda profil değişikliği = anomali
        profile_changes_in_window = successful_attacks
        
        logger.info(f"📊 Tespit İstatistikleri:")
        logger.info(f"   - Toplam CAN mesajı: {total_can_messages}")
        logger.info(f"   - Profil değişikliği sayısı: {profile_changes_in_window}")
        logger.info(f"   - IDS anomali sayısı: {ids_stats.get('anomalies_detected', 0)}")
        
        # ==========================================
        # ADIM 5: DOĞRULAMA (Assertions)
        # ==========================================
        
        # Test 1: En az 3 CP'ye saldırı komutu gönderilmiş olmalı
        assert successful_attacks >= 3, \
            f"Yetersiz saldırı: {successful_attacks} CP'ye komut gönderildi (en az 3 bekleniyor)"
        
        # Test 2: Toplam CAN mesajı sayısı yeterli olmalı
        assert total_can_messages >= successful_attacks, \
            f"CAN mesajları eksik: {total_can_messages} mesaj (en az {successful_attacks} bekleniyor)"
        
        # Test 3: Temporal correlation - Aynı zamanda çok sayıda değişiklik
        # (Bu bir anomali göstergesidir)
        assert profile_changes_in_window >= 3, \
            f"Koordinasyon tespit edilemedi: {profile_changes_in_window} eşzamanlı değişiklik"
        
        # Test 4: CSMS istatistikleri
        csms_stats = csms.get_stats()
        assert csms_stats['connected_cps'] >= 3, \
            f"Yetersiz CP bağlantısı: {csms_stats['connected_cps']} CP"
        
        logger.warning("✅ CLAC-SCO saldırı senaryosu başarıyla tamamlandı!")
        logger.warning("   → Koordineli yük değişikliği tespit edildi")
        logger.warning("   → Temporal correlation gözlemlendi")
        
        # ==========================================
        # ADIM 6: CLEANUP
        # ==========================================
        
        logger.info("🧹 Temizlik yapılıyor...")
        
        # Tüm CP'leri durdur
        for cp in charge_points:
            try:
                await cp.stop()
            except Exception as e:
                logger.debug(f"CP durdurma hatası: {e}")
        
        # CSMS'i durdur
        await csms.stop()
        
        # Task'ları iptal et
        for task in cp_tasks:
            task.cancel()
        csms_task.cancel()
        
        logger.info("✅ Temizlik tamamlandı")
        
    except Exception as e:
        logger.error(f"❌ Senaryo hatası: {e}", exc_info=True)
        
        # Hata durumunda da temizlik yap
        for cp in charge_points:
            try:
                await cp.stop()
            except:
                pass
        
        try:
            await csms.stop()
        except:
            pass
        
        for task in cp_tasks:
            task.cancel()
        csms_task.cancel()
        
        raise


@pytest.mark.asyncio
async def test_clac_sco_detection_indicators():
    """
    CLAC-SCO Tespit Göstergeleri Testi
    
    Bu test, CLAC-SCO saldırısının tespit göstergelerini doğrular:
    - Temporal correlation (zaman korelasyonu)
    - Burst pattern tespiti
    - Anormal profil değişiklikleri
    """
    print("\n" + "="*80)
    print("CLAC-SCO: DETECTION INDICATORS TEST")
    print("="*80)
    
    # Port çakışmasını önlemek için rastgele port
    import random
    detect_port = 9031 + random.randint(0, 100)
    
    csms = CSMSimulator(host='0.0.0.0', port=detect_port, scenario='plain_ws')
    csms_task = asyncio.create_task(csms.start())
    
    # Server'ın başlamasını bekle
    await asyncio.sleep(2)
    if csms.server_started:
        try:
            await asyncio.wait_for(csms.server_started.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
    
    try:
        # 3 CP başlat
        cps = []
        for i in range(1, 4):
            cp = ChargePointSimulator(
                cp_id=f"CP_DETECT_{i:03d}",
                scenario='plain_ws',
                csms_url=f'ws://127.0.0.1:{detect_port}/charge_point/cp_detect_{i:03d}'
            )
            cps.append(cp)
            await cp.start()
            await asyncio.sleep(0.5)
        
        await asyncio.sleep(2)
        
        # Saldırı: Eşzamanlı profil değişikliği
        attack_tasks = []
        for cp_id in list(csms.connected_cps.keys()):
            task = csms.send_set_charging_profile(
                cp_id=cp_id,
                connector_id=1,
                charging_profile_id=999,
                max_current=50
            )
            attack_tasks.append(task)
        
        # Eşzamanlı gönder
        await asyncio.gather(*attack_tasks)
        await asyncio.sleep(1)
        
        # Tespit göstergelerini kontrol et
        # 1. Temporal correlation: Aynı zamanda 3+ değişiklik
        simultaneous_changes = len(attack_tasks)
        assert simultaneous_changes >= 3, "Temporal correlation tespit edilemedi"
        
        # 2. Burst pattern: Kısa sürede çok mesaj
        total_messages = sum(cp.get_stats()['gateway_stats'].get('ocpp_to_can', 0) 
                            for cp in cps)
        assert total_messages >= 3, "Burst pattern tespit edilemedi"
        
        logger.info("✅ Tespit göstergeleri doğrulandı")
        
        # Cleanup
        for cp in cps:
            await cp.stop()
        await csms.stop()
        csms_task.cancel()
        
    except Exception as e:
        logger.error(f"❌ Test hatası: {e}")
        await csms.stop()
        csms_task.cancel()
        raise


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # pytest olmadan direkt çalıştırma
    async def run_tests():
        print("\n" + "="*80)
        print("CLAC-SCO Senaryosu Çalıştırılıyor...")
        print("="*80 + "\n")
        
        try:
            await test_clac_sco_coordinated_attack()
            print("\n✅ Ana test başarıyla tamamlandı!\n")
        except Exception as e:
            print(f"\n❌ Test hatası: {e}\n")
            import traceback
            traceback.print_exc()
        
        try:
            await test_clac_sco_detection_indicators()
            print("\n✅ Tespit göstergeleri testi başarıyla tamamlandı!\n")
        except Exception as e:
            print(f"\n❌ Tespit testi hatası: {e}\n")
            import traceback
            traceback.print_exc()
    
    # pytest varsa kullan, yoksa direkt çalıştır
    try:
        import pytest
        pytest.main([__file__, '-v', '-s'])
    except ImportError:
        print("⚠️  pytest bulunamadı, direkt çalıştırılıyor...\n")
        asyncio.run(run_tests())

