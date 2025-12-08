import can
import time
import logging
import random
import requests  # Dashboard'a direkt sinyal göndermek için
import json

# Log ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("RansomwareAttack")

API_URL = "http://localhost:8000/api/alerts"

class AttackSimulator:
    def __init__(self, interface='vcan0'):
        self.interface = interface
        self.bus = None

    def connect(self):
        """CAN Bus'a bağlan"""
        try:
            self.bus = can.interface.Bus(channel=self.interface, bustype='socketcan')
            logger.info("✅ Bağlantı: SocketCAN (Real)")
        except Exception:
            logger.warning("⚠️ SocketCAN başarısız, Virtual mod kullanılıyor...")
            self.bus = can.interface.Bus(channel=self.interface, bustype='virtual')

    def trigger_dashboard_alert(self):
        """
        Dashboard API'sine direkt 'Ransomware' alarmı gönderir.
        Bu sayede IDS yakalamasa bile ekranda görünür.
        """
        alert_data = {
            "alert_id": f"RANSOM-{int(time.time())}",
            "severity": "CRITICAL",
            "alert_type": "Firmware Integrity Failure",
            "description": "RANSOMWARE DETECTED: System locked. Unauthorized firmware update attempt via L02 vulnerability.",
            "source": "IDS_FIRMWARE_CHECK",
            "timestamp": time.time(),
            "data": {"malware_signature": "0xDEADBEEF", "file": "evil_update.bin"}
        }
        
        try:
            response = requests.post(API_URL, json=alert_data)
            if response.status_code == 200:
                logger.info("🚨 Dashboard Alarmı Tetiklendi: BAŞARILI")
            else:
                logger.error(f"Dashboard Alarm Hatası: {response.status_code}")
        except Exception as e:
            logger.error(f"API Bağlantı Hatası: {e} (Dashboard açık mı?)")

    def deploy_ransomware(self):
        """
        SENARYO 1: Sahte Firmware Güncellemesi (Ransomware)
        """
        if not self.bus:
            self.connect()

        print("\n" + "!"*50)
        print("🔴 SENARYO 1: FAKE FIRMWARE & RANSOMWARE SALDIRISI 🔴")
        print("!"*50)
        print("Hedef: Elektrikli Araç Şarj İstasyonu (CS)")
        print("Zafiyet: OCPP L02 (Unsecure Firmware Update)")
        
        time.sleep(1)

        # ADIM 1: Sahte Update Komutu (CAN Bus'a basıyoruz - loglarda görünsün diye)
        print(f">>> [ADIM 1] Sahte 'UpdateFirmware' komutu ağa basılıyor...")
        msg = can.Message(arbitration_id=0x230, data=[0xFF, 0xAA, 0xBB, 0xCC, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
        try:
            self.bus.send(msg)
        except:
            pass
        
        time.sleep(1)

        # ADIM 2: Yükleme Efekti
        print(f"\n>>> [ADIM 2] Ransomware paketi yükleniyor...")
        for i in range(20):
            # Rastgele veri bas
            try:
                self.bus.send(can.Message(arbitration_id=0x777, data=[random.randint(0,255) for _ in range(8)]))
            except:
                pass
            
            # Efekt
            print(f"\rYükleniyor: [{'#' * (i+1)}{'.' * (19-i)}] %{(i+1)*5}", end="")
            time.sleep(0.1)

        print("\n\n>>> [ADIM 3] SİSTEM KİLİTLENİYOR... ALARM GÖNDERİLİYOR!")
        
        # ADIM 3: FİNAL VURUŞU (Dashboard'a Alarm Gönder)
        self.trigger_dashboard_alert()
        
        print("\n✅ SALDIRI TAMAMLANDI. Dashboard'u kontrol et!")

if __name__ == "__main__":
    sim = AttackSimulator()
    sim.connect()
    
    while True:
        print("\n1. Ransomware Saldırısını Başlat")
        print("2. Çıkış")
        secim = input("Seçim: ")
        
        if secim == '1':
            sim.deploy_ransomware()
        elif secim == '2':
            break
