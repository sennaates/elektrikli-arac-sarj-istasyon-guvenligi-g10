"""
CAN-Bus simülatörü - vcan0 üzerinde çalışır
"""

import can
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import struct

logger = logging.getLogger(__name__)


@dataclass
class CANMessage:
    """CAN mesaj veri yapısı"""
    can_id: int
    data: bytes
    timestamp: datetime
    dlc: int = 8  # Data Length Code (CAN standard: 0-8 bytes)
    
    def __post_init__(self):
        if len(self.data) > 8:
            raise ValueError("CAN data cannot exceed 8 bytes")
        self.dlc = len(self.data)


class CANBusSimulator:
    """
    Sanal CAN bus simülatörü
    
    vcan0 arayüzü üzerinde CAN mesajları gönderir ve alır.
    """
    
    def __init__(self, channel: str = 'vcan0', bitrate: int = 500000):
        """
        Args:
            channel: CAN arayüz adı (örn: vcan0, can0)
            bitrate: CAN bitrate (500000 = 500 kbps, standard rate)
        """
        self.channel = channel
        self.bitrate = bitrate
        self.bus: Optional[can.BusABC] = None
        self.callbacks: List[Callable[[CANMessage], None]] = []
        self.messages_log: List[CANMessage] = []
        
    def start(self):
        """CAN bus'ı başlat"""
        try:
            self.bus = can.interface.Bus(channel=self.channel, 
                                        interface='socketcan',
                                        bitrate=self.bitrate)
            logger.info(f"✅ CAN bus başlatıldı: {self.channel} @ {self.bitrate} bps")
        except (OSError, AttributeError) as e:
            # macOS'ta CAN bus desteği yok, mock mode'a geç
            logger.warning(f"⚠️  CAN bus başlatılamadı (mock mode): {e}")
            logger.warning(f"⚠️  Mock CAN bus modunda çalışılıyor - mesajlar simüle edilecek")
            self.bus = None  # Mock mode
            # Mock mode'da da çalışmaya devam et
    
    def stop(self):
        """CAN bus'ı durdur"""
        if self.bus:
            self.bus.shutdown()
            logger.info("🔒 CAN bus durduruldu")
    
    def send_message(self, can_id: int, data: bytes) -> bool:
        """
        CAN mesajı gönder
        
        Args:
            can_id: CAN identifier (11-bit veya 29-bit)
            data: Mesaj verisi (maks 8 byte)
            
        Returns:
            bool: Gönderim başarılı mı?
        """
        if len(data) > 8:
            logger.error(f"❌ CAN data çok uzun: {len(data)} byte")
            return False
        
        # Mock mode: bus None ise simüle et
        if not self.bus:
            can_msg = CANMessage(can_id=can_id, data=data, timestamp=datetime.now())
            self.messages_log.append(can_msg)
            logger.debug(f"📤 CAN TX (MOCK): ID={hex(can_id)}, Data={data.hex()}")
            return True
        
        try:
            msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
            self.bus.send(msg)
            
            can_msg = CANMessage(can_id=can_id, data=data, timestamp=datetime.now())
            self.messages_log.append(can_msg)
            
            logger.debug(f"📤 CAN TX: ID={hex(can_id)}, Data={data.hex()}")
            return True
            
        except Exception as e:
            logger.error(f"❌ CAN mesaj gönderilemedi: {e}")
            return False
    
    def add_listener(self, callback: Callable[[CANMessage], None], 
                     can_id_filter: Optional[int] = None):
        """
        CAN mesaj dinleyicisi ekle
        
        Args:
            callback: Mesaj alındığında çağrılacak fonksiyon
            can_id_filter: Sadece belirli CAN ID'leri için dinle (None = hepsi)
        """
        def filtered_callback(can_msg: CANMessage):
            if can_id_filter is None or can_msg.can_id == can_id_filter:
                callback(can_msg)
        
        self.callbacks.append(filtered_callback)
        logger.debug(f"👂 CAN listener eklendi (filter: {can_id_filter})")
    
    def start_listening(self):
        """CAN mesajlarını dinlemeye başla"""
        # Mock mode: bus None ise dinleme yapma (sadece log tut)
        if not self.bus:
            logger.debug("👂 CAN dinleme (mock mode) - mesajlar log'da tutulacak")
            return
        
        logger.info("👂 CAN dinleme başlatıldı")
        
        try:
            while True:
                msg = self.bus.recv(timeout=1.0)
                if msg:
                    can_msg = CANMessage(
                        can_id=msg.arbitration_id,
                        data=msg.data,
                        timestamp=datetime.now(),
                        dlc=msg.dlc
                    )
                    
                    # Tüm listener'ları çağır
                    for callback in self.callbacks:
                        try:
                            callback(can_msg)
                        except Exception as e:
                            logger.error(f"❌ Listener hatası: {e}")
                    
                    logger.debug(f"📥 CAN RX: ID={hex(can_msg.can_id)}, Data={can_msg.data.hex()}")
                    
        except KeyboardInterrupt:
            logger.info("⏹️  CAN dinleme durduruldu")
        except Exception as e:
            logger.debug(f"CAN dinleme sonlandırıldı: {e}")
    
    def get_stats(self) -> Dict:
        """İstatistikleri döndür"""
        stats = {
            'total_messages': len(self.messages_log),
            'sent_messages': sum(1 for _ in self.messages_log),
            'listeners': len(self.callbacks)
        }
        
        # CAN ID dağılımı
        id_counts = {}
        for msg in self.messages_log:
            id_counts[msg.can_id] = id_counts.get(msg.can_id, 0) + 1
        stats['id_distribution'] = id_counts
        
        return stats
    
    def clear_log(self):
        """Mesaj logunu temizle"""
        self.messages_log.clear()
        logger.info("🧹 CAN log temizlendi")


def pack_can_payload(connector_id: int, energy: int, voltage: int, current: int) -> bytes:
    """
    MeterValues için CAN payload paketle
    
    Args:
        connector_id: Bağlayıcı ID (1 byte)
        energy: Enerji (Wh) (2 bytes)
        voltage: Voltaj (V) (2 bytes)
        current: Akım (mA) (2 bytes)
        
    Returns:
        8 byte CAN payload
    """
    return struct.pack('BHHH', connector_id, energy, voltage, current)


def unpack_can_payload(data: bytes) -> Dict:
    """
    CAN payload'ı unpack et
    
    Returns:
        Dict with unpacked values
    """
    if len(data) < 7:
        raise ValueError("Payload en az 7 byte olmalı")
    
    connector_id, energy, voltage, current = struct.unpack('BHHH', data[:7])
    
    return {
        'connector_id': connector_id,
        'energy': energy,  # Wh
        'voltage': voltage,  # V
        'current': current  # mA
    }

