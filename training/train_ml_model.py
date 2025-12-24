"""
ML Model Eğitim Scripti (Mutfak)
utils/ml_ids.py içindeki yapıyı kullanarak modeli eğitir.
"""
import sys
import os
import time
import random
from loguru import logger

# --- PATH AYARLARI ---
# utils klasörüne erişmek için bir üst dizini path'e ekle
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.ml_ids import MLBasedIDS

# Modelin kaydedileceği yer
MODEL_PATH = os.path.join(BASE_DIR, "models", "isolation_forest.pkl")

def generate_and_train():
    logger.info("ML Model Eğitimi Başlatılıyor...")

    # 1. ML-IDS Nesnesini Oluştur
    ml_ids = MLBasedIDS(contamination=0.05) # %5 anomali payı

    # --- DÜZELTME BURADA ---
    # Modelin içini kontrol etme, sadece 'None' mu diye bak.
    if ml_ids.model is None:
        logger.error("sklearn bulunamadı, eğitim iptal.")
        return
    # -----------------------

    # 2. Sentetik Normal Trafik Üret
    logger.info("Sentetik veri üretiliyor...")
    
    start_time = time.time()
    current_time = start_time
    
    # Normal Trafik Paternleri
    patterns = {
        0x200: (lambda i: [0x01, i % 255, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0.1), 
        0x201: (lambda i: [0x02, (i*2) % 255, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0.5), 
        0x300: (lambda i: [0x03, random.randint(50, 60), 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 1.0),
    }

    # 5000 adet örnek veri üretelim
    for i in range(5000):
        can_id = random.choice(list(patterns.keys()))
        data_func, avg_interval = patterns[can_id]
        
        payload = data_func(i)
        
        time_step = random.uniform(0.01, 0.1)
        current_time += time_step
        
        ml_ids.add_training_sample(
            can_id=can_id,
            data=payload,
            timestamp=current_time
        )

    logger.info(f"{len(ml_ids.training_buffer)} adet eğitim verisi hazırlandı.")

    # 3. Modeli Eğit
    success = ml_ids.train(min_samples=1000)
    
    if success:
        # 4. Modeli Kaydet
        model_dir = os.path.dirname(MODEL_PATH)
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
            
        if ml_ids.save_model(MODEL_PATH):
            logger.success(f"✅ Model başarıyla eğitildi ve kaydedildi: {MODEL_PATH}")
        else:
            logger.error("Model kaydedilemedi.")
    else:
        logger.error("Eğitim başarısız oldu.")

if __name__ == "__main__":
    generate_and_train()