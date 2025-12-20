import asyncio
import can
import time

VIRTUAL_CAN_BUS = 'vcan0'
ALLOWED_CAN_IDS = {0x200, 0x201, 0x300}

async def can_ids_detector():
    print(f"ADIM 6: Savunma (IDS) - '{VIRTUAL_CAN_BUS}' dinleniyor...")
    try:
        can_bus = can.Bus(VIRTUAL_CAN_BUS, interface='socketcan')
    except Exception as e:
        print(f"HATA: '{VIRTUAL_CAN_BUS}' bulunamadı.")
        return

    while True:
        try:
            msg = await asyncio.to_thread(can_bus.recv, 1.0)
            if msg and msg.arbitration_id not in ALLOWED_CAN_IDS:
                print(f"!!! ANOMALİ TESPİT EDİLDİ !!!")
                print(f"    Zaman: {time.time()} | CAN ID: {hex(msg.arbitration_id)}")
        except Exception:
            await asyncio.sleep(1)

if __name__ == '__main__':
    try:
        asyncio.run(can_ids_detector())
    except KeyboardInterrupt:
        print("\nIDS durduruldu.")