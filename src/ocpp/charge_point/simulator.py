"""
Charge Point (CP) Simülatörü

OCPP protokolü üzerinden CSMS ile iletişim kuran şarj istasyonu simülatörü
"""

import asyncio
import logging
import websockets
from typing import Optional, Dict, Any
from datetime import datetime
import json
import sys
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.bridge.gateway import OCPPCANGateway
from src.can_bus.can_simulator import CANBusSimulator
from src.security.tls_config import TLSConfigManager

logger = logging.getLogger(__name__)


class ChargePointSimulator:
    """
    Charge Point simülatörü
    
    OCPP üzerinden CSMS'e bağlanır ve CAN bus üzerinden charger kontrolünü simüle eder
    """
    
    def __init__(self, 
                 cp_id: str = "CP001",
                 scenario: str = 'plain_ws',
                 csms_url: str = "ws://localhost:9000/charge_point/cp001"):
        """
        Args:
            cp_id: Charge Point ID
            scenario: Güvenlik senaryosu (plain_ws, weak_tls, strong_tls)
            csms_url: CSMS WebSocket URL
        """
        self.cp_id = cp_id
        self.scenario = scenario
        self.csms_url = csms_url
        
        # Components
        self.can_bus = CANBusSimulator()
        self.gateway = OCPPCANGateway(self.can_bus)
        self.tls_config = TLSConfigManager()
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        
        # State
        self.connected = False
        self.transaction_id: Optional[int] = None
        self.connector_status = {
            1: 'Available',
            2: 'Available'
        }
        
        logger.info(f"🔌 CP Simülatörü başlatıldı: {cp_id}")
    
    async def start(self):
        """CP'yi başlat"""
        # CAN bus başlat
        self.can_bus.start()
        self.gateway.setup_listeners()
        
        # CAN listener thread başlat
        import threading
        can_thread = threading.Thread(target=self._can_listener_thread, daemon=True)
        can_thread.start()
        
        # CSMS'e bağlan
        await self.connect_to_csms()
    
    def _can_listener_thread(self):
        """CAN dinleme thread'i"""
        try:
            self.can_bus.start_listening()
        except Exception as e:
            logger.debug(f"CAN listener thread sonlandırıldı: {e}")
    
    async def connect_to_csms(self):
        """CSMS'e bağlan"""
        # TLS context al
        ssl_context = self.tls_config.get_client_context(self.scenario)
        
        # URL'den scheme'u çıkart
        ws_url = self.csms_url.replace('ws://', '').replace('wss://', '')
        scheme = 'wss' if ssl_context else 'ws'
        full_url = f"{scheme}://{ws_url}"
        
        logger.info(f"🔗 CSMS'e bağlanılıyor: {full_url}")
        
        try:
            async with websockets.connect(
                full_url,
                ssl=ssl_context,
                ping_interval=None
            ) as websocket:
                self.websocket = websocket
                self.connected = True
                logger.info("✅ CSMS bağlantısı kuruldu")
                
                # BootNotification gönder
                await self.send_boot_notification()
                
                # Mesajları dinle
                await self.listen_messages()
                
        except Exception as e:
            logger.error(f"❌ CSMS bağlantı hatası: {e}")
            self.connected = False
    
    async def send_boot_notification(self):
        """BootNotification mesajı gönder"""
        boot_msg = {
            'messageTypeId': 2,  # CALL
            'uniqueId': f"boot_{self.cp_id}_{int(datetime.now().timestamp())}",
            'action': 'BootNotification',
            'payload': {
                'chargePointVendor': 'BSG Simulator',
                'chargePointModel': 'CP-SIM-001',
                'firmwareVersion': '1.0.0'
            }
        }
        
        await self.send_message(boot_msg)
        logger.info("📤 BootNotification gönderildi")
    
    async def send_message(self, message: Dict[str, Any]):
        """OCPP mesajı gönder"""
        if self.websocket and self.connected:
            try:
                json_msg = json.dumps(message)
                await self.websocket.send(json_msg)
                logger.debug(f"📤 OCPP mesajı gönderildi: {message.get('action')}")
            except Exception as e:
                logger.error(f"❌ Mesaj gönderilemedi: {e}")
    
    async def listen_messages(self):
        """CSMS'den gelen mesajları dinle"""
        if not self.websocket:
            return
        
        try:
            async for message in self.websocket:
                msg_data = json.loads(message)
                await self.handle_message(msg_data)
                
        except websockets.exceptions.ConnectionClosed:
            logger.warning("⚠️  CSMS bağlantısı kapandı")
            self.connected = False
        except Exception as e:
            logger.error(f"❌ Mesaj dinleme hatası: {e}")
            self.connected = False
    
    async def handle_message(self, message: Dict[str, Any]):
        """CSMS'den gelen mesajı handle et"""
        action = message.get('action')
        
        if not action:
            logger.warning("⚠️  Action bilgisi yok")
            return
        
        logger.info(f"📥 OCPP mesajı alındı: {action}")
        
        # RemoteStartTransaction
        if action == 'RemoteStartTransaction':
            await self.handle_remote_start(message.get('payload', {}))
        
        # RemoteStopTransaction
        elif action == 'RemoteStopTransaction':
            await self.handle_remote_stop(message.get('payload', {}))
        
        # SetChargingProfile
        elif action == 'SetChargingProfile':
            await self.handle_set_charging_profile(message.get('payload', {}))
        
        else:
            logger.warning(f"⚠️  Bilinmeyen action: {action}")
    
    async def handle_remote_start(self, payload: Dict[str, Any]):
        """RemoteStartTransaction handle et"""
        connector_id = payload.get('connectorId', 1)
        
        # CAN'a komut gönder (gateway üzerinden)
        success = self.gateway.ocpp_message_to_can('RemoteStartTransaction', payload)
        
        if success:
            self.transaction_id = int(datetime.now().timestamp())
            self.connector_status[connector_id] = 'Charging'
            
            # CSMS'e yanıt gönder
            response = {
                'messageTypeId': 3,  # CALLRESULT
                'uniqueId': payload.get('uniqueId'),
                'payload': {
                    'status': 'Accepted',
                    'transactionId': self.transaction_id
                }
            }
            await self.send_message(response)
            logger.info(f"✅ Şarj başlatıldı: Connector {connector_id}")
        
        else:
            response = {
                'messageTypeId': 4,  # CALLERROR
                'uniqueId': payload.get('uniqueId'),
                'payload': {
                    'errorCode': 'InternalError',
                    'errorDescription': 'CAN communication failed'
                }
            }
            await self.send_message(response)
            logger.error("❌ Şarj başlatılamadı: CAN hatası")
    
    async def handle_remote_stop(self, payload: Dict[str, Any]):
        """RemoteStopTransaction handle et"""
        tx_id = payload.get('transactionId')
        
        # CAN'a komut gönder
        success = self.gateway.ocpp_message_to_can('RemoteStopTransaction', payload)
        
        if success:
            self.transaction_id = None
            
            # CSMS'e yanıt gönder
            response = {
                'messageTypeId': 3,  # CALLRESULT
                'uniqueId': payload.get('uniqueId'),
                'payload': {
                    'status': 'Accepted'
                }
            }
            await self.send_message(response)
            logger.info(f"✅ Şarj durduruldu: Transaction {tx_id}")
        else:
            logger.error("❌ Şarj durdurulamadı")
    
    async def handle_set_charging_profile(self, payload: Dict[str, Any]):
        """SetChargingProfile handle et"""
        # CAN'a gönder
        success = self.gateway.ocpp_message_to_can('SetChargingProfile', payload)
        
        response = {
            'messageTypeId': 3,
            'uniqueId': payload.get('uniqueId'),
            'payload': {
                'status': 'Accepted' if success else 'Rejected'
            }
        }
        await self.send_message(response)
    
    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri döndür"""
        return {
            'connected': self.connected,
            'cp_id': self.cp_id,
            'scenario': self.scenario,
            'gateway_stats': self.gateway.get_stats()
        }
    
    async def stop(self):
        """CP'yi durdur"""
        self.connected = False
        
        # WebSocket'i kapat
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.debug(f"WebSocket kapatma hatası: {e}")
        
        # CAN bus'ı durdur
        try:
            self.can_bus.stop()
        except Exception as e:
            logger.debug(f"CAN bus kapatma hatası: {e}")
        
        # 0.1 saniye bekle
        await asyncio.sleep(0.1)
        
        logger.info("🔒 CP simülatörü durduruldu")


async def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Charge Point Simulator')
    parser.add_argument('--cp-id', default='CP001', help='Charge Point ID')
    parser.add_argument('--scenario', 
                       choices=['plain_ws', 'weak_tls', 'strong_tls'],
                       default='plain_ws',
                       help='Güvenlik senaryosu')
    parser.add_argument('--csms-url', 
                       default='ws://localhost:9000/charge_point/cp001',
                       help='CSMS WebSocket URL')
    parser.add_argument('--log-level', default='INFO', help='Log seviyesi')
    
    args = parser.parse_args()
    
    # Logging yapılandır
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Simülatörü başlat
    cp = ChargePointSimulator(
        cp_id=args.cp_id,
        scenario=args.scenario,
        csms_url=args.csms_url
    )
    
    try:
        await cp.start()
        # Keep running
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("⏹️  Simülatör durduruluyor...")
        await cp.stop()


if __name__ == '__main__':
    asyncio.run(main())

