# 🚗 Elektrikli Araç Şarj İstasyonu Güvenlik Simülasyonu

> Blockchain-Based CAN-Bus Security Framework & OCPP Threat Analysis

## 🔍 Proje Tanımı

Bu proje, **elektrikli araç şarj altyapılarında (EVCS)** kullanılan **OCPP (Open Charge Point Protocol)** iletişimini ve **araç içi CAN veri yolu** etkileşimini simüle ederek, **siber güvenlik açısından anomali tespiti ve analizini** amaçlamaktadır.

Her ekip üyesi, belirli bir **anomali senaryosu** geliştirip sanal ortamda test edecek, sonuçlarını **SWOT analizi** ve **literatür incelemesi** ile destekleyecektir.

> **⚠️ Güvenlik Uyarısı:** Bu proje **akademik amaçlı** yürütülmekte olup **gerçek sistemler üzerinde herhangi bir test yapılmamaktadır**. Tüm deneyler, güvenli sanal ağlarda (`vcan0`, `localhost`, Python tabanlı simülasyon ortamı) gerçekleştirilir.

---

## ⚙️ Öne Çıkan İşlevler

- **OCPP iletişim simülasyonu:** CSMS ↔ CP ↔ CAN arasındaki veri akışının modellenmesi
- **CAN veri yolu trafiği:** `python-can` ve `vcan0` ile sanal araç verisi üretimi
- **Anomali senaryoları:** Her ekip üyesi tarafından özgün saldırı veya bozulma senaryosu
- **CAN Intrusion Detection System (IDS):** İstatistiksel ve kural-tabanlı anomali tespiti
- **MitM Proxy:** Plain WebSocket trafiğinde mesaj manipülasyonu simülasyonu
- **Loglama ve analiz:** Deney verilerinin toplanması, temizlenmesi ve istatistiksel analiz

---

## 🏗️ Proje Yapısı

```
bsg/
├── src/
│   ├── ocpp/                  # OCPP simülatörleri
│   │   ├── charge_point/      # CP (Charge Point) simülatör
│   │   │   └── simulator.py
│   │   └── central_system/    # CSMS simülatör
│   │       └── simulator.py
│   ├── can_bus/              # CAN-Bus simülasyonu
│   │   └── can_simulator.py  # vcan0 simülatörü
│   ├── bridge/               # OCPP-CAN köprü katmanı
│   │   ├── gateway.py        # Mesaj mapping ve dönüşüm
│   │   └── mapper.py         # OCPP ↔ CAN dönüşüm tabloları
│   ├── security/             # Güvenlik katmanları
│   │   └── tls_config.py     # TLS konfigürasyonları
│   ├── attacks/              # Saldırı simülasyonları
│   │   └── mitm_proxy.py     # MitM proxy
│   └── detection/            # Anomali tespit
│       └── can_ids.py        # CAN Intrusion Detection System
├── tests/                    # Test senaryoları
│   └── my_scenario.py        # Senaryo şablonu
├── config/                   # Yapılandırma dosyaları
│   ├── ocpp_config.yaml
│   └── can_config.yaml
├── scripts/                  # Yardımcı scriptler
│   ├── setup_vcan.sh         # vcan0 kurulumu
│   ├── generate_certs.sh     # Test sertifikaları
│   └── run_demo.sh           # Demo senaryoları
├── certs/                    # TLS sertifikaları
│   ├── weak/                 # Zayıf sertifikalar
│   └── strong/               # Güçlü sertifikalar
└── docs/                     # Dokümantasyon
    ├── README.md             # Bu dosya
    ├── START_HERE.md         # İlk adım rehberi
    ├── HOW_TO_SUBMIT_SCENARIO.md  # Senaryo gönderme rehberi
    ├── USAGE.md              # Kullanım örnekleri
    ├── INSTALL.md            # Kurulum kılavuzu
    ├── PROJECT_SUMMARY.md    # Teknik mimari
    └── QUICKSTART.md         # Hızlı başlangıç
```

