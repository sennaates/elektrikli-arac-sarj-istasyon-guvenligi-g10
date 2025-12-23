
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

import websockets
from ocpp.v16 import call, ChargePoint as CP
from src.bsg.utils.logging import setup_logger

logger = setup_logger(__name__)

class ChargePointSimulator:
    """
    Simulator for an OCPP 1.6 J Charge Point.
    Connects to a CSMS and allows sending commands.
    """
    
    def __init__(self, charge_point_id: str, csms_url: str):
        self.charge_point_id = charge_point_id
        self.csms_url = csms_url
        self.websocket = None
        self.charge_point = None
        self.is_connected = False
        self._tasks = []
        
    async def start(self):
        """Starts the ChargePoint connection and background tasks."""
        try:
            url = f"{self.csms_url}/{self.charge_point_id}"
            self.websocket = await websockets.connect(
                url,
                subprotocols=["ocpp1.6"]
            )
            self.charge_point = CP(self.charge_point_id, self.websocket)
            self.is_connected = True
            
            logger.info(f"✅ ChargePoint connected: {self.charge_point_id}")
            
            # Start listening loop in background
            self._tasks.append(asyncio.create_task(self.charge_point.start()))
            
            # Wait a bit for connection stability
            await asyncio.sleep(0.1)
            
            # Send Boot Notification
            await self._send_boot_notification()
            
            # Start Heartbeat loop
            self._tasks.append(asyncio.create_task(self._heartbeat_loop()))
            
        except Exception as e:
            logger.error(f"❌ Connection error ({self.charge_point_id}): {e}")
            raise
            
    async def _send_boot_notification(self):
        try:
            request = call.BootNotification(
                charge_point_model="SimulatorModel",
                charge_point_vendor="BSG_Professional"
            )
            response = await self.charge_point.call(request)
            logger.info(f"📢 BootNotification response: {response.status}")
        except Exception as e:
             logger.error(f"Failed to send BootNotification: {e}")

    async def stop(self):
        """Stops the ChargePoint and closes connection."""
        self.is_connected = False
        for task in self._tasks:
            task.cancel()
            
        if self.websocket:
            await self.websocket.close()
            logger.info(f"🛑 ChargePoint stopped: {self.charge_point_id}")
            
    async def _heartbeat_loop(self):
        """Sends periodic heartbeats."""
        while self.is_connected:
            try:
                await asyncio.sleep(30) # Increased interval
                if self.is_connected and self.charge_point:
                    request = call.Heartbeat()
                    await self.charge_point.call(request)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
                break
                
    async def send_start_transaction(self, reservation_id: str, 
                                     id_tag: str = "TEST_TAG",
                                     connector_id: int = 1) -> Dict:
        """
        Sends a StartTransaction request.
        
        Args:
            reservation_id: The reservation ID (string). 
                            Will be converted to int hash as per OCPP 1.6 limitations in this sim.
            id_tag: The identifier tag.
            connector_id: Connector ID.
            
        Returns:
            Dict containing transaction details and status.
        """
        if not self.is_connected or not self.charge_point:
            raise RuntimeError(f"ChargePoint not connected: {self.charge_point_id}")
            
        # OCPP 1.6 expects Integer reservationId. 
        # We hash the string to get an int for simulation purposes.
        reservation_id_int = abs(hash(reservation_id)) % 1000000
        
        request = call.StartTransaction(
            connector_id=connector_id,
            id_tag=id_tag,
            meter_start=0,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            reservation_id=reservation_id_int
        )
        
        logger.info(
            f"🔋 Sending StartTransaction - "
            f"CP: {self.charge_point_id}, ReservationID: {reservation_id} ({reservation_id_int})"
        )
        
        response = await self.charge_point.call(request)
        
        return {
            "charge_point_id": self.charge_point_id,
            "transaction_id": response.transaction_id,
            "reservation_id": reservation_id,
            "status": response.id_tag_info["status"]
        }
        
    async def send_stop_transaction(self, transaction_id: int):
        """Sends a StopTransaction request."""
        if not self.is_connected or not self.charge_point:
            raise RuntimeError(f"ChargePoint not connected: {self.charge_point_id}")
            
        request = call.StopTransaction(
            transaction_id=transaction_id,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None).isoformat(),
            meter_stop=100
        )
        
        response = await self.charge_point.call(request)
        logger.info(f"⏹️  StopTransaction sent: TxID {transaction_id}")
        return response
