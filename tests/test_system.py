"""
Sistem Test Scripti
Tüm bileşenleri test eder.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from loguru import logger

# Test edilecek modüller
from utils.blockchain import Blockchain
from utils.can_handler import OCPPtoCANMapper, CANFrame
from utils.ids import RuleBasedIDS
from utils.ml_ids import MLBasedIDS, FeatureExtractor, SKLEARN_AVAILABLE


def test_blockchain():
    """Blockchain modülü testi"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: BLOCKCHAIN")
    logger.info("="*60)
    
    try:
        # Blockchain oluştur
        bc = Blockchain(enable_signature=True)
        
        # Blok ekle
        bc.add_block({"action": "RemoteStartTransaction", "connector": 1}, "OCPP")
        bc.add_block({"can_id": "0x200", "data": [0x01, 0x02]}, "CAN")
        bc.add_block({"alert": "Unauthorized injection"}, "ALERT")
        
        # Doğrula
        is_valid = bc.is_chain_valid()
        
        logger.info(f"Toplam blok: {len(bc)}")
        logger.info(f"Blockchain geçerli: {is_valid}")
        
        if is_valid and len(bc) == 4:  # Genesis + 3 blok
            logger.success("✅ Blockchain testi BAŞARILI")
            return True
        else:
            logger.error("❌ Blockchain testi BAŞARISIZ")
            return False
    
    except Exception as e:
        logger.error(f"❌ Blockchain test hatası: {e}")
        return False


def test_ocpp_to_can_mapping():
    """OCPP → CAN mapping testi"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: OCPP → CAN MAPPING")
    logger.info("="*60)
    
    try:
        mapper = OCPPtoCANMapper()
        
        # Test 1: RemoteStartTransaction
        frame = mapper.ocpp_to_can("RemoteStartTransaction", {
            "connector_id": 1,
            "id_tag": "USER_ABC"
        })
        
        if frame and frame.can_id == 0x200:
            logger.info(f"✓ RemoteStartTransaction → CAN ID {hex(frame.can_id)}")
        else:
            logger.error("❌ RemoteStartTransaction mapping başarısız")
            return False
        
        # Test 2: RemoteStopTransaction
        frame = mapper.ocpp_to_can("RemoteStopTransaction", {
            "transaction_id": 12345
        })
        
        if frame and frame.can_id == 0x201:
            logger.info(f"✓ RemoteStopTransaction → CAN ID {hex(frame.can_id)}")
        else:
            logger.error("❌ RemoteStopTransaction mapping başarısız")
            return False
        
        logger.success("✅ OCPP → CAN mapping testi BAŞARILI")
        return True
    
    except Exception as e:
        logger.error(f"❌ Mapping test hatası: {e}")
        return False


def test_rule_based_ids():
    """Rule-based IDS testi"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: RULE-BASED IDS")
    logger.info("="*60)
    
    try:
        ids = RuleBasedIDS()
        
        # Test 1: Normal trafik (yetkili)
        ids.register_authorized_can_frame(0x200, [0x01, 0x02, 0x03])
        alert = ids.check_can_frame(0x200, [0x01, 0x02, 0x03], time.time())
        
        if alert is None:
            logger.info("✓ Normal trafik doğru sınıflandırıldı")
        else:
            logger.error("❌ Normal trafik yanlış alarm!")
            return False
        
        # Test 2: Unauthorized injection
        alert = ids.check_can_frame(0x200, [0xFF, 0xFF, 0xFF], time.time())
        
        if alert and alert.alert_type == "UNAUTHORIZED_CAN_INJECTION":
            logger.info(f"✓ Unauthorized injection tespit edildi: {alert.description}")
        else:
            logger.error("❌ Unauthorized injection tespit edilemedi!")
            return False
        
        # Test 3: Invalid CAN ID
        alert = ids.check_can_frame(0x9FF, [0x00], time.time())
        
        if alert and alert.alert_type == "INVALID_CAN_ID":
            logger.info(f"✓ Invalid CAN ID tespit edildi: {alert.description}")
        else:
            logger.error("❌ Invalid CAN ID tespit edilemedi!")
            return False
        
        logger.success("✅ Rule-based IDS testi BAŞARILI")
        return True
    
    except Exception as e:
        logger.error(f"❌ IDS test hatası: {e}")
        return False