---

## 🔌 OCPP-CAN Mapping

| OCPP Action | CAN ID | Payload | Yön | Açıklama |
|-------------|--------|---------|-----|----------|
| RemoteStartTransaction | 0x200 | [cp_id, connector_id, start_cmd] | CSMS→CP→CAN | Şarj başlatma komutu |
| RemoteStopTransaction | 0x201 | [tx_id, stop_cmd] | CSMS→CP→CAN | Şarj durdurma komutu |
| SetChargingProfile | 0x210 | [profile_id, max_current] | CSMS→CP→CAN | Şarj profil ayarı |
| MeterValues | 0x300 | [energy, voltage, current] | CAN→CP→CSMS | Enerji ölçüm verileri |

---

## 🧰 Kullanılan Teknolojiler

| Katman | Teknolojiler |
|--------|-------------|
| **Programlama Dili** | Python 3.10+ |
| **Simülasyon & Haberleşme** | `websockets`, `ocpp`, `python-can`, `asyncio` |
| **Veri Analizi** | `pandas`, `numpy`, `matplotlib` |
| **Test Framework** | `pytest` |
| **Sanal Ağ** | `vcan0` (Virtual CAN Interface) |
| **Güvenlik** | `cryptography`, `pyOpenSSL` |
| **Sürüm Kontrol** | Git & GitHub |

---

## 🚀 Hızlı Başlangıç

### 1. Gereksinimler (Linux)

```bash
sudo apt-get update
sudo apt-get install -y linux-modules-extra-$(uname -r) can-utils
```

### 2. Kurulum

```bash
# Repository'yi klonlayın
git clone https://github.com/sennaates/elektrikli-arac-sarj-istasyon-guvenligi-g10.git
cd elektrikli-arac-sarj-istasyon-guvenligi-g10

# Sanal ortam oluşturun
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# vcan0 arayüzünü kurun
chmod +x scripts/setup_vcan.sh
sudo ./scripts/setup_vcan.sh

# Test sertifikalarını oluşturun
chmod +x scripts/generate_certs.sh
./scripts/generate_certs.sh
```

### 3. İlk Demo

```bash
# Otomatik demo çalıştırın
bash scripts/run_demo.sh plain_ws
```

**Beklenen:** 3 terminal penceresi açılmalı ve çalışmalı.

---

## 📋 Güvenlik Senaryoları

### Senaryo 1: Plain WebSocket (Saldırıya Açık)
```bash
# Manuel çalıştırma
python -m src.ocpp.central_system.simulator --scenario plain_ws &
python -m src.ocpp.charge_point.simulator --scenario plain_ws &
python -m src.attacks.mitm_proxy
```

**Tehditler:** MitM, mesaj manipülasyonu, trafik dinleme

### Senaryo 2: Zayıf TLS
```bash
python -m src.ocpp.central_system.simulator --scenario weak_tls &
python -m src.ocpp.charge_point.simulator --scenario weak_tls
```

**Tehditler:** Zayıf cipher suites, self-signed sertifikalar

### Senaryo 3: Güçlü TLS (Önerilen)
```bash
python -m src.ocpp.central_system.simulator --scenario strong_tls &
python -m src.ocpp.charge_point.simulator --scenario strong_tls
```

**Koruma:** TLS 1.2/1.3, mutual TLS, güçlü sertifikalar

---

## 🔍 CAN Trafiği İzleme

```bash
# vcan0 trafiğini gerçek zamanlı izle
candump vcan0

# Belirli CAN ID'leri filtrele
candump vcan0 | grep "0x200\|0x201"

# ASCII formatında göster
canview vcan0
```

---

## 🧪 Kendi Senaryonuzu Yazın

### Hızlı Başlangıç

