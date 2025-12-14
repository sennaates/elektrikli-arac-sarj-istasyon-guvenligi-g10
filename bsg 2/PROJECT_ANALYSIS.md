# 🔍 Proje Analizi - OCPP-CAN Bridge Security Simulation

**Analiz Tarihi**: 2025-01-27  
**Proje Dizini**: `/Users/earth/Downloads/bsg`

---

## 📋 Proje Özeti

Bu proje, **OCPP (Open Charge Point Protocol)** ve **CAN-Bus** protokolleri arasındaki güvenlik köprüsünü simüle eden, şarj istasyonu sistemlerindeki zafiyetleri test eden ve blokzincir tabanlı güvenlik katmanı önerisi sunan bir güvenlik araştırma projesidir.

### Temel Özellikler
- ✅ OCPP 1.6 protokol simülasyonu (CSMS + Charge Point)
- ✅ CAN-Bus (vcan0) simülasyonu
- ✅ OCPP ↔ CAN mesaj dönüşüm köprüsü
- ✅ 3 farklı güvenlik senaryosu (Plain WS, Weak TLS, Strong TLS)
- ✅ MitM (Man-in-the-Middle) saldırı simülasyonu
- ✅ CAN Intrusion Detection System (IDS)
- ✅ Test framework (pytest)

---

## 🏗️ Proje Yapısı

```
bsg/
├── src/                          # Ana kaynak kod
│   ├── ocpp/                     # OCPP simülatörleri
│   │   ├── central_system/       # CSMS (Central System Management System)
│   │   │   └── simulator.py      # Merkezi yönetim sistemi
│   │   └── charge_point/         # CP (Charge Point)
│   │       └── simulator.py      # Şarj istasyonu simülatörü
│   ├── can_bus/                  # CAN-Bus simülasyonu
│   │   └── can_simulator.py      # vcan0 simülatörü
│   ├── bridge/                   # OCPP-CAN köprü katmanı
│   │   ├── gateway.py            # Mesaj gateway'i
│   │   └── mapper.py             # OCPP ↔ CAN dönüşüm tabloları
│   ├── security/                 # Güvenlik katmanları
│   │   └── tls_config.py         # TLS konfigürasyonları
│   ├── attacks/                  # Saldırı simülasyonları
│   │   └── mitm_proxy.py         # MitM proxy
│   └── detection/                # Anomali tespit
│       └── can_ids.py            # CAN Intrusion Detection System
├── config/                       # Yapılandırma dosyaları
│   ├── ocpp_config.yaml         # OCPP ayarları
│   └── can_config.yaml          # CAN ayarları
├── certs/                        # TLS sertifikaları
│   ├── weak/                    # Zayıf sertifikalar (512 bit)
│   └── strong/                  # Güçlü sertifikalar (4096 bit)
├── tests/                        # Test senaryoları
│   └── my_scenario.py           # Senaryo şablonu
├── scripts/                      # Yardımcı scriptler
│   ├── setup_vcan.sh            # vcan0 kurulumu
│   ├── generate_certs.sh        # Test sertifikaları
│   └── run_demo.sh              # Demo çalıştırma
└── docs/                         # Dokümantasyon
    ├── README.md
    ├── PROJECT_SUMMARY.md
    ├── QUICKSTART.md
    ├── START_HERE.md
    ├── USAGE.md
    └── HOW_TO_SUBMIT_SCENARIO.md
```

---

## 🔧 Teknik Mimari

### 1. OCPP Katmanı

#### CSMSimulator (`src/ocpp/central_system/simulator.py`)
- **Görev**: Merkezi yönetim sistemi simülasyonu
- **Port**: 9000 (varsayılan)
- **Protokol**: WebSocket (ws/wss)
- **Özellikler**:
  - Charge Point bağlantı yönetimi
  - BootNotification handling
  - RemoteStartTransaction gönderme
  - RemoteStopTransaction gönderme
  - Mesaj istatistikleri

#### ChargePointSimulator (`src/ocpp/charge_point/simulator.py`)
- **Görev**: Şarj istasyonu simülasyonu
- **Bağlantı**: CSMS'e WebSocket üzerinden
- **Özellikler**:
  - CSMS'e bağlanma
  - BootNotification gönderme
  - OCPP mesajlarını CAN'a dönüştürme (gateway üzerinden)
  - CAN mesajlarını OCPP'ye dönüştürme

### 2. CAN-Bus Katmanı

#### CANBusSimulator (`src/can_bus/can_simulator.py`)
- **Arayüz**: vcan0 (virtual CAN)
- **Bitrate**: 500 kbps (CAN 2.0 standard)
- **Özellikler**:
  - CAN mesaj gönderme/alma
  - Listener callback sistemi
  - Mesaj loglama
  - İstatistik toplama

**CAN ID Tanımlamaları**:
- `0x200`: RemoteStartTransaction
- `0x201`: RemoteStopTransaction
- `0x210`: SetChargingProfile
- `0x300`: MeterValues
- `0x301`: ChargeStatus
- `0x9FF`: Error/Anomaly

### 3. Bridge Katmanı

