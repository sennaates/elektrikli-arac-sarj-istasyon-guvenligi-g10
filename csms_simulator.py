"""
Basit CSMS Simülatörü - Test İçin
OCPP 1.6 WebSocket sunucusu simüle eder.
"""
import asyncio
import websockets
import json
from datetime import datetime
from loguru import logger


class SimpleCSMS:
    """Basit CSMS simülatörü"""
    
    def __init__(self, host="0.0.0.0", port=9000):
        self.host = host
        self.port = port
        self.connected_chargers = {}
    
    async def handle_client(self, websocket, path):
        """Client bağlantısını handle et"""
        charger_id = None
        
        try:
            logger.info(f"Yeni bağlantı: {websocket.remote_address}")
            
            async for message in websocket:
                try:
                    # OCPP mesajını parse et
                    data = json.loads(message)
                    message_type = data[0]
                    message_id = data[1]
                    
                    if message_type == 2:  # CALL (request)
                        action = data[2]
                        payload = data[3]
                        
                        logger.info(f"📨 Gelen: {action}")
                        logger.debug(f"   Payload: {payload}")
                        
                        # Action'a göre yanıt üret
                        if action == "BootNotification":
                            charger_id = payload.get("chargePointVendor", "Unknown")
                            self.connected_chargers[charger_id] = websocket
                            
                            response = [
                                3,  # CALLRESULT
                                message_id,
                                {
                                    "status": "Accepted",
                                    "currentTime": datetime.utcnow().isoformat() + "Z",
                                    "interval": 60
                                }
                            ]
                            
                            logger.success(f"✓ {charger_id} kabul edildi")
                        
                        elif action == "Heartbeat":
                            response = [
                                3,  # CALLRESULT
                                message_id,
                                {
                                    "currentTime": datetime.utcnow().isoformat() + "Z"
                                }
                            ]
                        
                        elif action == "StatusNotification":
                            response = [
                                3,  # CALLRESULT
                                message_id,
                                {}
                            ]
                        
                        elif action == "MeterValues":
                            response = [
                                3,  # CALLRESULT
                                message_id,
                                {}
                            ]
                        
                        else:
                            # Generic response
                            response = [
                                3,  # CALLRESULT
                                message_id,
                                {"status": "Accepted"}
                            ]
                        
                        # Yanıtı gönder
                        await websocket.send(json.dumps(response))
                        logger.debug(f"📤 Yanıt gönderildi: {action}")
                    
                except json.JSONDecodeError:
                    logger.error("Geçersiz JSON mesajı")
                except Exception as e:
                    logger.error(f"Mesaj işleme hatası: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"Bağlantı kapatıldı: {charger_id or 'Unknown'}")
        except Exception as e:
            logger.error(f"Bağlantı hatası: {e}")
        finally:
            if charger_id and charger_id in self.connected_chargers:
                del self.connected_chargers[charger_id]
    
    async def send_remote_command(self, charger_id: str, action: str, payload: dict):
        """Şarj istasyonuna uzaktan komut gönder"""
        if charger_id not in self.connected_chargers:
            logger.error(f"Şarj istasyonu bulunamadı: {charger_id}")
            return
        
        websocket = self.connected_chargers[charger_id]
        
        message = [
            2,  # CALL
            f"remote_{action}_{int(asyncio.get_event_loop().time())}",
            action,
            payload
        ]
        
        try:
            await websocket.send(json.dumps(message))
            logger.info(f"📤 Uzaktan komut gönderildi: {action} → {charger_id}")
        except Exception as e:
            logger.error(f"Komut gönderme hatası: {e}")
    
    async def start(self):
        """CSMS sunucusunu başlat"""
        logger.info("="*60)
        logger.info("Basit CSMS Simülatörü Başlatılıyor")
        logger.info("="*60)
        
        async with websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            subprotocols=['ocpp1.6']
        ):
            logger.success(f"✓ CSMS sunucusu başlatıldı: ws://{self.host}:{self.port}/ocpp")
            logger.info("Şarj istasyonu bağlantıları bekleniyor...")
            logger.info("Ctrl+C ile durdurun")
            
            # Sonsuz döngü
            await asyncio.Future()


async def main():
    """Ana entry point"""
    # Logger config
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>"
    )
    
    csms = SimpleCSMS(host="0.0.0.0", port=9000)
    
    try:
        await csms.start()
    except KeyboardInterrupt:
        logger.warning("\n⚠ CSMS sunucusu durduruldu")


if __name__ == "__main__":
    asyncio.run(main())

