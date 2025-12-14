"""
Central System Management System (CSMS) Simülatörü

OCPP protokolü üzerinden Charge Point'ler ile iletişim kuran merkezi yönetim sistemi
"""

import asyncio
import logging
from typing import Dict, Any, Set, Optional
from datetime import datetime
import json
import sys
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.security.tls_config import TLSConfigManager

logger = logging.getLogger(__name__)


class CSMSimulator:
    """
    Central System Management System simülatörü
    
    Charge Point'lerin bağlandığı merkezi yönetim sistemi
    """
    
    def __init__(self,
                 host: str = 'localhost',
                 port: int = 9000,
                 scenario: str = 'plain_ws'):
        """
        Args:
            host: CSMS host adresi
            port: CSMS port numarası
            scenario: Güvenlik senaryosu
        """
        self.host = host
        self.port = port
        self.scenario = scenario
        
        # Components
        self.tls_config = TLSConfigManager()
        self.connected_cps: Dict[str, Dict[str, Any]] = {}
        
        # State
        self.running = False
        self.message_counter = 0
        self.server_started = None  # Server başladığını bildirmek için (start() içinde oluşturulacak)
        
        logger.info(f"🌐 CSMS simülatörü başlatıldı: {host}:{port}")
    
    async def start(self):
        """CSMS'i başlat"""
        import websockets
        
        # Event'i oluştur (event loop çalışıyor olmalı)
        self.server_started = asyncio.Event()
        
        # TLS context al
        ssl_context = self.tls_config.get_server_context(self.scenario)
        
        # WebSocket server başlat
        self.running = True
        
        logger.info(f"🚀 CSMS WebSocket server başlatılıyor: {self.scenario}")
        
        if ssl_context:
            scheme = 'wss'
        else:
            scheme = 'ws'
        
        logger.info(f"✅ CSMS hazır: {scheme}://{self.host}:{self.port}")
        
        # Server'ı başlat ve başladığını logla
        try:
            async with websockets.serve(
                self.handle_connection,
                self.host,
                self.port,
                ssl=ssl_context
            ) as server:
                logger.info(f"🌐 WebSocket server dinliyor: {self.host}:{self.port}")
                # Server başladığını bildir
                self.server_started.set()
                # Keep running
                await asyncio.Event().wait()
        except Exception as e:
            logger.error(f"❌ WebSocket server başlatılamadı: {e}", exc_info=True)
            self.server_started.set()  # Hata olsa bile event'i set et
            raise
    
    async def handle_connection(self, websocket, path: str):
        """Charge Point bağlantısını handle et"""
        cp_id = self._extract_cp_id_from_path(path)
        
        if not cp_id:
            # Path'den çıkarılamadıysa timestamp kullan
            cp_id = f"CP{int(datetime.now().timestamp())}"
        
        logger.info(f"🔗 Yeni CP bağlantısı: {cp_id} (path: {path})")
        
        self.connected_cps[cp_id] = {
            'ws': websocket,
            'connected_at': datetime.now(),
            'status': 'connected',
            'boot_complete': False
        }
        
        logger.info(f"✅ CP kaydedildi. Toplam bağlı CP: {len(self.connected_cps)}")
        
        try:
            # Mesajları dinle
            async for message in websocket:
                await self.handle_message(cp_id, message)
                
        except Exception as e:
            logger.error(f"❌ CP bağlantı hatası: {e}")
        finally:
            # Bağlantıyı temizle
            if cp_id in self.connected_cps:
                del self.connected_cps[cp_id]
            logger.info(f"📴 CP bağlantısı kapatıldı: {cp_id}")
    
    def _extract_cp_id_from_path(self, path: str) -> Optional[str]:
        """Path'den CP ID çıkar"""
        # Path format: /charge_point/{cp_id}
        parts = path.split('/')
        if len(parts) >= 3 and parts[1] == 'charge_point':
            return parts[2]
        return None
    
    async def handle_message(self, cp_id: str, raw_message: str):
        """Charge Point'den gelen mesajı handle et"""
        try:
            message = json.loads(raw_message)
            self.message_counter += 1
            
            message_type = message.get('messageTypeId')
            action = message.get('action')
            
            # CALLRESULT veya CALLERROR mesajlarında action olmaz (normal)
            if message_type in [3, 4]:  # CALLRESULT veya CALLERROR
                logger.debug(f"📥 Response mesajı alındı: {cp_id} - Type {message_type}")
                return
            
            # CALL mesajlarında action olmalı
            if not action:
                logger.warning(f"⚠️  CALL mesajında action yok. Mesaj: {raw_message[:200]}")
                logger.warning(f"⚠️  Message keys: {list(message.keys())}")
                return
            
            logger.info(f"📥 Mesaj alındı: {cp_id} - {action}")
            
            # BootNotification handle et
            if action == 'BootNotification':
                await self.handle_boot_notification(cp_id, message)
            
            # Diğer mesajlar için echo response gönder
            else:
                # Herhangi bir response için unique ID gönder
                response = {
                    'messageTypeId': 3,  # CALLRESULT
                    'uniqueId': message.get('uniqueId'),
                    'payload': {
                        'status': 'Accepted'
                    }
                }
                await self.send_to_cp(cp_id, response)
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse hatası: {e}, Raw: {raw_message[:200]}")
        except Exception as e:
            logger.error(f"❌ Mesaj handle hatası: {e}", exc_info=True)
    
    async def handle_boot_notification(self, cp_id: str, message: Dict[str, Any]):
        """BootNotification handle et"""
        response = {
            'messageTypeId': 3,  # CALLRESULT
            'uniqueId': message.get('uniqueId'),
            'payload': {
                'status': 'Accepted',
                'currentTime': datetime.now().isoformat(),
                'interval': 3600  # Heartbeat interval (saniye)
            }
        }
        
        await self.send_to_cp(cp_id, response)
        
        if cp_id in self.connected_cps:
            self.connected_cps[cp_id]['boot_complete'] = True
        
        logger.info(f"✅ BootNotification tamamlandı: {cp_id}")
    
    async def send_to_cp(self, cp_id: str, message: Dict[str, Any]):
        """Charge Point'e mesaj gönder"""
        if cp_id in self.connected_cps:
            ws = self.connected_cps[cp_id]['ws']
            try:
                json_msg = json.dumps(message)
                await ws.send(json_msg)
                logger.debug(f"📤 Mesaj gönderildi: {cp_id}")
                return True
            except Exception as e:
                logger.error(f"❌ Mesaj gönderilemedi: {e}")
        else:
            logger.error(f"❌ CP bulunamadı: {cp_id}")
        return False
    
    async def send_remote_start(self, cp_id: str, connector_id: int = 1):
        """RemoteStartTransaction gönder"""
        unique_id = f"remote_start_{datetime.now().timestamp()}"
        
        message = {
            'messageTypeId': 2,  # CALL
            'uniqueId': unique_id,
            'action': 'RemoteStartTransaction',
            'payload': {
                'connectorId': connector_id
            }
        }
        
        success = await self.send_to_cp(cp_id, message)
        if success:
            logger.info(f"📤 RemoteStartTransaction gönderildi: {cp_id}")
        return success
    
    async def send_remote_stop(self, cp_id: str, transaction_id: int):
        """RemoteStopTransaction gönder"""
        unique_id = f"remote_stop_{datetime.now().timestamp()}"
        
        message = {
            'messageTypeId': 2,  # CALL
            'uniqueId': unique_id,
            'action': 'RemoteStopTransaction',
            'payload': {
                'transactionId': transaction_id
            }
        }
        
        success = await self.send_to_cp(cp_id, message)
        if success:
            logger.info(f"📤 RemoteStopTransaction gönderildi: {cp_id}")
        return success
    
    async def send_set_charging_profile(self, cp_id: str, connector_id: int = 1, 
                                        charging_profile_id: int = 1, 
                                        max_current: int = 32):
        """
        SetChargingProfile gönder
        
        Args:
            cp_id: Charge Point ID
            connector_id: Connector ID
            charging_profile_id: Charging Profile ID
            max_current: Maximum current (A)
        """
        unique_id = f"set_profile_{datetime.now().timestamp()}"
        
        message = {
            'messageTypeId': 2,  # CALL
            'uniqueId': unique_id,
            'action': 'SetChargingProfile',
            'payload': {
                'connectorId': connector_id,
                'chargingProfileId': charging_profile_id,
                'chargingSchedule': {
                    'chargingRateUnit': 'A',
                    'chargingSchedulePeriod': [{
                        'startPeriod': 0,
                        'limit': max_current
                    }]
                }
            }
        }
        
        success = await self.send_to_cp(cp_id, message)
        if success:
            logger.info(f"📤 SetChargingProfile gönderildi: {cp_id} (max_current={max_current}A)")
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri döndür"""
        return {
            'running': self.running,
            'scenario': self.scenario,
            'connected_cps': len(self.connected_cps),
            'total_messages': self.message_counter,
            'cp_list': list(self.connected_cps.keys())
        }
    
    async def stop(self):
        """CSMS'i durdur"""
        self.running = False
        # Tüm bağlantıları kapat
        for cp_id, cp_data in list(self.connected_cps.items()):
            try:
                await cp_data['ws'].close()
            except Exception as e:
                logger.debug(f"Bağlantı kapatma hatası: {e}")
                pass
        self.connected_cps.clear()
        
        # 0.1 saniye bekle ve temizle
        await asyncio.sleep(0.1)
        
        logger.info("🔒 CSMS durduruldu")


