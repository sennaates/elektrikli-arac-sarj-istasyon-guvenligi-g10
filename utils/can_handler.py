"""
CAN-Bus Handler Modülü
OCPP komutlarını CAN frame'lerine çevirir ve vcan0 üzerinde iletişim kurar.
"""
import can
import time
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from loguru import logger


@dataclass
class CANFrame:
    """CAN frame veri yapısı"""
    can_id: int
    data: List[int]
    dlc: int
    timestamp: float
    is_extended: bool = False
    is_error: bool = False
    
    def to_message(self) -> can.Message:
        """python-can Message objesine çevir"""
        return can.Message(
            arbitration_id=self.can_id,
            data=self.data,
            is_extended_id=self.is_extended,
            is_error_frame=self.is_error
        )
    
    @classmethod
    def from_message(cls, msg: can.Message) -> 'CANFrame':
        """python-can Message'dan CANFrame oluştur"""
        return cls(
            can_id=msg.arbitration_id,
            data=list(msg.data),
            dlc=msg.dlc,
            timestamp=msg.timestamp,
            is_extended=msg.is_extended_id,
            is_error=msg.is_error_frame
        )
    
    def to_dict(self) -> Dict:
        """Dictionary formatına çevir"""
        return {
            "can_id": hex(self.can_id),
            "data": [hex(b) for b in self.data],
            "dlc": self.dlc,
            "timestamp": self.timestamp,
            "is_extended": self.is_extended
        }


