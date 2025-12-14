# OCPP-CAN Bridge Security Simulation
# Blockchain-Based CAN-Bus Security Framework

## 🎯 Proje Kapsamı

Bu proje, OCPP (Open Charge Point Protocol) ve CAN-Bus arasındaki güvenlik köprüsünü simüle ederek, şarj istasyonu sistemlerindeki zafiyetleri test eder. Üç farklı güvenlik konfigürasyonu ile saldırı ve savunma senaryoları gerçekleştirilir.

## 📋 Hedef Senaryolar

1. **Plain WebSocket (ws)** - En zayıf güvenlik (MitM, mesaj manipülasyonu)
2. **WSS + Zayıf TLS** - Zayıf şifreleme konfigürasyonları (TLS1.0, zayıf cipher suites)
3. **WSS + Güçlü TLS** - Önerilen güvenli konfigürasyon (TLS1.2/1.3 + mutual TLS)

## 🏗️ Proje Yapısı

```
bsg/
├── src/
│   ├── ocpp/                  # OCPP simülatörleri (CP ve CSMS)
│   │   ├── charge_point/      # CP simülatör
│   │   └── central_system/    # CSMS simülatör
│   ├── can_bus/              # CAN-Bus simülasyonu
│   │   ├── can_simulator.py  # vcan0 simülatörü
│   │   └── can_messages.py   # CAN mesaj yapıları
│   ├── bridge/               # OCPP-CAN köprü katmanı
│   │   ├── gateway.py        # Mesaj mapping ve dönüşüm
│   │   └── mapper.py         # OCPP ↔ CAN dönüşüm tabloları
│   ├── security/             # Güvenlik katmanları
│   │   ├── tls_config.py     # TLS konfigürasyonları
│   │   └── validator.py      # Mesaj doğrulama
│   ├── attacks/              # Saldırı simülasyonları
│   │   ├── mitm_proxy.py     # MitM proxy
│   │   └── attack_scenarios.py
│   ├── detection/            # Anomali tespit
│   │   └── can_ids.py        # CAN Intrusion Detection System
│   └── blockchain/           # Blokzincir altyapısı (gelecek)
├── tests/                    # Test senaryoları
│   ├── scenario_1_plain_ws.py
│   ├── scenario_2_weak_tls.py
│   └── scenario_3_strong_tls.py
├── config/                   # Yapılandırma
│   ├── ocpp_config.yaml
│   ├── can_config.yaml
│   └── security_config.yaml
├── certs/                    # TLS sertifikaları
│   ├── weak/                 # Zayıf sertifikalar
│   └── strong/               # Güçlü sertifikalar
├── docs/                     # Dokümantasyon
└── scripts/                  # Yardımcı scriptler
    ├── setup_vcan.sh         # vcan0 kurulumu
    └── generate_certs.sh     # Test sertifikaları

```

## 🔌 OCPP-CAN Mapping

| OCPP Action | CAN ID | Payload | Yön |
|-------------|--------|---------|-----|
| RemoteStartTransaction | 0x200 | [cp_id, connector_id, start_cmd] | CSMS→CP→CAN |
| RemoteStopTransaction | 0x201 | [tx_id, stop_cmd] | CSMS→CP→CAN |
| SetChargingProfile | 0x210 | [profile_id, max_current] | CSMS→CP→CAN |
| MeterValues | 0x300 | [energy, voltage, current] | CAN→CP→CSMS |

## 🛠️ Kurulum

### ⚠️ ÖNEMLİ: CAN Bus Gereksinimi

**Gerçek CAN bus desteği için Linux gerekli!**

- ✅ **Linux**: CAN bus tam desteklenir
- ❌ **macOS**: CAN bus desteği yok (Docker container içinde bile)
- 💡 **Çözüm**: Linux VM kullanın (VirtualBox, VMware, vb.)

Detaylar: [LINUX_SETUP.md](LINUX_SETUP.md) ve [docker/README_CAN_BUS.md](docker/README_CAN_BUS.md)

### 1. Gereksinimler (Linux)

```bash
# Linux gerekli (sanal CAN desteği için)
sudo apt-get update
sudo apt-get install -y linux-modules-extra-$(uname -r)
sudo apt-get install -y can-utils
```

