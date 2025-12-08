import asyncio
import logging
import random
from datetime import datetime

import websockets
import can

from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call

logging.basicConfig(level=logging.INFO)

VIRTUAL_CAN_BUS = "vcan0"
CHARGE_POINT_ID = "CP_001"
# Proxy Portu (9023) olmalı ki saldırı çalışsın!
CSMS_URL = "ws://localhost:9023"

CAN_ID_METER_VALUE = 0x300


class ChargePointSimulator(cp):
    def __init__(self, id, connection, can_bus):
        super().__init__(id, connection)
        self._can_bus = can_bus

    async def send_boot_notification(self):
        logging.info("[CP] BootNotification gonderiliyor.")
        
        try:
            request = call.BootNotificationPayload(
                charge_point_model="SDP-VM-v1",
                charge_point_vendor="BSG_Lab",
            )
        except AttributeError:
            request = call.BootNotification(
                charge_point_model="SDP-VM-v1",
                charge_point_vendor="BSG_Lab",
            )

        response = await self.call(request)

        if response.status == "Accepted":
            logging.info(
                "[CP] KABUL EDILDI. Interval: %ss", getattr(response, "interval", "?")
            )
            interval = getattr(response, "interval", 10) or 10
            asyncio.create_task(self.start_heartbeat_loop(interval))
        else:
            logging.warning(f"[CP] Beklenmeyen status: {response.status}")

    async def start_heartbeat_loop(self, interval):
        while True:
            await asyncio.sleep(interval)
            try:
                request = call.HeartbeatPayload()
            except AttributeError:
                request = call.Heartbeat()
            
            await self.call(request)
            logging.info("[CP] Heartbeat gonderildi.")

    async def send_status(self, status):
        try:
            request = call.StatusNotificationPayload(
                connector_id=1,
                error_code="NoError",
                status=status,
            )
        except AttributeError:
            request = call.StatusNotification(
                connector_id=1,
                error_code="NoError",
                status=status,
            )
        await self.call(request)

    async def send_simulated_meter_values(self):
        current_energy = 1000
        while True:
            await asyncio.sleep(10)
            current_energy += random.randint(5, 15)
            can_data = current_energy.to_bytes(8, "little")
            try:
                can_msg = can.Message(
                    arbitration_id=CAN_ID_METER_VALUE,
                    data=can_data,
                    is_extended_id=False,
                )
                self._can_bus.send(can_msg)
                logging.info(
                    "--- [CP -> vcan0] CAN VERISI: %d Wh ---", current_energy
                )
            except can.CanError:
                pass

    async def listen_can_bus(self):
        logging.info("[CP] vcan0 dinleniyor.")
        while True:
            try:
                msg = await asyncio.to_thread(self._can_bus.recv, 1.0)
                if msg and msg.arbitration_id == CAN_ID_METER_VALUE:
                    energy_value = int.from_bytes(msg.data, "little")

                    try:
                        request = call.MeterValuesPayload(
                            connector_id=1,
                            meter_value=[
                                {
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "sampled_value": [
                                        {
                                            "value": str(energy_value),
                                            "unit": "Wh",
                                            "measurand": "Energy.Active.Import.Register",
                                        }
                                    ],
                                }
                            ],
                        )
                    except AttributeError:
                        request = call.MeterValues(
                            connector_id=1,
                            meter_value=[
                                {
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "sampled_value": [
                                        {
                                            "value": str(energy_value),
                                            "unit": "Wh",
                                            "measurand": "Energy.Active.Import.Register",
                                        }
                                    ],
                                }
                            ],
                        )

                    await self.call(request)
                    logging.info(
                        "[CP -> CSMS] OCPP VERISI ILETILDI: %d Wh", energy_value
                    )
            except Exception:
                await asyncio.sleep(1)


async def main():
    print("=" * 50)
    print("      CP SIMULATOR (UYUMLU SURUM - FINAL)      ")
    print("=" * 50)

    try:
        can_bus = can.Bus(
            VIRTUAL_CAN_BUS, interface="socketcan", receive_own_messages=True
        )
    except Exception:
        print(f"HATA: '{VIRTUAL_CAN_BUS}' yok.")
        return

    try:
        async with websockets.connect(
            f"{CSMS_URL}/{CHARGE_POINT_ID}",
            subprotocols=["ocpp1.6"],
            ping_interval=None,
        ) as ws:
            logging.info("[CP] Sunucuya baglandi.")
            cp_obj = ChargePointSimulator(CHARGE_POINT_ID, ws, can_bus)

            try:
                await asyncio.gather(
                    cp_obj.start(),
                    cp_obj.send_boot_notification(),
                    cp_obj.listen_can_bus(),
                    cp_obj.send_simulated_meter_values(),
                )
            except websockets.exceptions.ConnectionClosedOK:
                logging.warning("[CP] Baglanti normal sekilde kapatildi (1000).")
            except websockets.exceptions.ConnectionClosedError as e:
                logging.error("[CP] Baglanti hata ile kapandi: %s", e)

    except Exception as e:
        logging.error("Baglanti Hatasi: %s", e)

    finally:
        try:
            can_bus.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
