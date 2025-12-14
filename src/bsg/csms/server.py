
import asyncio
import logging
import websockets
from datetime import datetime, timezone
from typing import Dict, List, Optional
from ocpp.v16 import call, call_result, ChargePoint as CP
from ocpp.v16.enums import Action, RegistrationStatus, AuthorizationStatus
from ocpp.routing import on
from src.bsg.utils.logging import setup_logger

logger = setup_logger(__name__)

# API senkronizasyonu için (opsiyonel)
try:
    from src.bsg.utils.api_sync import BSGAPISync
    API_SYNC_AVAILABLE = True
except ImportError:
    API_SYNC_AVAILABLE = False
    logger.debug("API sync modülü mevcut değil, senkronizasyon devre dışı")

class CSMSimulator:
    """
    Central System (CSMS) Simulator.
    
    Attributes:
        secure_mode (bool): If True, enables security checks to prevent duplicate bookings.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 9024, secure_mode: bool = False, 
                 api_sync: bool = False, api_url: str = "http://127.0.0.1:8000"):
        self.host = host
        self.port = port
        self.secure_mode = secure_mode
        self.server = None
        self.connected_charge_points: Dict[str, CP] = {}
        # Stores active transactions: list of dicts
        self.active_transactions: List[Dict] = []
        self.is_running = False
        # API senkronizasyonu
        self.api_sync_enabled = api_sync and API_SYNC_AVAILABLE
        self.api_sync = None
        if self.api_sync_enabled:
            self.api_sync = BSGAPISync(api_url)
            logger.info(f"API senkronizasyonu etkin: {api_url}")
        
    async def start(self):
        """Starts the CSMS WebSocket server."""
        self.is_running = True
        self.server = await websockets.serve(
            self._handle_connection,
            self.host,
            self.port,
            subprotocols=["ocpp1.6"]
        )
        mode_str = "🔒 SECURE MODE" if self.secure_mode else "⚠️  VULNERABLE MODE"
        logger.info(f"✅ CSMS started: ws://{self.host}:{self.port} [{mode_str}]")
        
    async def stop(self):
        """Stops the CSMS server."""
        self.is_running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("🛑 CSMS stopped")
            
    async def _handle_connection(self, websocket):
        """Handles incoming ChargePoint connections."""
        path = websocket.request.path if hasattr(websocket, 'request') else websocket.path
        charge_point_id = path.strip("/")
        logger.info(f"🔌 New connection: {charge_point_id}")
        
        cp = ChargePointHandler(charge_point_id, websocket, self)
        self.connected_charge_points[charge_point_id] = cp
        
        # API'ye senkronize et (eğer etkinse)
        if self.api_sync_enabled and self.api_sync:
            try:
                self.api_sync.sync_csms_data(self)
            except Exception as e:
                logger.debug(f"API senkronizasyonu hatası (non-critical): {e}")
        
        try:
            await cp.start()
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"❌ Connection closed: {charge_point_id}")
        except Exception as e:
            logger.error(f"❌ Connection error ({charge_point_id}): {e}")
        finally:
            self.connected_charge_points.pop(charge_point_id, None)
            # API'ye senkronize et (bağlantı kapandığında)
            if self.api_sync_enabled and self.api_sync:
                try:
                    self.api_sync.sync_csms_data(self)
                except Exception as e:
                    logger.debug(f"API senkronizasyonu hatası (non-critical): {e}")

    def is_reservation_active(self, reservation_id: int) -> bool:
        """Checks if a reservation ID is currently used in an active transaction."""
        for tx in self.active_transactions:
            if tx.get("reservation_id") == reservation_id and tx.get("active"):
                return True
        return False

    def register_transaction(self, charge_point_id: str, transaction_id: int, 
                            reservation_id: Optional[int], id_tag: str):
        """Registers a new transaction."""
        transaction = {
            "charge_point_id": charge_point_id,
            "transaction_id": transaction_id,
            "reservation_id": reservation_id,
            "id_tag": id_tag,
            "start_time": datetime.now().isoformat(),
            "active": True
        }
        self.active_transactions.append(transaction)
        
        # Log warning if we just registered a duplicate (meaning vulnerability was exploited)
        # We check count of matches. If > 1, then we have a duplicate.
        count = sum(1 for tx in self.active_transactions 
                   if tx.get("reservation_id") == reservation_id and tx.get("active"))
        
        if count > 1 and reservation_id is not None:
             logger.warning(
                f"⚠️  VULNERABILITY EXPLOITED: Duplicate transaction for ReservationID {reservation_id}!"
            )
        else:
            logger.info(f"Transaction registered: {transaction_id}")
        
        # API'ye senkronize et (eğer etkinse)
        if self.api_sync_enabled and self.api_sync:
            try:
                self.api_sync.sync_csms_data(self)
            except Exception as e:
                logger.debug(f"API senkronizasyonu hatası (non-critical): {e}")

    def get_active_transactions_by_reservation(self, reservation_id_str: str) -> List[Dict]:
        """Helper to find transactions by reservation ID (string input from test)."""
        reservation_id_int = abs(hash(reservation_id_str)) % 1000000
        return [
            tx for tx in self.active_transactions
            if tx.get("reservation_id") == reservation_id_int and tx.get("active")
        ]

    def get_statistics(self) -> Dict:
        return {
            "connected_charge_points": len(self.connected_charge_points),
            "total_transactions": len(self.active_transactions),
            "active_transactions": len([tx for tx in self.active_transactions if tx["active"]])
        }


class ChargePointHandler(CP):
    """
    Handles OCPP messages from a Charge Point.
    """
    
    def __init__(self, charge_point_id: str, websocket, csms: CSMSimulator):
        super().__init__(charge_point_id, websocket)
        self.csms = csms
        self.transaction_counter = 0
        
    @on(Action.boot_notification)
    async def on_boot_notification(self, charge_point_vendor: str, 
                                    charge_point_model: str, **kwargs):
        logger.info(f"📢 BootNotification: {self.id}")
        return call_result.BootNotification(
            current_time=datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            interval=300,
            status=RegistrationStatus.accepted
        )
        
    @on(Action.heartbeat)
    async def on_heartbeat(self):
        return call_result.Heartbeat(
            current_time=datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
        )
        
    @on(Action.status_notification)
    async def on_status_notification(self, connector_id: int, error_code: str,
                                     status: str, **kwargs):
        logger.info(f"📊 StatusNotification: {self.id} -> {status}")
        return call_result.StatusNotification()
        
    @on(Action.start_transaction)
    async def on_start_transaction(self, connector_id: int, id_tag: str,
                                   meter_start: int, timestamp: str,
                                   reservation_id: Optional[int] = None, **kwargs):
        """
        Handle StartTransaction.
        Checks for duplicate booking if secure_mode is enabled.
        """
        logger.info(f"Request StartTransaction from {self.id}, ResID: {reservation_id}")

        # --- SECURITY CHECK ---
        if self.csms.secure_mode and reservation_id is not None:
            if self.csms.is_reservation_active(reservation_id):
                logger.error(f"🛡️ SECURITY BLOCK: Rejected duplicate reservation {reservation_id} from {self.id}")
                return call_result.StartTransaction(
                    transaction_id=0,
                    id_tag_info={
                        "status": AuthorizationStatus.invalid  # Reject the transaction
                    }
                )
        # ----------------------

        self.transaction_counter += 1
        transaction_id = int(f"{hash(self.id) % 1000}{self.transaction_counter}")
        
        self.csms.register_transaction(
            self.id, 
            transaction_id, 
            reservation_id, 
            id_tag
        )
        
        return call_result.StartTransaction(
            transaction_id=transaction_id,
            id_tag_info={"status": AuthorizationStatus.accepted}
        )
        
    @on(Action.stop_transaction)
    async def on_stop_transaction(self, transaction_id: int, timestamp: str,
                                  meter_stop: int, **kwargs):
        # Mark transaction as inactive
        for tx in self.csms.active_transactions:
            if tx["transaction_id"] == transaction_id:
                tx["active"] = False
                break
                
        logger.info(f"⏹️  Transaction stopped: {transaction_id}")
        return call_result.StopTransaction()