async def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CSMS Simulator')
    parser.add_argument('--host', default='localhost', help='Host address')
    parser.add_argument('--port', type=int, default=9000, help='Port number')
    parser.add_argument('--scenario',
                       choices=['plain_ws', 'weak_tls', 'strong_tls'],
                       default='plain_ws',
                       help='Güvenlik senaryosu')
    parser.add_argument('--log-level', default='INFO', help='Log seviyesi')
    
    args = parser.parse_args()
    
    # Logging yapılandır
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Simülatörü başlat
    csms = CSMSimulator(
        host=args.host,
        port=args.port,
        scenario=args.scenario
    )
    
    try:
        # CSMS'i arka planda başlat
        start_task = asyncio.create_task(csms.start())
        
        # Biraz bekle, sonra otomatik RemoteStartTransaction gönder
        await asyncio.sleep(5)
        
        # Bağlı CP'lere RemoteStartTransaction gönder
        if csms.connected_cps:
            for cp_id in list(csms.connected_cps.keys()):
                logger.info(f"⏳ {cp_id} için RemoteStartTransaction gönderiliyor...")
                await csms.send_remote_start(cp_id, connector_id=1)
                await asyncio.sleep(2)
        
        # Forever
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("⏹️  Simülatör durduruluyor...")
        await csms.stop()


if __name__ == '__main__':
    asyncio.run(main())

