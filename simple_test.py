"""
Basit Test Dedektifi
Bu kod vcan/UDP hattını dinler, ML modelini kullanır ve saldırıları ekrana basar.
OS fark etmeksizin (Windows/Mac/Linux) çalışır.
"""
import time
import os
import platform
from utils.can_handler import CANBusHandler
from utils.ml_ids import MLBasedIDS
from utils.ids import RuleBasedIDS
from loguru import logger

def start_detective():
    # İşletim sistemini algıla
    os_name = platform.system()
    mode_str = "MAC/UDP" if os_name == "Darwin" else "LINUX/VCAN" if os_name == "Linux" else "WINDOWS/VIRTUAL"

    print("\n" + "="*60)
    print(f"🕵️  DEDEKTİF MODU BAŞLATILIYOR ({mode_str})")
    print("="*60)

    # 1. Modelleri Yükle
    logger.info("🧠 Yapay Zeka (ML) Modeli yükleniyor...")
    
    # Model yolunu belirle
    model_path = os.path.join("models", "isolation_forest.pkl")
    
    # Modeli başlat
    ml_ids = MLBasedIDS(model_path=model_path)
    
    if not ml_ids.is_trained:
        logger.error(f"❌ Model yüklenemedi! ({model_path} bulunamadı)")
        logger.info("Lütfen önce 'python training/train_ml_model.py' çalıştır.")
        return

    rule_ids = RuleBasedIDS()
    logger.success("✅ Modeller Hazır!")

    # 2. Hattı Dinlemeye Başla
    logger.info("📡 Hat dinleniyor (Veri akışı bekleniyor)...")
    
    # Handler otomatik olarak OS'e göre en uygun modu seçer
    handler = CANBusHandler(interface="vcan0") 
    
    if not handler.connect():
        logger.error("Hat bağlantısı başarısız!")
        return

    try:
        while True:
            # Mesaj gelmesini bekle
            frame = handler.receive_frame(timeout=1.0)
            
            if frame:
                # 1. ML Kontrolü
                is_anomaly, score = ml_ids.predict(frame.can_id, frame.data, frame.timestamp)
                
                # 2. Kural Kontrolü (Rule-Based)
                alert = rule_ids.check_can_frame(frame.can_id, frame.data, frame.timestamp)

                # --- SONUÇLARI YAZDIR ---
                
                if is_anomaly:
                    # ML Yakaladıysa KIRMIZI yaz
                    print(f"\n🚨 [YAPAY ZEKA] ANOMALİ TESPİT ETTİ! Skor: {score:.4f}")
                    print(f"   ID: {hex(frame.can_id)} | Data: {[hex(x) for x in frame.data]}")
                
                elif alert:
                    # Kural Yakaladıysa SARI yaz
                    print(f"\n⚠️ [KURAL] İHLAL TESPİT ETTİ: {alert.description}")
                
                else:
                    # Normalse sessizce nokta koy
                    print(".", end="", flush=True)

    except KeyboardInterrupt:
        print("\nTest durduruldu.")
        handler.disconnect()

if __name__ == "__main__":
    start_detective()