#### OCPPCANGateway (`src/bridge/gateway.py`)
- **Görev**: OCPP ve CAN arasında köprü
- **Fonksiyonlar**:
  - `ocpp_message_to_can()`: OCPP → CAN dönüşümü
  - `can_message_to_ocpp()`: CAN → OCPP dönüşümü
  - İstatistik toplama

#### OCPPCANMapper (`src/bridge/mapper.py`)
- **Görev**: Mesaj format dönüşümleri
- **Mapping Tabloları**:
  - RemoteStartTransaction → CAN ID 0x200
  - RemoteStopTransaction → CAN ID 0x201
  - SetChargingProfile → CAN ID 0x210
  - MeterValues ← CAN ID 0x300
  - ChargeStatus ← CAN ID 0x301

### 4. Güvenlik Katmanı

#### TLSConfigManager (`src/security/tls_config.py`)
- **3 Senaryo**:
  1. **Plain WebSocket** (`plain_ws`): Şifreleme yok
  2. **Weak TLS** (`weak_tls`): TLS 1.0, 512-bit sertifikalar, verification kapalı
  3. **Strong TLS** (`strong_tls`): TLS 1.2+, 4096-bit sertifikalar, verification açık

### 5. Saldırı Simülasyonu

#### MitMProxy (`src/attacks/mitm_proxy.py`)
- **Görev**: Ortadaki adam saldırısı simülasyonu
- **Port**: 9090 (varsayılan)
- **Özellikler**:
  - WebSocket trafiğini intercept etme
  - Mesaj manipülasyonu (örn: RemoteStartTransaction'da connector ID değiştirme)
  - Mesaj loglama

### 6. Anomali Tespit

#### CANIntrusionDetector (`src/detection/can_ids.py`)
- **Görev**: CAN trafiğinde anomali tespiti
- **Tespit Yöntemleri**:
  1. **Beklenmeyen CAN ID**: Baseline'da olmayan ID'ler
  2. **Frekans Anomalisi**: Normalden %50+ sapma
  3. **Burst Attack**: Saniyede 10+ mesaj
- **Baseline Öğrenme**: 30 saniye normal trafik öğrenme

---

## 📊 Mesaj Akışı

### Normal Akış (OCPP → CAN)

```
CSMS → WebSocket → CP → Gateway → CAN Bus (vcan0)
```

1. CSMS `RemoteStartTransaction` gönderir
2. CP mesajı alır
3. Gateway OCPP mesajını CAN frame'e dönüştürür
4. CAN bus üzerinden gönderilir

### Ters Akış (CAN → OCPP)

```
CAN Bus (vcan0) → Gateway → CP → WebSocket → CSMS
```

1. CAN bus'tan `MeterValues` mesajı gelir
2. Gateway CAN frame'i OCPP mesajına dönüştürür
3. CP CSMS'e gönderir

---

## 🔒 Güvenlik Senaryoları

### Senaryo 1: Plain WebSocket ⚠️
- **Güvenlik**: ❌ YOK
- **Risk**: 🔴 ÇOK YÜKSEK
- **Kullanım**: Saldırı demonstrasyonu
- **Özellikler**:
  - Şifreleme yok
  - MitM saldırılarına açık
  - Mesaj manipülasyonu mümkün

### Senaryo 2: Weak TLS ⚠️
- **Güvenlik**: ⚠️ ZAYIF
- **Risk**: 🟠 YÜKSEK
- **Özellikler**:
  - TLS 1.0 (eski protokol)
  - Self-signed sertifikalar (512 bit)
  - Certificate verification kapalı
  - Zayıf cipher suites

### Senaryo 3: Strong TLS ✅
- **Güvenlik**: ✅ GÜÇLÜ
- **Risk**: 🟢 DÜŞÜK
- **Özellikler**:
  - TLS 1.2+ (modern protokol)
  - Güçlü sertifikalar (4096 bit)
  - Certificate verification açık
  - Strong cipher suites
  - Mutual TLS desteği

---

## 🧪 Test Framework

### Test Yapısı
- **Framework**: pytest + pytest-asyncio
- **Şablon**: `tests/my_scenario.py`
- **Port Yönetimi**: Her test farklı port kullanır (9020, 9021, ...)

### Test Senaryosu Örneği
```python
@pytest.mark.asyncio
async def test_my_scenario():
    # 1. CSMS başlat
    csms = CSMSimulator(host='localhost', port=9020, scenario='plain_ws')
    await csms.start()
    
    # 2. CP başlat
    cp = ChargePointSimulator(cp_id='CP_TEST', scenario='plain_ws')
    await cp.start()
    
    # 3. Senaryo uygula
    await csms.send_remote_start('cp_test', connector_id=1)
    
    # 4. Doğrula
    stats = cp.get_stats()
    assert stats['gateway_stats']['ocpp_to_can'] >= 1
    
    # 5. Temizle
    await cp.stop()
    await csms.stop()
```

---

## 📦 Bağımlılıklar

### Ana Kütüphaneler
- `ocpp==0.22.0`: OCPP protokol desteği
- `websockets==12.0`: WebSocket implementasyonu
- `python-can==4.3.1`: CAN bus işlemleri
- `cantools==39.4.1`: CAN mesaj parsing
- `cryptography==41.0.7`: Şifreleme
- `pytest==7.4.3`: Test framework

### Sistem Gereksinimleri
- **OS**: Linux (CAN kernel modülleri için)
- **Python**: 3.9+
- **CAN Utils**: `can-utils` paketi (candump, cansend için)
- **Root**: vcan0 kurulumu için sudo gerekir

---

## 🚀 Kullanım Senaryoları

### 1. Demo Çalıştırma
```bash
bash scripts/run_demo.sh plain_ws
```

### 2. Manuel Çalıştırma
```bash
# Terminal 1: CSMS
python -m src.ocpp.central_system.simulator --scenario plain_ws

# Terminal 2: CP
python -m src.ocpp.charge_point.simulator --scenario plain_ws

# Terminal 3: CAN trafiği
candump vcan0
```

### 3. MitM Saldırısı
```bash
# Terminal 1: CSMS
python -m src.ocpp.central_system.simulator --scenario plain_ws

# Terminal 2: MitM Proxy
python -m src.attacks.mitm_proxy --proxy-port 9090

# Terminal 3: CP (proxy üzerinden)
python -m src.ocpp.charge_point.simulator --csms-url ws://localhost:9090/...
```

### 4. Test Çalıştırma
```bash
pytest tests/ -v -s
```

---

## 📈 İstatistikler ve Metrikler

### Toplanan Metrikler
- **Gateway Stats**:
  - `ocpp_to_can`: OCPP → CAN dönüşüm sayısı
  - `can_to_ocpp`: CAN → OCPP dönüşüm sayısı
  - `errors`: Hata sayısı
- **CAN Stats**:
  - `total_messages`: Toplam mesaj sayısı
  - `id_distribution`: CAN ID dağılımı
- **IDS Stats**:
  - `anomalies_detected`: Tespit edilen anomali sayısı
  - `baseline_mode`: Öğrenme/tespit modu

---

## 🔮 Gelecek Geliştirmeler

### Kısa Vadeli
- [ ] Blokzincir entegrasyonu (hash tabanlı kayıt)
- [ ] Detaylı performans analizi
- [ ] Grafana/Prometheus monitoring
- [ ] Otomatik test suite

### Orta Vadeli
- [ ] Machine learning tabanlı anomali tespiti
- [ ] Gerçek donanım entegrasyonu
- [ ] V2X protokol desteği
- [ ] ISO 15118 uyumluluğu

### Uzun Vadeli
- [ ] End-to-end blokzincir güvenlik katmanı
- [ ] Federated learning ile IoT güvenliği
- [ ] Quantum-safe encryption
- [ ] Autonomous vehicle network

---

## ⚠️ Güvenlik ve Etik Uyarıları

- ⛔ Tüm testler **yalnızca izole laboratuvar ortamında** yapılmalı
- ⛔ Canlı altyapılara erişim **kesinlikle yasak**
- ⛔ Gerçek araç veya şarj istasyonlarında test yapılmamalı
- ✅ Sorumlu disclosure prensipleri uygulanmalı
- ✅ Tüm veriler anonimleştirilmeli

---

## 📚 Dokümantasyon Dosyaları

| Dosya | İçerik |
|-------|--------|
| `README.md` | Genel bakış ve kurulum |
| `PROJECT_SUMMARY.md` | Teknik mimari detayları |
| `QUICKSTART.md` | 5 dakikada başlangıç |
| `START_HERE.md` | İlk adım rehberi |
| `USAGE.md` | Kullanım örnekleri |
| `HOW_TO_SUBMIT_SCENARIO.md` | Senaryo gönderme rehberi |
| `INSTALL.md` | Detaylı kurulum |

---

## 🎯 Proje Durumu

### Tamamlanan Özellikler ✅
- OCPP simülatörleri (CSMS + CP)
- CAN-Bus simülasyonu
- OCPP-CAN köprü katmanı
- TLS konfigürasyonları (3 senaryo)
- MitM proxy
- CAN IDS
- Test framework
- Dokümantasyon

### Eksik/Planlanan Özellikler 📋
- Blokzincir entegrasyonu
- Gerçek donanım desteği
- Machine learning tabanlı IDS
- Monitoring dashboard
- Otomatik test suite

---

## 🔍 Kod İstatistikleri

- **Toplam Modül**: 8 ana modül
- **Sınıf Sayısı**: ~15 sınıf
- **Fonksiyon Sayısı**: ~65+ fonksiyon
- **Test Dosyası**: 1 şablon (genişletilebilir)
- **Konfigürasyon**: 2 YAML dosyası

---

## 📞 Destek ve Katkı

- **GitHub Issues**: Soru/Problem bildirimi
- **GitHub Discussions**: Senaryo fikirleri
- **Pull Requests**: Senaryo eklemeleri

---

**Son Güncelleme**: 2025-01-27  
**Analiz Eden**: Auto (Cursor AI)

