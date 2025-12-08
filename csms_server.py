import asyncio
import logging
from datetime import datetime

import websockets

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.v16.enums import RegistrationStatus, Action

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    @on(Action.BootNotification)
    async def on_boot_notification(
        self, charge_point_vendor, charge_point_model, **kwargs
    ):
        logging.info(
            "[CSMS] BAGLANTI ISTEGI: id=%s | vendor=%s | model=%s",
            self.id,
            charge_point_vendor,
            charge_point_model,
        )

        try:
            # OCPP 0.24.0+ için Payload sınıfı kullanımı
            return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().isoformat(),
                interval=10,
                status=RegistrationStatus.accepted,
            )
        except AttributeError:
            # Fallback (Eski versiyonlar için)
            return call_result.BootNotification(
                current_time=datetime.utcnow().isoformat(),
                interval=10,
                status=RegistrationStatus.accepted,
            )

    @on(Action.Heartbeat)
    async def on_heartbeat(self):
        logging.info(f"[CSMS] '{self.id}' Heartbeat alindi.")
        try:
            return call_result.HeartbeatPayload(current_time=datetime.utcnow().isoformat())
        except AttributeError:
            return call_result.Heartbeat(current_time=datetime.utcnow().isoformat())

    @on(Action.MeterValues)
    async def on_meter_values(self, connector_id, meter_value, **kwargs):
        print("\n" + "=" * 40)
        logging.info(f"[CSMS] '{self.id}' SENSÖR VERİSİ ALINDI:")
        try:
            for mv in meter_value:
                sampled_values = mv.get("sampled_value", [])
                if not isinstance(sampled_values, list):
                    sampled_values = [sampled_values]
                
                for sv in sampled_values:
                    val = sv.get("value", "N/A")
                    unit = sv.get("unit", "")
                    print(f"  -> Değer: {val} {unit}")
        except Exception as e:
            logging.error(f"[CSMS] MeterValues işlenirken hata: {e}")
            
        print("=" * 40 + "\n")
        try:
            return call_result.MeterValuesPayload()
        except AttributeError:
            return call_result.MeterValues()

    @on(Action.StatusNotification)
    async def on_status_notification(
        self, connector_id, error_code, status, **kwargs
    ):
        logging.info(f"[CSMS] '{self.id}' durumu: {status}")
        try:
            return call_result.StatusNotificationPayload()
        except AttributeError:
            return call_result.StatusNotification()


async def on_connect(websocket):
    try:
        path = getattr(websocket, "path", "/")
        requested_path = (path or "/").strip("/")
        if not requested_path:
            charge_point_id = "CP_001"
        else:
            charge_point_id = requested_path

        logging.info(
            "[CSMS] Yeni baglanti: id=%s | path=%s | subprotocol=%s",
            charge_point_id,
            path,
            websocket.subprotocol,
        )

        cp_obj = ChargePoint(charge_point_id, websocket)
        await cp_obj.start()

    except Exception as e:
        logging.exception(f"[CSMS] Hata: {e}")


async def main():
    server = await websockets.serve(
        on_connect,
        "0.0.0.0",
        9000,
        subprotocols=["ocpp1.6"],
        ping_interval=None,
    )
    print("=" * 50)
    print("      CSMS SUNUCUSU (SADELESTIRILMIS V12 - FINAL)      ")
    print("      Port 9000 dinleniyor.                           ")
    print("=" * 50)
    await server.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