```bash
# 1. Şablon dosyayı kopyalayın
cp tests/my_scenario.py tests/my_anomaly.py

# 2. Düzenleyin
nano tests/my_anomaly.py

# 3. Test edin
pytest tests/my_anomaly.py -v -s
```

### Örnek Senaryo Yapısı

```python
@pytest.mark.asyncio
async def test_my_scenario():
    """Senaryo açıklaması"""
    # 1. CSMS başlat
    csms = CSMSimulator(host="localhost", port=9020, scenario="plain_ws")
    await csms.start()
    
    # 2. CP başlat
    cp = ChargePointSimulator(cp_id="CP_TEST", scenario="plain_ws")
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

**📖 Detaylı rehber:** [START_HERE.md](START_HERE.md) | [HOW_TO_SUBMIT_SCENARIO.md](HOW_TO_SUBMIT_SCENARIO.md)

---

## 📊 Test Senaryoları

```bash
# Tüm testleri çalıştır
pytest tests/ -v

# Coverage raporu
pytest tests/ --cov=src --cov-report=html

# Belirli senaryoyu test et
pytest tests/my_scenario.py -v -s
```

---

## 📚 Dokümantasyon

- **[START_HERE.md](START_HERE.md)** - 🚀 İlk adım rehberi (okumanız gerek!)
- **[QUICKSTART.md](QUICKSTART.md)** - Hızlı başlangıç kılavuzu
- **[HOW_TO_SUBMIT_SCENARIO.md](HOW_TO_SUBMIT_SCENARIO.md)** - 📤 Senaryo gönderme rehberi
- **[USAGE.md](USAGE.md)** - Manuel kullanım örnekleri
- **[INSTALL.md](INSTALL.md)** - Detaylı kurulum kılavuzu
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Teknik mimari ve tasarım

---

## 👥 Ekip Arkadaşları

- Sude Demir
- Sudem Cücemen
- Sena Ateş
- Enes Malik
- Uğur Berktaş
- İbrahim Kerem Güven
- Semih Tepe
- Özgün Deniz Sevilmiş
- Şerif Bayram
- Oğuzhan Erdoğan
- Selanur Ayaz

---

## 🎯 Proje Amacı

Bu çalışma, **araç içi ağ güvenliğini artırmak**, **blokzincir tabanlı doğrulama mekanizmalarını araştırmak** ve **akıllı ulaşım sistemleri** için güvenli bir veri iletişim altyapısı tasarlamak amacıyla yürütülmektedir.

Her öğrencinin geliştireceği anomali senaryosu, gelecekteki otonom ve bağlantılı araç güvenliği çözümlerine katkı sağlamayı hedeflemektedir.

---

## ⚠️ Güvenlik ve Etik Uyarıları

- ⛔ Tüm testler **yalnızca izole ağ ortamında** gerçekleştirilmeli
- ⛔ Gerçek şarj istasyonlarına veya canlı altyapılara asla erişim sağlanmamalı
- ⛔ Sorumlu disclosure prensipleri uygulanmalı
- ✅ Tüm log ve veriler anonimleştirilmeli

---

## 📊 Ölçülecek Metrikler

- **Gecikme (Latency)**: OCPP mesajı → CAN frame dönüşüm süresi
- **Başarı Oranı**: Başarılı mesaj iletimi yüzdesi
- **Tespit Oranı**: CAN IDS tarafından yakalanan anomali oranı
- **CPU/Bellek**: Sistem kaynak kullanımı

---

## 📚 Referanslar

- OCPP 1.6/2.0 Specification
- ISO 15118 (Vehicle to Grid Communication)
- CAN 2.0 Specification
- ISO/SAE 21434 (Cybersecurity Engineering)
- STRIDE Threat Modeling Framework

---

## 📄 Lisans

Bu proje akademik araştırma kapsamında geliştirilmiştir.

---

<div align="center">

**⭐ Projeyi beğendiyseniz star vermeyi unutmayın! ⭐**

Made with ❤️ by G10 Team

</div>
