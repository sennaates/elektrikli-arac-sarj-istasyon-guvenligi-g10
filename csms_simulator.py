"""
Basit CSMS Simülatörü - Test İçin
OCPP 1.6 WebSocket sunucusu simüle eder.
"""
import asyncio
import websockets
import json
import requests
from datetime import datetime
from loguru import logger

# Dashboard API URL
API_URL = "http://localhost:8000"


class SimpleCSMS:
    """Basit CSMS simülatörü"""
    
    def __init__(self, host="0.0.0.0", port=9000, auto_test: bool = False):
        self.host = host
        self.port = port
        self.connected_chargers = {}
        self.auto_test = auto_test
        self.test_task = None
        self.transactions = []
        self.transaction_counter = 0
    
    def update_dashboard(self):
        """Dashboard API'sine BSG verilerini gönder"""
        try:
            bsg_data = {
                "charge_points": [
                    {
                        "charge_point_id": cp_id,
                        "connected": True,
                        "status": "Available",
                        "last_heartbeat": datetime.utcnow().isoformat()
                    }
                    for cp_id in self.connected_chargers.keys()
                ],
                "transactions": self.transactions,
                "statistics": {
                    "connected_charge_points": len(self.connected_chargers),
                    "total_transactions": len(self.transactions),
                    "active_transactions": len([t for t in self.transactions if t.get("active", False)]),
                    "inactive_transactions": len([t for t in self.transactions if not t.get("active", False)])
                }
            }
            requests.post(f"{API_URL}/api/bsg/register", json=bsg_data, timeout=2)
            logger.debug(f"📊 Dashboard güncellendi: {len(self.connected_chargers)} CP bağlı")
        except Exception as e:
            logger.debug(f"Dashboard güncellenemedi: {e}")
    
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
                            # Charge Point ID'yi al (chargePointVendor veya chargePointModel'den)
                            charger_id = payload.get("chargePointVendor", "Unknown")
                            # Eğer CP_001 gibi bir ID varsa onu kullan
                            if "CP_" in str(payload.get("chargePointModel", "")):
                                charger_id = payload.get("chargePointModel", charger_id)
                            
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
                            
                            # Dashboard'ı güncelle
                            self.update_dashboard()
                            
                            # Otomatik test modu aktifse test komutlarını gönder
                            if self.auto_test:
                                logger.info("🧪 Otomatik test modu aktif, test komutları gönderilecek...")
                                self.test_task = asyncio.create_task(
                                    self.auto_send_test_commands(charger_id)
                                )
                        
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
                        
                        elif action == "StartTransaction":
                            # Transaction başlat
                            self.transaction_counter += 1
                            tx = {
                                "transaction_id": self.transaction_counter,
                                "charge_point_id": charger_id,
                                "connector_id": payload.get("connectorId", 1),
                                "id_tag": payload.get("idTag", "UNKNOWN"),
                                "start_time": datetime.utcnow().isoformat(),
                                "active": True
                            }
                            self.transactions.append(tx)
                            self.update_dashboard()
                            
                            response = [
                                3,  # CALLRESULT
                                message_id,
                                {
                                    "transactionId": self.transaction_counter,
                                    "idTagInfo": {"status": "Accepted"}
                                }
                            ]
                            logger.success(f"✓ Transaction başlatıldı: #{self.transaction_counter}")
                        
                        elif action == "StopTransaction":
                            # Transaction durdur
                            tx_id = payload.get("transactionId")
                            for tx in self.transactions:
                                if tx.get("transaction_id") == tx_id:
                                    tx["active"] = False
                                    tx["stop_time"] = datetime.utcnow().isoformat()
                            self.update_dashboard()
                            
                            response = [
                                3,  # CALLRESULT
                                message_id,
                                {"idTagInfo": {"status": "Accepted"}}
                            ]
                            logger.success(f"✓ Transaction durduruldu: #{tx_id}")
                        
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
                self.update_dashboard()
                logger.info(f"📊 Dashboard güncellendi: {charger_id} ayrıldı")
    
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
    
    async def auto_send_test_commands(self, charger_id: str):
        """Test için otomatik komut gönder"""
        await asyncio.sleep(5)  # Bridge'in tam bağlanmasını bekle
        
        if charger_id not in self.connected_chargers:
            logger.warning("Şarj istasyonu bağlantısı kayboldu")
            return
        
        logger.info("="*60)
        logger.info("🧪 OTOMATIK TEST KOMUTLARI BAŞLATILIYOR")
        logger.info("="*60)
        
        # Senaryo #1: Timing anomaly
        logger.info("\n📋 Senaryo #1: Timing Anomaly Test")
        logger.info("📤 RemoteStartTransaction gönderiliyor...")
        await self.send_remote_command(
            charger_id,
            "RemoteStartTransaction",
            {"connectorId": 1, "idTag": "TEST_001"}
        )
        
        await asyncio.sleep(1.0)  # 1 saniye bekle (K1 kuralı tetiklenmeli)
        
        logger.info("📤 RemoteStopTransaction gönderiliyor (1 saniye sonra - timing anomaly)...")
        await self.send_remote_command(
            charger_id,
            "RemoteStopTransaction",
            {"transactionId": 1}
        )
        
        await asyncio.sleep(3)
        
        # Senaryo #2: OCPP flooding
        logger.info("\n📋 Senaryo #2: OCPP Message Flooding Test")
        logger.info("📤 20 Heartbeat mesajı gönderiliyor (20 mesaj/s, eşik: 5 mesaj/s)...")
        for i in range(20):
            await self.send_remote_command(
                charger_id,
                "Heartbeat",
                {}
            )
            await asyncio.sleep(0.05)  # 20 mesaj/saniye
        
        await asyncio.sleep(3)
        
        # Senaryo #3: MeterValues (sampling manipulation için)
        logger.info("\n📋 Senaryo #3: MeterValues Test (Sampling Manipulation)")
        logger.info("📤 Düşük frekanslı MeterValues gönderiliyor...")
        for i in range(3):
            await self.send_remote_command(
                charger_id,
                "MeterValues",
                {
                    "connectorId": 1,
                    "transactionId": 1,
                    "meterValue": [{
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "sampledValue": [{
                            "value": str(10.0 + (i * 0.1)),
                            "context": "Sample.Periodic",
                            "format": "Raw",
                            "measurand": "Energy.Active.Import.Register",
                            "unit": "kWh"
                        }]
                    }]
                }
            )
            await asyncio.sleep(60)  # Her 60 saniyede bir (düşük rate)
        
        logger.info("\n✅ Otomatik test komutları tamamlandı!")
        logger.info("="*60)
    
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
    import argparse
    
    parser = argparse.ArgumentParser(description="CSMS Simülatörü")
    parser.add_argument(
        "--auto-test",
        action="store_true",
        help="Otomatik test komutlarını gönder (Senaryo #1, #2, #3)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9000,
        help="CSMS portu (default: 9000)"
    )
    args = parser.parse_args()
    
    # Logger config
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>"
    )
    
    csms = SimpleCSMS(host="0.0.0.0", port=args.port, auto_test=args.auto_test)
    
    if args.auto_test:
        logger.info("🧪 Otomatik test modu: AKTİF")
        logger.info("   Bridge bağlandığında test komutları otomatik gönderilecek")
    
    try:
        await csms.start()
    except KeyboardInterrupt:
        logger.warning("\n⚠ CSMS sunucusu durduruldu")


if __name__ == "__main__":
    asyncio.run(main())

