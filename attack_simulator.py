import asyncio
import json
import random
import uuid
import argparse
from datetime import datetime

# Renkli çıktılar için basit tanımlamalar
class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class AttackSimulator:
    def __init__(self, target_url="ws://localhost:9000/ocpp"):
        self.target_url = target_url
        print(f"{BColors.HEADER}--- SALDIRI SİMÜLATÖRÜ BAŞLATILDI ---{BColors.ENDC}")

    async def inject_ocpp_message(self, payload):
        """
        Mesajı sisteme enjekte eder (Simülasyon amaçlı ekrana basar)
        Gerçek sistemde burada websocket.send() olurdu.
        """
        print(f"\n{BColors.WARNING}[SALDIRI] Hedefe Paket Gönderiliyor...{BColors.ENDC}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Simülasyon gecikmesi
        await asyncio.sleep(0.5) 
        
        print(f"{BColors.OKGREEN}[BAŞARILI] Paket Bridge Sistemine Ulaştı.{BColors.ENDC}")
        self.log_attack_to_console(payload)

    def log_attack_to_console(self, payload):
        # IDS'in yakalaması gereken anomaliyi vurgula
        if "connectorId" in payload.get("payload", {}) and isinstance(payload["payload"]["connectorId"], str):
             print(f"{BColors.OKCYAN}>>> BEKLENEN IDS TEPKİSİ: [ALERT] Schema Validation Error (Type Mismatch){BColors.ENDC}")
        elif "extraField" in payload.get("payload", {}):
             print(f"{BColors.OKCYAN}>>> BEKLENEN IDS TEPKİSİ: [ALERT] Unknown Field Detected{BColors.ENDC}")

    async def attack_schema_drift(self):
        """
        SENARYO: OCPP Schema Drift (Senin Görevin)
        """
        print(f"\n{BColors.BOLD}⚡ SENARYO BAŞLATILIYOR: OCPP Schema Drift{BColors.ENDC}")
        print("Açıklama: Veri tipleri bozularak IDS şaşırtılmaya çalışılıyor.")

        # HATA 1: Tamsayı olması gereken yere String göndermek
        malformed_payload_1 = {
            "messageTypeId": 2,
            "uniqueId": str(uuid.uuid4()),
            "action": "StatusNotification",
            "payload": {
                "connectorId": "BIR_BUCUK",  # <-- HATA BURADA (Normalde sayı olmalı: 1)
                "status": "Available",
                "errorCode": "NoError"
            }
        }
        
        await self.inject_ocpp_message(malformed_payload_1)

        # HATA 2: Olmayan bir alan eklemek
        print(f"\n{BColors.BOLD}⚡ SENARYO ADIM 2: Bilinmeyen Alan Enjeksiyonu{BColors.ENDC}")
        malformed_payload_2 = {
            "messageTypeId": 2,
            "uniqueId": str(uuid.uuid4()),
            "action": "Heartbeat",
            "payload": {
                "extraField": "Bu alan OCPP standardında yok!", # <-- HATA BURADA
                "hack_attempt": True
            }
        }
        await self.inject_ocpp_message(malformed_payload_2)

    async def run(self):
        # Sadece senin senaryonu çalıştırır
        await self.attack_schema_drift()

if __name__ == "__main__":
    simulator = AttackSimulator()
    asyncio.run(simulator.run())
