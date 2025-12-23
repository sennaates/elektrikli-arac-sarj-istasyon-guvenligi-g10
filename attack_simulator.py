"""
Attack Simulator - Saldırı Senaryolarını Simüle Eder
Dashboard'da kırmızı alarm tetiklemek için kullanılır.
"""
import can
import time
import random
import argparse
import asyncio
import websockets
import json
import uuid
from datetime import datetime
from typing import List, Dict
from loguru import logger
# Eğer utils.can_handler yoksa hata vermemesi için try-except veya proje yapısına göre import
try:
    from utils.can_handler import CANBusHandler, CANFrame
except ImportError:
    # Test amaçlı dummy handler (Dosya tek başına çalıştırılırsa diye)
    class CANFrame:
        def __init__(self, can_id, data, dlc, timestamp):
            self.can_id = can_id
            self.data = data
            self.dlc = dlc
            self.timestamp = timestamp

    class CANBusHandler:
        def __init__(self, interface): self.interface = interface
        def connect(self): return True
        def disconnect(self): pass
        def send_frame(self, frame): return True


class AttackSimulator:
    """
    Çeşitli saldırı senaryolarını simüle eder.
    
    Saldırı Tipleri:
    1. Unauthorized CAN Injection
    2. CAN Flood Attack
    3. Replay Attack
    4. Invalid CAN ID Attack
    5. Spoofed OCPP Command
    6. MitM OCPP Manipulation
    7. OCPP Message Flooding
    8. Sampling Manipulation
    9. OCPP Protocol Fuzzing (Senaryo #4)
    10. Fail-Open / DoS Attack (Senaryo #4 Alternatif)
    """
    
    def __init__(self, interface: str = "vcan0"):
        self.interface = interface
        self.can_handler = CANBusHandler(interface=interface)
        
        logger.info(f"AttackSimulator başlatıldı: {interface}")
    
    def connect(self) -> bool:
        """CAN-Bus'a bağlan"""
        return self.can_handler.connect()
    
    def disconnect(self) -> None:
        """Bağlantıyı kes"""
        self.can_handler.disconnect()
    
    # Saldırı 1: Unauthorized CAN Injection
    def unauthorized_injection(self, can_id: int = 0x200, count: int = 1):
        """Bridge tarafından gönderilmemiş sahte CAN frame gönder."""
        logger.warning(f"🚨 SALDIRI: Unauthorized CAN Injection başlatılıyor...")
        logger.info(f"   CAN ID: {hex(can_id)}, Frame sayısı: {count}")
        
        for i in range(count):
            data = [0xFF, 0xFF, 0xFF, 0xFF, 0xDE, 0xAD, 0xBE, 0xEF]
            frame = CANFrame(can_id=can_id, data=data, dlc=len(data), timestamp=time.time())
            
            success = self.can_handler.send_frame(frame)
            if success:
                logger.debug(f"  [{i+1}/{count}] Sahte frame gönderildi")
            time.sleep(0.1)
        
        logger.warning(f"✓ Unauthorized Injection tamamlandı ({count} frame)")
    
    # Saldırı 2: CAN Flood Attack
    def can_flood(self, can_id: int = 0x201, duration: float = 2.0, rate: int = 200):
        """Çok kısa sürede çok fazla CAN frame gönder (DoS)."""
        logger.warning(f"🚨 SALDIRI: CAN Flood başlatılıyor...")
        logger.info(f"   CAN ID: {hex(can_id)}, Süre: {duration}s, Rate: {rate} frame/s")
        
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            data = [random.randint(0, 255) for _ in range(8)]
            frame = CANFrame(can_id=can_id, data=data, dlc=8, timestamp=time.time())
            self.can_handler.send_frame(frame)
            frame_count += 1
            time.sleep(1.0 / rate)
        
        logger.warning(f"✓ CAN Flood tamamlandı ({frame_count} frame {duration}s içinde)")
    
    # Saldırı 3: Replay Attack
    def replay_attack(self, can_id: int = 0x200, original_data: List[int] = None, 
                      delay: float = 1.0, replay_count: int = 3):
        """Aynı CAN frame'i kısa aralıklarla tekrar gönder."""
        if not original_data:
            original_data = [0x01, 0x01, 0xAB, 0xCD, 0x00, 0x00, 0x00, 0x00]
        
        logger.warning(f"🚨 SALDIRI: Replay Attack başlatılıyor...")
        logger.info(f"   CAN ID: {hex(can_id)}, Replay sayısı: {replay_count}, Gecikme: {delay}s")
        
        for i in range(replay_count):
            frame = CANFrame(can_id=can_id, data=original_data, dlc=len(original_data), timestamp=time.time())
            self.can_handler.send_frame(frame)
            logger.debug(f"  [{i+1}/{replay_count}] Frame replay edildi")
            if i < replay_count - 1:
                time.sleep(delay)
        
        logger.warning(f"✓ Replay Attack tamamlandı")
    
    # Saldırı 4: Invalid CAN ID Attack
    def invalid_can_id(self, invalid_id: int = 0x9FF, count: int = 5):
        """İzin listesinde olmayan CAN ID ile frame gönder."""
        logger.warning(f"🚨 SALDIRI: Invalid CAN ID başlatılıyor...")
        logger.info(f"   CAN ID: {hex(invalid_id)}, Frame sayısı: {count}")
        
        for i in range(count):
            data = [0x00] * 8
            frame = CANFrame(can_id=invalid_id, data=data, dlc=8, timestamp=time.time())
            self.can_handler.send_frame(frame)
            logger.debug(f"  [{i+1}/{count}] Geçersiz ID ile frame gönderildi")
            time.sleep(0.1)
        
        logger.warning(f"✓ Invalid CAN ID Attack tamamlandı")
    
    # Saldırı 5: High Entropy Attack
    def high_entropy_attack(self, can_id: int = 0x200, count: int = 10):
        """Tamamen rastgele payload ile frame gönder."""
        logger.warning(f"🚨 SALDIRI: High Entropy Attack başlatılıyor...")
        logger.info(f"   CAN ID: {hex(can_id)}, Frame sayısı: {count}")
        
        for i in range(count):
            data = [random.randint(0, 255) for _ in range(8)]
            frame = CANFrame(can_id=can_id, data=data, dlc=8, timestamp=time.time())
            self.can_handler.send_frame(frame)
            logger.debug(f"  [{i+1}/{count}] Yüksek entropy frame gönderildi")
            time.sleep(0.2)
        
        logger.warning(f"✓ High Entropy Attack tamamlandı")
    
    # Saldırı 6: MitM OCPP Manipulation
    def mitm_ocpp_manipulation(self, scenario: str = "start_to_stop"):
        """Man-in-the-Middle OCPP mesaj manipülasyonu simülasyonu."""
        logger.warning(f"🚨 SALDIRI: MitM OCPP Manipulation başlatılıyor...")
        logger.info(f"   Senaryo: {scenario}")
        
        if scenario == "start_to_stop":
            logger.info("   [Simülasyon] RemoteStartTransaction komutu yakalandı")
            time.sleep(0.5)
            logger.warning("   [Manipülasyon] Start → Stop dönüştürülüyor")
            time.sleep(0.3)
            # Stop CAN Frame gönder
            wrong_frame = CANFrame(can_id=0x201, data=[0x02, 0,0,0,0,0,0,0], dlc=8, timestamp=time.time())
            self.can_handler.send_frame(wrong_frame)
            logger.error("   ⚠️  OCPP-CAN Mismatch: Start bekleniyor ama Stop frame gönderildi!")

        elif scenario == "stop_to_start":
            logger.info("   [Simülasyon] RemoteStopTransaction komutu yakalandı")
            time.sleep(0.5)
            logger.warning("   [Manipülasyon] Stop → Start dönüştürülüyor")
            time.sleep(0.3)
            # Start CAN Frame gönder
            wrong_frame = CANFrame(can_id=0x200, data=[0x01, 1, 0xAB, 0xCD, 0,0,0,0], dlc=8, timestamp=time.time())
            self.can_handler.send_frame(wrong_frame)
            logger.error("   ⚠️  OCPP-CAN Mismatch: Stop bekleniyor ama Start frame gönderildi!")

        elif scenario == "timing_anomaly":
            logger.info("   [Simülasyon] Normal RemoteStartTransaction")
            start_frame = CANFrame(can_id=0x200, data=[0x01, 1, 0,0,0,0,0,0], dlc=8, timestamp=time.time())
            self.can_handler.send_frame(start_frame)
            logger.info("   [Normal] Start CAN frame gönderildi")
            
            time.sleep(1.0) # Anomali: Çok kısa süre sonra
            logger.warning("   [Manipülasyon] 1 saniye sonra Stop komutu enjekte ediliyor")
            
            stop_frame = CANFrame(can_id=0x201, data=[0x02, 0,0,0,0,0,0,0], dlc=8, timestamp=time.time())
            self.can_handler.send_frame(stop_frame)
            logger.error("   ⚠️  Timing Anomaly: Start sonrası 1 saniyede Stop!")
        
        logger.warning(f"✓ MitM OCPP Manipulation tamamlandı")
    
    # Saldırı 7: OCPP Message Flooding
    async def ocpp_message_flooding_async(self, csms_url: str = "ws://localhost:9000", rate: int = 20, duration: float = 5.0, message_type: str = "Heartbeat"):
        logger.warning(f"🚨 SALDIRI: OCPP Message Flooding başlatılıyor...")
        logger.info(f"   Hedef: {csms_url}, Rate: {rate}/s, Süre: {duration}s")
        
        message_count = 0
        start_time = time.time()
        
        try:
            async with websockets.connect(csms_url, subprotocols=['ocpp1.6']) as ws:
                logger.info("   ✓ CSMS'e bağlandı")
                while time.time() - start_time < duration:
                    msg = [2, f"flood-{message_count}", message_type, {}]
                    await ws.send(json.dumps(msg))
                    message_count += 1
                    await asyncio.sleep(1.0 / rate)
                
                logger.warning(f"✓ Flooding tamamlandı: {message_count} mesaj")
        except Exception as e:
            logger.error(f"   Flooding hatası: {e}")
    
    def ocpp_message_flooding(self, **kwargs):
        asyncio.run(self.ocpp_message_flooding_async(**kwargs))

    # Saldırı 8: Sampling Manipulation
    def sampling_manipulation(self, scenario: str = "rate_drop", duration: float = 120.0):
        logger.warning(f"🚨 SALDIRI: Sampling Manipulation ({scenario}) başlatılıyor...")
        start_time = time.time()
        
        if scenario == "rate_drop":
            logger.info("   [Manipülasyon] Örnekleme oranı düşürülüyor (1s -> 60s)")
            while time.time() - start_time < duration:
                logger.debug(f"   [Sample] Energy data sent...")
                time.sleep(60.0) # Çok yavaş veri gönderimi
        
        elif scenario == "peak_smoothing":
            logger.info("   [Manipülasyon] Peak değerler ortalama ile gizleniyor")
            buffer = []
            while time.time() - start_time < duration:
                buffer.append(random.uniform(7.0, 15.0))
                if len(buffer) >= 10:
                    avg = sum(buffer) / len(buffer)
                    logger.debug(f"   [Sent] Avg Power: {avg:.2f} kW (Peak gizlendi)")
                    buffer.clear()
                time.sleep(1.0)
                
        elif scenario == "buffer_manipulation":
            logger.info("   [Manipülasyon] Veriler bufferda tutuluyor, gönderilmiyor")
            buffer_count = 0
            while time.time() - start_time < duration:
                buffer_count += 1
                if buffer_count % 30 == 0:
                    logger.debug(f"   [Delayed Send] 30 saniyelik veri toplu gönderildi")
                time.sleep(1.0)
                
        logger.warning(f"✓ Sampling Manipulation tamamlandı")

    # Saldırı 9: OCPP Protocol Fuzzing (Senaryo #4)
    def ocpp_fuzzing_attack(self, target_url: str, intensity: int = 10):
        """Senaryo #04: Fuzzing saldırı simülasyonu"""
        logger.warning(f"🚨 SALDIRI: [OCPP Protocol Fuzzing] başlatılıyor... Hedef: {target_url}")
        fuzz_types = ["TYPE_MUTATION", "LENGTH_MUTATION", "FORMAT_MUTATION"]
        
        for i in range(intensity):
            fuzz_type = random.choice(fuzz_types)
            payload = {}
            logger.info(f"Fuzzing [{i+1}/{intensity}]: {fuzz_type} gönderiliyor...")
            
            # Simülasyon: Fuzzing isteği gönderiliyor gibi bekle
            time.sleep(0.5)

        logger.warning(f"✓ [OCPP Protocol Fuzzing] tamamlandı")

    # Saldırı 10: Fail-Open Attack (Senaryo #4 Alternatif)
    def fail_open_attack(self, csms_url: str, duration: float = 300.0, dos_rate: int = 100):
        """
        Senaryo #04: Fail-Open Attack Simülasyonu.
        CSMS bağlantısını keserek şarj cihazını 'Offline' moda düşürmeye ve
        güvenliksiz şarj (Free Vend) başlatmaya zorlar.
        """
        logger.warning(f"🚨 SALDIRI: [Fail-Open / DoS] başlatılıyor...")
        logger.info(f"   Hedef CSMS: {csms_url}")
        logger.info(f"   Süre: {duration}s, DoS Rate: {dos_rate} req/s")
        logger.info("   Amaç: CSMS bağlantısını koparıp 'Offline Mode'a düşürmek")
        
        start_time = time.time()
        requests_sent = 0
        
        # Simüle edilmiş DoS
        try:
            while time.time() - start_time < duration:
                # DoS trafiği simülasyonu (Log kirliliği yapmamak için her 50de bir log)
                if requests_sent % 50 == 0:
                    logger.debug(f"   [DoS] {dos_rate} adet bağlantı isteği gönderildi (Connection flood)")
                
                requests_sent += dos_rate
                time.sleep(1.0) # Her saniye dos_rate kadar istek simüle et
                
                if requests_sent > dos_rate * 5:
                    logger.warning("   ⚠️  CSMS Yanıt Vermiyor (Simülasyon)")
                    logger.info("   [ChargingStation] Connection Lost -> Entering OFFLINE MODE")
                    logger.info("   [Attacker] Şarj başlatma isteği gönderiliyor (Authentication devre dışı)")
                    break

        except KeyboardInterrupt:
            logger.info("Saldırı durduruldu.")
            
        logger.warning(f"✓ [Fail-Open Attack] tamamlandı. Sistem Offline moda zorlandı.")

    # Kombine saldırı
    def combined_attack(self):
        """Birden fazla saldırı tipini peş peşe uygular."""
        logger.warning("🚨 KOMBİNE SALDIRI BAŞLATILIYOR!")
        logger.info("=" * 60)
        time.sleep(2)
        
        self.unauthorized_injection(can_id=0x200, count=3)
        time.sleep(3)
        self.invalid_can_id(invalid_id=0x9FF, count=3)
        time.sleep(3)
        self.replay_attack(can_id=0x201, delay=1.0, replay_count=3)
        time.sleep(3)
        self.high_entropy_attack(can_id=0x200, count=5)
        time.sleep(3)
        self.can_flood(can_id=0x202, duration=1.0, rate=150)
        
        logger.warning("=" * 60)
        logger.warning("✓ KOMBİNE SALDIRI TAMAMLANDI!")


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(description="CAN-Bus Attack Simulator")
    parser.add_argument(
        "--interface",
        type=str,
        default="vcan0",
        help="CAN interface (default: vcan0)"
    )
    # Conflict çözüldü: Hem fuzzing hem fail_open eklendi
    parser.add_argument(
        "--attack",
        type=str,
        choices=["injection", "flood", "replay", "invalid_id", "entropy", 
                 "mitm", "ocpp_flood", "sampling", "fuzzing", "fail_open", 
                 "combined", "all"],
        default="combined",
        help="Saldırı tipi"
    )
    parser.add_argument(
        "--mitm-scenario",
        type=str,
        choices=["start_to_stop", "stop_to_start", "timing_anomaly"],
        default="start_to_stop",
        help="MitM saldırı senaryosu"
    )
    parser.add_argument(
        "--csms-url",
        type=str,
        default="ws://localhost:9000",
        help="CSMS WebSocket URL"
    )
    parser.add_argument(
        "--ocpp-rate", type=int, default=20, help="OCPP mesaj rate"
    )
    parser.add_argument(
        "--ocpp-duration", type=float, default=5.0, help="OCPP flooding süresi"
    )
    parser.add_argument(
        "--sampling-scenario",
        type=str,
        choices=["rate_drop", "peak_smoothing", "buffer_manipulation"],
        default="rate_drop",
        help="Sampling manipulation senaryosu"
    )
    parser.add_argument(
        "--sampling-duration", type=float, default=120.0, help="Sampling süresi"
    )
    # Senaryo #4 Parametreleri
    parser.add_argument(
        "--fuzz-intensity", type=int, default=10, help="Fuzzing yoğunluğu"
    )
    parser.add_argument(
        "--fail-open-duration", type=float, default=300.0, help="Fail-open süresi"
    )
    parser.add_argument(
        "--dos-rate", type=int, default=100, help="DoS istek oranı"
    )
    
    args = parser.parse_args()
    
    # Logger config
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>"
    )
    
    simulator = AttackSimulator(interface=args.interface)
    
    if not simulator.connect():
        logger.error(f"CAN interface bağlantısı başarısız: {args.interface}")
        return
    
    try:
        logger.info(f"Saldırı tipi: {args.attack}")
        logger.info("=" * 60)
        
        if args.attack == "injection":
            simulator.unauthorized_injection(count=5)
        elif args.attack == "flood":
            simulator.can_flood(duration=3.0, rate=200)
        elif args.attack == "replay":
            simulator.replay_attack(replay_count=5, delay=1.0)
        elif args.attack == "invalid_id":
            simulator.invalid_can_id(invalid_id=0x9FF, count=10)
        elif args.attack == "entropy":
            simulator.high_entropy_attack(count=15)
        elif args.attack == "mitm":
            simulator.mitm_ocpp_manipulation(scenario=args.mitm_scenario)
        elif args.attack == "ocpp_flood":
            simulator.ocpp_message_flooding(csms_url=args.csms_url, rate=args.ocpp_rate, duration=args.ocpp_duration)
        elif args.attack == "sampling":
            simulator.sampling_manipulation(scenario=args.sampling_scenario, duration=args.sampling_duration)
        elif args.attack == "fuzzing":
            simulator.ocpp_fuzzing_attack(target_url=args.csms_url, intensity=args.fuzz_intensity)
        elif args.attack == "fail_open":
            simulator.fail_open_attack(csms_url=args.csms_url, duration=args.fail_open_duration, dos_rate=args.dos_rate)
        elif args.attack == "combined":
            simulator.combined_attack()
        elif args.attack == "all":
            # Tüm saldırılar sırayla...
            simulator.unauthorized_injection(count=3)
            time.sleep(2)
            simulator.invalid_can_id(count=3)
            time.sleep(2)
            simulator.replay_attack(replay_count=3)
            time.sleep(2)
            simulator.high_entropy_attack(count=5)
            time.sleep(2)
            simulator.mitm_ocpp_manipulation(scenario="timing_anomaly")
            time.sleep(2)
            simulator.ocpp_fuzzing_attack(target_url=args.csms_url, intensity=5)
            
    except KeyboardInterrupt:
        logger.warning("\n⚠ Saldırı durduruldu (Ctrl+C)")
    
    finally:
        simulator.disconnect()
        logger.info("Simulator kapatıldı")


if __name__ == "__main__":
    main()