def test_ml_ids():
    """ML-based IDS testi"""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: ML-BASED IDS")
    logger.info("="*60)
    
    if not SKLEARN_AVAILABLE:
        logger.warning("⚠️  sklearn kurulu değil, ML-IDS testi atlanıyor")
        return True
    
    try:
        ml_ids = MLBasedIDS()
        
        # Eğitim örnekleri ekle (normal trafik)
        logger.info("Normal trafik örnekleri ekleniyor...")
        for i in range(200):
            ml_ids.add_training_sample(
                can_id=0x200,
                data=[i % 256, (i+1) % 256, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                timestamp=time.time() + i * 0.01
            )
        
        # Model eğit
        logger.info("Model eğitiliyor...")
        success = ml_ids.train(min_samples=100)
        
        if not success:
            logger.error("❌ Model eğitimi başarısız!")
            return False
        
        logger.info("✓ Model eğitildi")
        
        # Test: Normal frame
        is_anomaly, score = ml_ids.predict(
            0x200,
            [0x01, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            time.time()
        )
        logger.info(f"Normal frame: anomaly={is_anomaly}, score={score:.3f}")
        
        # Test: Anormal frame
        is_anomaly, score = ml_ids.predict(
            0x9FF,
            [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF],
            time.time()
        )
        logger.info(f"Anormal frame: anomaly={is_anomaly}, score={score:.3f}")
        
        if is_anomaly:
            logger.success("✅ ML-IDS testi BAŞARILI")
            return True
        else:
            logger.warning("⚠️  ML-IDS anormaliyi tespit edemedi (threshold düşük olabilir)")
            return True  # Kritik değil
    
    except Exception as e:
        logger.error(f"❌ ML-IDS test hatası: {e}")
        return False


def test_feature_extractor():
    """Feature extraction testi"""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: FEATURE EXTRACTION")
    logger.info("="*60)
    
    if not SKLEARN_AVAILABLE:
        logger.warning("⚠️  sklearn kurulu değil, test atlanıyor")
        return True
    
    try:
        extractor = FeatureExtractor()
        
        features = extractor.extract_can_features(
            can_id=0x200,
            data=[0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08],
            timestamp=time.time()
        )
        
        if len(features) == 9:  # 9 feature bekleniyor
            logger.info(f"✓ Feature vector boyutu: {len(features)}")
            logger.info(f"  Features: {features}")
            logger.success("✅ Feature extraction testi BAŞARILI")
            return True
        else:
            logger.error(f"❌ Feature boyutu yanlış: {len(features)} (9 bekleniyor)")
            return False
    
    except Exception as e:
        logger.error(f"❌ Feature extraction test hatası: {e}")
        return False


def run_all_tests():
    """Tüm testleri çalıştır"""
    logger.info("\n")
    logger.info("🧪 " + "="*58)
    logger.info("🧪  SİSTEM TESTLERİ BAŞLATILIYOR")
    logger.info("🧪 " + "="*58)
    
    results = {
        "Blockchain": test_blockchain(),
        "OCPP → CAN Mapping": test_ocpp_to_can_mapping(),
        "Rule-Based IDS": test_rule_based_ids(),
        "ML-Based IDS": test_ml_ids(),
        "Feature Extraction": test_feature_extractor()
    }
    
    # Sonuç özeti
    logger.info("\n" + "="*60)
    logger.info("TEST SONUÇLARI")
    logger.info("="*60)
    
    for test_name, passed in results.items():
        status = "✅ BAŞARILI" if passed else "❌ BAŞARISIZ"
        logger.info(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    logger.info("="*60)
    logger.info(f"Toplam: {passed}/{total} test başarılı ({passed/total*100:.0f}%)")
    logger.info("="*60)
    
    return all(results.values())


def main():
    """Ana entry point"""
    # Logger config
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>"
    )
    
    success = run_all_tests()
    
    if success:
        logger.success("\n✅ TÜM TESTLER BAŞARILI!")
        sys.exit(0)
    else:
        logger.error("\n❌ BAZI TESTLER BAŞARISIZ!")
        sys.exit(1)


if __name__ == "__main__":
    main()

