"""
Secure OCPP-to-CAN Bridge
OCPP komutlarını alır, CAN frame'lerine çevirir ve blockchain ile güvence altına alır.
"""
import asyncio
import time
import os
import json
from typing import Dict, Optional, Any
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    try:
        import requests
        AIOHTTP_AVAILABLE = False
        REQUESTS_AVAILABLE = True
    except ImportError:
        AIOHTTP_AVAILABLE = False
        REQUESTS_AVAILABLE = False
        logger.warning("aiohttp veya requests bulunamadı. API server entegrasyonu devre dışı.")

# OCPP
try:
    from ocpp.v16 import ChargePoint as cp
    from ocpp.v16 import call, call_result
    from ocpp.routing import on
    import websockets
    OCPP_AVAILABLE = True
except ImportError:
    OCPP_AVAILABLE = False
    logger.warning("ocpp kütüphanesi bulunamadı. OCPP özelliği devre dışı.")

# Internal modules
from utils.blockchain import Blockchain
from utils.can_handler import CANBusHandler, OCPPtoCANMapper
from utils.ids import RuleBasedIDS
from utils.ml_ids import MLBasedIDS, HybridIDS, SKLEARN_AVAILABLE


# Load environment variables
load_dotenv()


class SecureChargePoint(cp if OCPP_AVAILABLE else object):
    """
    Güvenli Şarj İstasyonu (Charge Point).
    OCPP mesajlarını alır, blockchain'e kaydeder, CAN-Bus'a çevirir ve IDS kontrolleri yapar.
    """
    
    def __init__(
        self,
        charge_point_id: str,
        connection,
        can_handler: CANBusHandler,
        blockchain: Blockchain,
        ids: HybridIDS,
        api_callback=None
    ):
        if OCPP_AVAILABLE:
            super().__init__(charge_point_id, connection)
        
        self.charge_point_id = charge_point_id
        self.connection = connection
        self.can_handler = can_handler
        self.blockchain = blockchain
        self.ids = ids
        self.api_callback = api_callback  # Dashboard'a veri gönderme callback
        
        self.mapper = OCPPtoCANMapper()
        
        # Transaction tracking
        self.active_transactions: Dict[int, Dict] = {}
        
        logger.info(f"SecureChargePoint başlatıldı: {charge_point_id}")
    
    async def send_boot_notification(self):
        """BootNotification gönder (OCPP başlangıç)"""
        if not OCPP_AVAILABLE:
            return
        
        request = call.BootNotificationPayload(
            charge_point_model="SecureBridge-v1",
            charge_point_vendor="UniversityProject"
        )
        
        logger.info("BootNotification gönderiliyor...")
        response = await self.call(request)
        
        if response.status == "Accepted":
            logger.info(f"✓ CSMS tarafından kabul edildi. Heartbeat: {response.interval}s")
            
            # Blockchain'e kaydet
            self.blockchain.add_block({
                "action": "BootNotification",
                "status": "Accepted",
                "interval": response.interval
            }, block_type="OCPP")
        
        return response
    
    async def send_heartbeat_loop(self, interval: int = 60):
        """Heartbeat döngüsü"""
        if not OCPP_AVAILABLE:
            return
        
        while True:
            await asyncio.sleep(interval)
            try:
                request = call.HeartbeatPayload()
                response = await self.call(request)
                logger.debug(f"Heartbeat yanıtı: {response.current_time}")
            except Exception as e:
                logger.error(f"Heartbeat hatası: {e}")
    
    @on('RemoteStartTransaction')
    async def on_remote_start_transaction(self, **kwargs):
        """CSMS'den RemoteStartTransaction komutu geldi"""
        connector_id = kwargs.get('connector_id', 1)
        id_tag = kwargs.get('id_tag', '')
        
        logger.info(f"🔌 RemoteStartTransaction alındı: connector={connector_id}, tag={id_tag}")
        
        # 1. OCPP mesajını blockchain'e kaydet
        self.blockchain.add_block({
            "action": "RemoteStartTransaction",
            "connector_id": connector_id,
            "id_tag": id_tag
        }, block_type="OCPP")
        
        # 2. IDS kontrolü (OCPP seviyesinde)
        alert = self.ids.rule_based_ids.check_ocpp_message(
            "RemoteStartTransaction",
            {"connector_id": connector_id, "id_tag": id_tag},
            time.time()
        )
        
        if alert and alert.severity in ["HIGH", "CRITICAL"]:
            logger.error(f"🚨 IDS ALERT: {alert.description}")
            self.blockchain.add_block(alert.to_dict(), block_type="ALERT")
            
            # Dashboard'a bildir
            if self.api_callback:
                await self.api_callback("alert", alert.to_dict())
            
            # Komutu reddet
            return call_result.RemoteStartTransactionPayload(status="Rejected")
        
        # 3. OCPP → CAN mapping
        can_frame = self.mapper.ocpp_to_can("RemoteStartTransaction", {
            "connector_id": connector_id,
            "id_tag": id_tag
        })
        
        if not can_frame:
            logger.error("CAN frame oluşturulamadı!")
            return call_result.RemoteStartTransactionPayload(status="Rejected")
        
        # 4. CAN frame'i yetkili olarak kaydet (IDS için)
        self.ids.rule_based_ids.register_authorized_can_frame(
            can_frame.can_id,
            can_frame.data
        )
        
        # 5. CAN-Bus'a gönder
        success = self.can_handler.send_frame(can_frame)
        
        # 6. CAN frame'i blockchain'e kaydet
        self.blockchain.add_block(can_frame.to_dict(), block_type="CAN")
        
        # 7. Transaction başlat
        transaction_id = int(time.time() * 1000) % 100000
        self.active_transactions[transaction_id] = {
            "connector_id": connector_id,
            "id_tag": id_tag,
            "start_time": time.time()
        }
        
        logger.info(f"✓ Transaction başlatıldı: #{transaction_id}")
        
        # Dashboard'a bildir
        if self.api_callback:
            await self.api_callback("ocpp_message", {
                "action": "RemoteStartTransaction",
                "status": "Accepted",
                "transaction_id": transaction_id
            })
            await self.api_callback("can_frame", can_frame.to_dict())
        
        return call_result.RemoteStartTransactionPayload(
            status="Accepted" if success else "Rejected"
        )
    
    @on('RemoteStopTransaction')
    async def on_remote_stop_transaction(self, transaction_id: int, **kwargs):
        """CSMS'den RemoteStopTransaction komutu geldi"""
        logger.info(f"🛑 RemoteStopTransaction alındı: transaction={transaction_id}")
        
        # 1. Blockchain'e kaydet
        self.blockchain.add_block({
            "action": "RemoteStopTransaction",
            "transaction_id": transaction_id
        }, block_type="OCPP")
        
        # 2. IDS kontrolü
        alert = self.ids.rule_based_ids.check_ocpp_message(
            "RemoteStopTransaction",
            {"transaction_id": transaction_id},
            time.time()
        )
        
        if alert and alert.severity in ["HIGH", "CRITICAL"]:
            logger.error(f"🚨 IDS ALERT: {alert.description}")
            self.blockchain.add_block(alert.to_dict(), block_type="ALERT")
            
            if self.api_callback:
                await self.api_callback("alert", alert.to_dict())
            
            return call_result.RemoteStopTransactionPayload(status="Rejected")
        
        # 3. OCPP → CAN
        can_frame = self.mapper.ocpp_to_can("RemoteStopTransaction", {
            "transaction_id": transaction_id
        })
        
        if can_frame:
            self.ids.rule_based_ids.register_authorized_can_frame(
                can_frame.can_id,
                can_frame.data
            )
            self.can_handler.send_frame(can_frame)
            self.blockchain.add_block(can_frame.to_dict(), block_type="CAN")
        
        # 4. Transaction'ı kapat
        if transaction_id in self.active_transactions:
            del self.active_transactions[transaction_id]
            logger.info(f"✓ Transaction kapatıldı: #{transaction_id}")
        
        # Dashboard'a bildir
        if self.api_callback:
            await self.api_callback("ocpp_message", {
                "action": "RemoteStopTransaction",
                "status": "Accepted",
                "transaction_id": transaction_id
            })
            if can_frame:
                await self.api_callback("can_frame", can_frame.to_dict())
        
        return call_result.RemoteStopTransactionPayload(status="Accepted")
    
    async def listen_can_bus(self):
        """
        CAN-Bus'ı dinle ve gelen frame'leri kontrol et.
        Yetkisiz injection tespiti için kritik.
        """
        logger.info("CAN-Bus dinleme başlatıldı...")
        
        while True:
            try:
                # CAN frame al (non-blocking)
                frame = self.can_handler.receive_frame(timeout=0.1)
                
                if frame:
                    logger.debug(f"CAN Frame alındı: ID={hex(frame.can_id)}")
                    
                    # IDS kontrolü (Hybrid: Rule + ML)
                    alert, ml_score = self.ids.check_can_frame(
                        frame.can_id,
                        frame.data,
                        frame.timestamp
                    )
                    
                    # Alert varsa blockchain'e kaydet
                    if alert:
                        logger.warning(f"⚠ IDS Alert: {alert.description}")
                        self.blockchain.add_block(alert.to_dict(), block_type="ALERT")
                        
                        # Dashboard'a bildir
                        if self.api_callback:
                            await self.api_callback("alert", alert.to_dict())
                    
                    # Her frame'i blockchain'e kaydet
                    self.blockchain.add_block({
                        **frame.to_dict(),
                        "ml_score": ml_score
                    }, block_type="CAN_RECEIVED")
                    
                    # Dashboard'a bildir
                    if self.api_callback:
                        await self.api_callback("can_frame", {
                            **frame.to_dict(),
                            "ml_score": ml_score,
                            "is_alert": alert is not None
                        })
            
            except Exception as e:
                logger.error(f"CAN dinleme hatası: {e}")
            
            await asyncio.sleep(0.01)  # 10ms delay