class OCPPtoCANMapper:
    """
    OCPP komutlarını CAN-Bus frame'lerine map eder.
    
    Mapping Tablosu (Eğitim Amaçlı):
    - RemoteStartTransaction → CAN ID 0x200
    - RemoteStopTransaction  → CAN ID 0x201
    - SetChargingProfile     → CAN ID 0x210
    - MeterValues            → CAN ID 0x300
    - UnlockConnector        → CAN ID 0x202
    """
    
    # OCPP Action → CAN ID mapping
    ACTION_TO_CAN_ID = {
        "RemoteStartTransaction": 0x200,
        "RemoteStopTransaction": 0x201,
        "SetChargingProfile": 0x210,
        "UnlockConnector": 0x202,
        "Reset": 0x220,
        "ChangeConfiguration": 0x230,
        "GetConfiguration": 0x231,
        "TriggerMessage": 0x240,
    }
    
    # CAN ID → OCPP Action mapping (reverse)
    CAN_ID_TO_ACTION = {v: k for k, v in ACTION_TO_CAN_ID.items()}
    
    @classmethod
    def ocpp_to_can(cls, action: str, payload: Dict) -> Optional[CANFrame]:
        """
        OCPP komutunu CAN frame'e çevir
        
        Args:
            action: OCPP action (örn. "RemoteStartTransaction")
            payload: OCPP payload dict
        
        Returns:
            CANFrame veya None
        """
        can_id = cls.ACTION_TO_CAN_ID.get(action)
        if not can_id:
            logger.warning(f"Bilinmeyen OCPP action: {action}")
            return None
        
        # Action'a göre payload'u CAN data'ya çevir
        if action == "RemoteStartTransaction":
            connector_id = payload.get("connector_id", 1)
            id_tag_hash = hash(payload.get("id_tag", "")) & 0xFFFF
            data = [
                0x01,  # START command
                connector_id,
                (id_tag_hash >> 8) & 0xFF,
                id_tag_hash & 0xFF,
                0x00, 0x00, 0x00, 0x00
            ]
        
        elif action == "RemoteStopTransaction":
            transaction_id = payload.get("transaction_id", 0)
            data = [
                0x02,  # STOP command
                (transaction_id >> 24) & 0xFF,
                (transaction_id >> 16) & 0xFF,
                (transaction_id >> 8) & 0xFF,
                transaction_id & 0xFF,
                0x00, 0x00, 0x00
            ]
        
        elif action == "SetChargingProfile":
            profile_id = payload.get("profile_id", 0)
            max_current = int(payload.get("max_current", 32))  # Ampere
            data = [
                0x03,  # PROFILE command
                profile_id & 0xFF,
                max_current,
                0x00, 0x00, 0x00, 0x00, 0x00
            ]
        
        elif action == "UnlockConnector":
            connector_id = payload.get("connector_id", 1)
            data = [
                0x04,  # UNLOCK command
                connector_id,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00
            ]
        
        elif action == "Reset":
            reset_type = 1 if payload.get("type") == "Hard" else 0
            data = [
                0x05,  # RESET command
                reset_type,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00
            ]
        
        else:
            # Generic mapping
            data = [0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        
        return CANFrame(
            can_id=can_id,
            data=data,
            dlc=len(data),
            timestamp=time.time()
        )
    
    @classmethod
    def can_to_ocpp(cls, frame: CANFrame) -> Optional[Tuple[str, Dict]]:
        """
        CAN frame'i OCPP formatına çevir (ters mapping)
        
        Returns:
            (action, payload) tuple veya None
        """
        action = cls.CAN_ID_TO_ACTION.get(frame.can_id)
        if not action:
            return None
        
        # CAN data'dan payload çıkar
        if frame.can_id == 0x200:  # RemoteStartTransaction
            payload = {
                "connector_id": frame.data[1] if len(frame.data) > 1 else 1,
                "id_tag": f"TAG_{frame.data[2]:02X}{frame.data[3]:02X}"
            }
        
        elif frame.can_id == 0x201:  # RemoteStopTransaction
            transaction_id = (frame.data[1] << 24) | (frame.data[2] << 16) | \
                           (frame.data[3] << 8) | frame.data[4]
            payload = {"transaction_id": transaction_id}
        
        else:
            payload = {"raw_data": frame.data}
        
        return action, payload


class CANBusHandler:
    """CAN-Bus iletişim yöneticisi"""
    
    def __init__(self, interface: str = "vcan0", bitrate: int = 500000):
        self.interface = interface
        self.bitrate = bitrate
        self.bus: Optional[can.Bus] = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """CAN bus'a bağlan"""
        try:
            self.bus = can.Bus(
                interface='socketcan',
                channel=self.interface,
                bitrate=self.bitrate
            )
            self.is_connected = True
            logger.info(f"✓ CAN Bus'a bağlanıldı: {self.interface}")
            return True
        except Exception as e:
            logger.error(f"✗ CAN Bus bağlantı hatası: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> None:
        """CAN bus bağlantısını kes"""
        if self.bus:
            self.bus.shutdown()
            self.is_connected = False
            logger.info("CAN Bus bağlantısı kapatıldı")
    
    def send_frame(self, frame: CANFrame) -> bool:
        """CAN frame gönder"""
        if not self.is_connected:
            logger.error("CAN Bus bağlı değil!")
            return False
        
        try:
            msg = frame.to_message()
            self.bus.send(msg)
            logger.debug(f"CAN Frame gönderildi: ID={hex(frame.can_id)}, Data={[hex(b) for b in frame.data]}")
            return True
        except Exception as e:
            logger.error(f"CAN frame gönderme hatası: {e}")
            return False
    
    def receive_frame(self, timeout: float = 1.0) -> Optional[CANFrame]:
        """CAN frame al"""
        if not self.is_connected:
            return None
        
        try:
            msg = self.bus.recv(timeout=timeout)
            if msg:
                frame = CANFrame.from_message(msg)
                logger.debug(f"CAN Frame alındı: ID={hex(frame.can_id)}")
                return frame
        except Exception as e:
            logger.error(f"CAN frame alma hatası: {e}")
        
        return None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


if __name__ == "__main__":
    # Test
    logger.info("CAN Handler modülü test ediliyor...")
    
    # OCPP → CAN mapping testi
    print("\n" + "="*50)
    print("OCPP → CAN MAPPING TEST")
    print("="*50)
    
    mapper = OCPPtoCANMapper()
    
    ocpp_action = "RemoteStartTransaction"
    ocpp_payload = {"connector_id": 1, "id_tag": "USER_ABC123"}
    
    frame = mapper.ocpp_to_can(ocpp_action, ocpp_payload)
    if frame:
        print(f"\nOCPP Action: {ocpp_action}")
        print(f"Payload: {ocpp_payload}")
        print(f"\n→ CAN Frame:")
        print(f"  ID: {hex(frame.can_id)}")
        print(f"  Data: {[hex(b) for b in frame.data]}")
        print(f"  DLC: {frame.dlc}")
    
    # CAN bus test (vcan0 kuruluysa çalışır)
    print("\n" + "="*50)
    print("CAN BUS CONNECTION TEST")
    print("="*50)
    
    handler = CANBusHandler(interface="vcan0")
    if handler.connect():
        print("✓ vcan0'a başarıyla bağlanıldı")
        handler.disconnect()
    else:
        print("✗ vcan0 bulunamadı. Kurmak için:")
        print("  sudo modprobe vcan")
        print("  sudo ip link add dev vcan0 type vcan")
        print("  sudo ip link set up vcan0")

