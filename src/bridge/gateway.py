"""
OCPP-CAN Gateway: OCPP ve CAN arasında köprü katmanı
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from src.can_bus.can_simulator import CANBusSimulator, CANMessage
from src.bridge.mapper import OCPPCANMapper

logger = logging.getLogger(__name__)


class OCPPCANGateway:
    """
    OCPP mesajlarını CAN frame'lere ve tersine dönüştüren gateway
    """
    
    def __init__(self, can_bus: CANBusSimulator):
        self.can_bus = can_bus
        self.mapper = OCPPCANMapper()
        self.message_counter = 0
        self.stats = {
            'ocpp_to_can': 0,
            'can_to_ocpp': 0,
            'errors': 0
        }
    
    def ocpp_message_to_can(self, action: str, data: Dict[str, Any]) -> bool:
        """
        OCPP mesajını al, CAN frame'e çevir ve gönder
        
        Args:
            action: OCPP action adı
            data: OCPP mesaj verileri
            
        Returns:
            bool: Başarılı mı?
        """
        try:
            # OCPP → CAN payload dönüşümü
            can_payload = self.mapper.ocpp_to_can(action, data)
            
            if not can_payload:
                logger.error(f"❌ OCPP dönüşümü başarısız: {action}")
                self.stats['errors'] += 1
                return False
            
            # CAN ID bul
            can_id = self.mapper.get_can_id_for_action(action)
            if not can_id:
                logger.error(f"❌ CAN ID bulunamadı: {action}")
                self.stats['errors'] += 1
                return False
            
            # CAN frame gönder
            success = self.can_bus.send_message(can_id, can_payload)
            
            if success:
                logger.info(f"✅ OCPP→CAN: {action} → ID={hex(can_id)}")
                self.stats['ocpp_to_can'] += 1
                self.message_counter += 1
            else:
                logger.error(f"❌ CAN mesaj gönderilemedi: {action}")
                self.stats['errors'] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Gateway hatası: {e}")
            self.stats['errors'] += 1
            return False
    
    def can_message_to_ocpp(self, can_msg: CANMessage) -> Optional[Dict[str, Any]]:
        """
        CAN frame'i al, OCPP mesajına çevir
        
        Args:
            can_msg: CAN mesajı
            
        Returns:
            Optional[Dict]: OCPP mesaj verisi veya None
        """
        try:
            # CAN → OCPP dönüşümü
            ocpp_data = self.mapper.can_to_ocpp(can_msg.can_id, can_msg.data)
            
            if ocpp_data:
                logger.info(f"✅ CAN→OCPP: ID={hex(can_msg.can_id)}")
                self.stats['can_to_ocpp'] += 1
                self.message_counter += 1
                return ocpp_data
            else:
                logger.warning(f"⚠️  OCPP dönüşümü başarısız: ID={hex(can_msg.can_id)}")
                self.stats['errors'] += 1
                return None
                
        except Exception as e:
            logger.error(f"❌ Gateway hatası: {e}")
            self.stats['errors'] += 1
            return None
    
    def handle_can_message(self, can_msg: CANMessage):
        """
        CAN mesajını handle et (callback için)
        
        Args:
            can_msg: CAN mesajı
        """
        # Gateway üzerinden OCPP'ye dönüştür
        ocpp_data = self.can_message_to_ocpp(can_msg)
        
        # Burada OCPP'ye gönderilebilir (gerçek uygulamada)
        if ocpp_data:
            logger.debug(f"📥 OCPP data hazır: {ocpp_data}")
    
    def setup_listeners(self):
        """CAN bus için listener'ları kur"""
        # Tüm CAN mesajlarını dinle
        self.can_bus.add_listener(self.handle_can_message)
        logger.info("👂 Gateway CAN listener'ları kuruldu")
    
    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri döndür"""
        return {
            **self.stats,
            'total_messages': self.message_counter,
            'can_stats': self.can_bus.get_stats()
        }
    
    def reset_stats(self):
        """İstatistikleri sıfırla"""
        self.stats = {
            'ocpp_to_can': 0,
            'can_to_ocpp': 0,
            'errors': 0
        }
        self.message_counter = 0
        self.can_bus.clear_log()
        logger.info("🧹 Gateway stats reset")