class SecureBridgeService:
    """
    Ana bridge servisi.
    OCPP client, CAN handler, blockchain ve IDS'i yönetir.
    """
    
    def __init__(self):
        # Config
        self.csms_url = os.getenv("CSMS_URL", "ws://localhost:9000/ocpp")
        self.charge_point_id = os.getenv("CHARGE_POINT_ID", "CP_001")
        self.can_interface = os.getenv("CAN_INTERFACE", "vcan0")
        
        # Components
        self.blockchain = Blockchain(
            enable_signature=os.getenv("ENABLE_DIGITAL_SIGNATURE", "true").lower() == "true"
        )
        
        self.can_handler = CANBusHandler(interface=self.can_interface)
        
        # IDS
        rule_ids = RuleBasedIDS()
        
        # ML-IDS (opsiyonel)
        ml_ids = None
        if SKLEARN_AVAILABLE and os.getenv("ENABLE_ML_IDS", "true").lower() == "true":
            ml_model_path = os.getenv("ML_MODEL_PATH")
            ml_ids = MLBasedIDS(
                model_path=ml_model_path,
                threshold=float(os.getenv("ANOMALY_THRESHOLD", "0.7"))
            )
        
        self.ids = HybridIDS(rule_ids, ml_ids)
        
        # Charge Point
        self.charge_point: Optional[SecureChargePoint] = None
        
        # API callback queue
        self.api_queue: asyncio.Queue = asyncio.Queue()
        
        logger.info("SecureBridgeService başlatıldı")
    
    async def start(self):
        """Bridge'i başlat"""
        logger.info("="*60)
        logger.info("SECURE OCPP-TO-CAN BRIDGE BAŞLATILIYOR")
        logger.info("="*60)
        
        # CAN-Bus'a bağlan
        if not self.can_handler.connect():
            logger.error("CAN-Bus bağlantısı başarısız! vcan0 kurulu mu?")
            logger.info("Kurmak için:")
            logger.info("  sudo modprobe vcan")
            logger.info("  sudo ip link add dev vcan0 type vcan")
            logger.info("  sudo ip link set up vcan0")
            return
        
        # OCPP bağlantısı
        if OCPP_AVAILABLE:
            try:
                logger.info(f"CSMS'e bağlanılıyor: {self.csms_url}")
                # CSMS bağlantısını dene (timeout OCPP kütüphanesi tarafından yönetiliyor)
                async with websockets.connect(
                    self.csms_url,
                    subprotocols=['ocpp1.6'],
                    ping_interval=None  # Ping'i kapat
                ) as ws:
                    self.charge_point = SecureChargePoint(
                        self.charge_point_id,
                        ws,
                        self.can_handler,
                        self.blockchain,
                        self.ids,
                        api_callback=self._api_callback
                    )
                    
                    # BootNotification gönder
                    await self.charge_point.send_boot_notification()
                    
                    # Async görevler
                    tasks = [
                        self.charge_point.start(),  # OCPP message handler
                        self.charge_point.send_heartbeat_loop(60),
                        self.charge_point.listen_can_bus()
                    ]
                    
                    logger.info("✓ Bridge aktif!")
                    await asyncio.gather(*tasks)
            
            except Exception as e:
                logger.error(f"OCPP bağlantı hatası: {e}")
                logger.info("Not: CSMS sunucusu çalışıyor mu?")
                logger.info("Standalone CAN moduna geçiliyor...")
                # CSMS olmadan da CAN dinlemeye devam et
                await self._standalone_can_mode()
        else:
            logger.warning("OCPP kütüphanesi yok, sadece CAN dinleme modu")
            # Sadece CAN dinle
            await self._standalone_can_mode()
    
    async def _standalone_can_mode(self):
        """OCPP olmadan sadece CAN-Bus dinleme modu"""
        logger.info("Standalone CAN monitoring modu başlatıldı")
        
        # API server'a bridge state'ini kaydet
        await self._register_with_api_server()
        
        # Periyodik olarak state'i güncelle (her 10 saniyede bir)
        last_update = time.time()
        
        while True:
            try:
                frame = self.can_handler.receive_frame(timeout=0.1)
                
                if frame:
                    # IDS kontrolü
                    alert, ml_score = self.ids.check_can_frame(
                        frame.can_id,
                        frame.data,
                        frame.timestamp
                    )
                    
                    if alert:
                        logger.warning(f"⚠ {alert.description}")
                        self.blockchain.add_block(alert.to_dict(), block_type="ALERT")
                    
                    self.blockchain.add_block(frame.to_dict(), block_type="CAN")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"CAN monitoring hatası: {e}")
            
            # Her 10 saniyede bir API server'a state güncelle
            if time.time() - last_update >= 10.0:
                await self._register_with_api_server()
                last_update = time.time()
            
            await asyncio.sleep(0.01)
    
    async def _register_with_api_server(self):
        """API server'a bridge state'ini kaydet"""
        api_url = os.getenv("API_URL", "http://127.0.0.1:8000")
        
        try:
            stats = self.get_stats()
            
            if AIOHTTP_AVAILABLE:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{api_url}/api/bridge/register",
                        json=stats,
                        timeout=aiohttp.ClientTimeout(total=2)
                    ) as response:
                        if response.status == 200:
                            logger.debug("Bridge state API server'a kaydedildi")
                        else:
                            logger.warning(f"API server kayıt hatası: {response.status}")
            elif REQUESTS_AVAILABLE:
                try:
                    response = requests.post(
                        f"{api_url}/api/bridge/register",
                        json=stats,
                        timeout=2
                    )
                    if response.status_code == 200:
                        logger.debug("Bridge state API server'a kaydedildi")
                except Exception as e:
                    logger.debug(f"API server kayıt hatası: {e}")
        except Exception as e:
            logger.debug(f"API server'a bağlanılamadı: {e}")
    
    async def _api_callback(self, event_type: str, data: Dict[str, Any]):
        """Dashboard için veri gönderme callback'i"""
        await self.api_queue.put({
            "type": event_type,
            "data": data,
            "timestamp": time.time()
        })
    
    def get_stats(self) -> Dict:
        """Bridge istatistikleri"""
        ids_stats = self.ids.rule_based_ids.get_stats()
        
        # Alert listesini de ekle
        recent_alerts = self.ids.rule_based_ids.get_recent_alerts(20)
        ids_stats["recent_alerts"] = [alert.to_dict() for alert in recent_alerts]
        
        # Blockchain stats ve recent blocks
        blockchain_stats = self.blockchain.get_chain_stats()
        recent_blocks = self.blockchain.get_recent_blocks(20)
        blockchain_stats["recent_blocks"] = [block.to_dict() for block in recent_blocks]
        
        # ML-IDS stats
        ml_stats = None
        if self.ids.ml_based_ids:
            ml_stats = {
                "is_trained": self.ids.ml_based_ids.is_trained,
                "model_loaded": self.ids.ml_based_ids.model is not None,
                "threshold": self.ids.ml_based_ids.threshold,
                "training_samples": len(self.ids.ml_based_ids.training_buffer) if hasattr(self.ids.ml_based_ids, 'training_buffer') else 0,
                "ml_detections": getattr(self.ids, 'ml_detection_count', 0),
                "total_ml_checks": getattr(self.ids, 'total_ml_checks', 0)
            }
        
        return {
            "blockchain": blockchain_stats,
            "ids": ids_stats,
            "ml": ml_stats,
            "can_handler": {
                "interface": self.can_handler.interface,
                "is_connected": self.can_handler.is_connected
            }
        }
    
    def shutdown(self):
        """Bridge'i kapat"""
        logger.info("Bridge kapatılıyor...")
        self.can_handler.disconnect()
        logger.info("✓ Güvenli şekilde kapatıldı")


async def main():
    """Ana entry point"""
    # Logger konfigürasyonu
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>"
    )
    
    log_file = os.getenv("LOG_FILE", "./logs/bridge.log")
    logger.add(log_file, rotation="10 MB", retention="7 days")
    
    # Bridge'i başlat
    bridge = SecureBridgeService()
    
    try:
        await bridge.start()
    except KeyboardInterrupt:
        logger.info("\n⚠ Ctrl+C algılandı")
    finally:
        bridge.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

