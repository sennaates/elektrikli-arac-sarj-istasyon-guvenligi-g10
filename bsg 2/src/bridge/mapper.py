"""
OCPP-CAN mesaj mapping tabloları ve dönüşüm mantığı
"""

from typing import Dict, Optional, Any
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CANMapping:
    """CAN mesaj mapping tanımı"""
    can_id: int
    name: str
    direction: str  # "ocpp_to_can" veya "can_to_ocpp"
    payload_format: str  # Struct format string


class OCPPCANMapper:
    """
    OCPP mesajlarını CAN frame'lere dönüştürür
    ve CAN frame'leri OCPP mesajlarına dönüştürür
    """
    
    # CAN ID tanımlamaları (eğitim amaçlı örnek ID'ler)
    CAN_ID_REMOTE_START = 0x200
    CAN_ID_REMOTE_STOP = 0x201
    CAN_ID_SET_CHARGING_PROFILE = 0x210
    CAN_ID_METER_VALUES = 0x300
    CAN_ID_CHARGE_STATUS = 0x301
    CAN_ID_ERROR = 0x9FF  # Anomali tespit için
    
    def __init__(self):
        self.mappings = self._initialize_mappings()
    
    def _initialize_mappings(self) -> Dict[str, CANMapping]:
        """Mapping tablolarını başlat"""
        return {
            'RemoteStartTransaction': CANMapping(
                can_id=self.CAN_ID_REMOTE_START,
                name='RemoteStartTransaction',
                direction='ocpp_to_can',
                payload_format='BB'  # [cp_id, connector_id]
            ),
            'RemoteStopTransaction': CANMapping(
                can_id=self.CAN_ID_REMOTE_STOP,
                name='RemoteStopTransaction',
                direction='ocpp_to_can',
                payload_format='IB'  # [transaction_id (4 byte), stop_cmd]
            ),
            'SetChargingProfile': CANMapping(
                can_id=self.CAN_ID_SET_CHARGING_PROFILE,
                name='SetChargingProfile',
                direction='ocpp_to_can',
                payload_format='HBB'  # [profile_id (2 byte), connector_id, max_current]
            ),
            'MeterValues': CANMapping(
                can_id=self.CAN_ID_METER_VALUES,
                name='MeterValues',
                direction='can_to_ocpp',
                payload_format='BHHH'  # [connector_id, energy, voltage, current]
            ),
            'ChargeStatus': CANMapping(
                can_id=self.CAN_ID_CHARGE_STATUS,
                name='ChargeStatus',
                direction='can_to_ocpp',
                payload_format='BB'  # [connector_id, status]
            )
        }
    
    def ocpp_to_can(self, ocpp_action: str, ocpp_data: Dict[str, Any]) -> Optional[bytes]:
        """
        OCPP mesajını CAN payload'a dönüştür
        
        Args:
            ocpp_action: OCPP action adı (örn: "RemoteStartTransaction")
            ocpp_data: OCPP mesaj verileri
            
        Returns:
            bytes: CAN payload veya None
        """
        if ocpp_action not in self.mappings:
            logger.warning(f"⚠️  Bilinmeyen OCPP action: {ocpp_action}")
            return None
        
        mapping = self.mappings[ocpp_action]
        
        if mapping.direction != 'ocpp_to_can':
            logger.error(f"❌ Yanlış yön mapping: {ocpp_action}")
            return None
        
        # Her action için özel dönüşüm
        if ocpp_action == 'RemoteStartTransaction':
            return self._remote_start_to_can(ocpp_data)
        elif ocpp_action == 'RemoteStopTransaction':
            return self._remote_stop_to_can(ocpp_data)
        elif ocpp_action == 'SetChargingProfile':
            return self._set_charging_profile_to_can(ocpp_data)
        else:
            logger.error(f"❌ Dönüşüm implementasyonu yok: {ocpp_action}")
            return None
    
    def can_to_ocpp(self, can_id: int, can_data: bytes) -> Optional[Dict[str, Any]]:
        """
        CAN frame'i OCPP mesajına dönüştür
        
        Args:
            can_id: CAN identifier
            can_data: CAN payload
            
        Returns:
            Dict: OCPP mesaj verisi veya None
        """
        # Mapping'i bul
        mapping = None
        for name, m in self.mappings.items():
            if m.can_id == can_id:
                mapping = m
                break
        
        if not mapping:
            logger.warning(f"⚠️  Bilinmeyen CAN ID: {hex(can_id)}")
            return None
        
        if mapping.direction != 'can_to_ocpp':
            logger.error(f"❌ Yanlış yön mapping: {can_id}")
            return None
        
        # Her CAN ID için özel dönüşüm
        if can_id == self.CAN_ID_METER_VALUES:
            return self._meter_values_to_ocpp(can_data)
        elif can_id == self.CAN_ID_CHARGE_STATUS:
            return self._charge_status_to_ocpp(can_data)
        else:
            logger.error(f"❌ Dönüşüm implementasyonu yok: {hex(can_id)}")
            return None
    
    def _remote_start_to_can(self, data: Dict[str, Any]) -> bytes:
        """RemoteStartTransaction → CAN"""
        connector_id = data.get('connectorId', 1)
        cp_id = data.get('cpId', 1)
        return bytes([cp_id, connector_id])
    
    def _remote_stop_to_can(self, data: Dict[str, Any]) -> bytes:
        """RemoteStopTransaction → CAN"""
        tx_id = data.get('transactionId', 0)
        stop_cmd = 1
        return tx_id.to_bytes(4, 'little') + bytes([stop_cmd])
    
    def _set_charging_profile_to_can(self, data: Dict[str, Any]) -> bytes:
        """SetChargingProfile → CAN"""
        profile_id = data.get('chargingProfileId', 1)
        connector_id = data.get('connectorId', 1)
        
        # chargingSchedule içindeki limit değerini al
        charging_schedule = data.get('chargingSchedule', {})
        schedule_periods = charging_schedule.get('chargingSchedulePeriod', [])
        
        if schedule_periods and len(schedule_periods) > 0:
            max_current = schedule_periods[0].get('limit', 32)  # Default 32A
        else:
            max_current = 32  # Default değer
        
        # max_current'ı byte'a çevir (0-255 arası)
        max_current_byte = min(255, max(0, int(max_current)))
        
        return profile_id.to_bytes(2, 'little') + bytes([connector_id, max_current_byte])
    
    def _meter_values_to_ocpp(self, can_data: bytes) -> Dict[str, Any]:
        """CAN MeterValues → OCPP"""
        import struct
        if len(can_data) < 7:
            raise ValueError("CAN data yetersiz")
        
        connector_id, energy, voltage, current = struct.unpack('BHHH', can_data[:7])
        
        return {
            'connectorId': connector_id,
            'meterValue': [{
                'sampledValue': [{
                    'value': str(energy),
                    'unit': 'Wh',
                    'context': 'Sample.Periodic'
                }, {
                    'value': str(voltage),
                    'unit': 'V',
                    'context': 'Sample.Periodic'
                }, {
                    'value': str(current),
                    'unit': 'mA',
                    'context': 'Sample.Periodic'
                }]
            }]
        }
    
    def _charge_status_to_ocpp(self, can_data: bytes) -> Dict[str, Any]:
        """CAN ChargeStatus → OCPP"""
        if len(can_data) < 2:
            raise ValueError("CAN data yetersiz")
        
        connector_id = can_data[0]
        status = can_data[1]  # 0=Available, 1=Charging, 2=Finishing, 3=Unavailable
        
        status_map = {
            0: 'Available',
            1: 'Charging',
            2: 'Finishing',
            3: 'Unavailable'
        }
        
        return {
            'connectorId': connector_id,
            'status': status_map.get(status, 'Unknown')
        }
    
    def get_can_id_for_action(self, action: str) -> Optional[int]:
        """OCPP action için CAN ID döndür"""
        if action in self.mappings:
            return self.mappings[action].can_id
        return None
    
    def is_anomaly_id(self, can_id: int) -> bool:
        """CAN ID anomali mi?"""
        # Bilinmeyen veya beklenmeyen ID'ler anomali
        known_ids = [m.can_id for m in self.mappings.values()]
        return can_id not in known_ids