### 2. Sanal Ortam
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Sanal CAN Arayüzü
```bash
chmod +x scripts/setup_vcan.sh
sudo ./scripts/setup_vcan.sh
```

### 4. Test Sertifikaları
```bash
chmod +x scripts/generate_certs.sh
./scripts/generate_certs.sh
```

## 🚀 Kullanım

### Senaryo 1: Plain WebSocket (Saldırıya Açık)
```bash
# Terminal 1: CSMS başlat
python -m src.ocpp.central_system --scenario plain_ws

# Terminal 2: CP başlat
python -m src.ocpp.charge_point --scenario plain_ws

# Terminal 3: MitM saldırısı
python -m src.attacks.mitm_proxy --scenario plain_ws
```

### Senaryo 2: Zayıf TLS
```bash
python -m src.ocpp.central_system --scenario weak_tls
python -m src.ocpp.charge_point --scenario weak_tls
```

### Senaryo 3: Güçlü TLS
```bash
python -m src.ocpp.central_system --scenario strong_tls
python -m src.ocpp.charge_point --scenario strong_tls
```

## 🔍 CAN Trafiği İzleme

```bash
# vcan0 trafiğini izle
candump vcan0

# Belirli CAN ID'leri filtrele
candump vcan0 | grep "0x200\|0x201"
```

## 🧪 Test Senaryoları

```bash
# Tüm senaryoları çalıştır
pytest tests/ -v

# Belirli senaryoyu test et
pytest tests/scenario_1_plain_ws.py -v -s

# Coverage raporu
pytest tests/ --cov=src --cov-report=html
```

## 📊 Ölçülecek Metrikler

- **Gecikme (Latency)**: OCPP mesajı → CAN frame dönüşüm süresi
- **Başarı Oranı**: Başarılı mesaj iletimi yüzdesi
- **Tespit Oranı**: CAN IDS tarafından yakalanan anomali oranı
- **CPU/Bellek**: Sistem kaynak kullanımı

## ⚠️ Güvenlik ve Etik Uyarıları

- ⛔ Tüm testler **yalnızca izole ağ ortamında** gerçekleştirilmeli
- ⛔ Gerçek şarj istasyonlarına veya canlı altyapılara asla erişim sağlanmamalı
- ⛔ Sorumlu disclosure prensipleri uygulanmalı
- ✅ Tüm log ve veriler anonimleştirilmeli

## 🎨 Kendi Senaryonuzu Yazın

### Hızlı Başlangıç

```bash
# 1. Şablon dosyayı kopyalayın
cp tests/my_scenario.py tests/my_anomaly.py

# 2. Düzenleyin ve test edin
pytest tests/my_anomaly.py -v -s
```

### Dokümantasyon

- **START_HERE.md** - 🚀 İlk adım rehberi
- **HOW_TO_SUBMIT_SCENARIO.md** - 📤 Senaryo gönderme rehberi (format kuralları, şablon)
- **USAGE.md** - Manuel kullanım örnekleri
- **PROJECT_SUMMARY.md** - Teknik mimari

### Örnek Senaryo Yapısı

```python
@pytest.mark.asyncio
async def test_my_scenario():
    # 1. CSMS başlat
    csms = CSMSimulator(host="localhost", port=9020, scenario="plain_ws")
    await csms.start()
    
    # 2. CP başlat
    cp = ChargePointSimulator(cp_id="CP_TEST", scenario="plain_ws", ...)
    await cp.start()
    await asyncio.sleep(2)
    
    # 3. Senaryonuzu uygula
    await csms.send_remote_start("cp_test", connector_id=1)
    
    # 4. Sonucu doğrula
    stats = csms.get_stats()
    assert stats['gateway_stats']['ocpp_to_can'] >= 1
    
    # 5. Temizle
    await cp.stop()
    await csms.stop()
```

## 📚 Referanslar

- OCPP 1.6 Specification
- ISO 15118 (Vehicle to Grid Communication)
- CAN 2.0 Specification
- ISO/SAE 21434 (Cybersecurity Engineering)

## 👥 Katkıda Bulunanlar

Bu proje akademik araştırma kapsamında geliştirilmiştir.

