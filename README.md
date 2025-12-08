# 🔐 Secure OCPP-to-CAN Bridge

**Blockchain-Secured Automotive Gateway with ML-Powered Intrusion Detection**

---

## 📋 Proje Özeti

Bu proje, **OCPP (Open Charge Point Protocol)** komutlarını **CAN-Bus** frame'lerine çeviren güvenli bir köprü sistemidir. Sistem, **blockchain teknolojisi** ile veri bütünlüğünü garanti altına alır ve **hibrit IDS (Intrusion Detection System)** ile gerçek zamanlı saldırı tespiti yapar.

### 🎯 Temel Özellikler

- ⛓️ **Blockchain-Based Security**: Her OCPP ve CAN mesajı SHA-256 hash chain'e kaydedilir
- 🛡️ **Hybrid IDS**: Rule-based + ML-based (Isolation Forest) anomali tespiti
- 🔐 **Digital Signature**: ECDSA ile blok imzalama
- 📊 **Real-Time Dashboard**: Streamlit ile canlı izleme
- 🚨 **Alert System**: Otomatik saldırı tespiti ve alarm
- 🤖 **ML-Ready**: Scikit-learn ile eğitilebilir anomali modeli
- 🧪 **Attack Simulator**: Test senaryoları için saldırı simülatörü

---

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                    CSMS (WebSocket Server)                   │
└─────────────────────────────────────────────────────────────┘
                            ▼ OCPP 1.6
┌─────────────────────────────────────────────────────────────┐
│              SECURE BRIDGE (secure_bridge.py)               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  OCPP Client  →  Blockchain  →  IDS  →  CAN Handler  │  │
│  └───────────────────────────────────────────────────────┘  │
│                      ▲                  ▼                    │
│                   FastAPI          vcan0 (CAN Bus)          │
└─────────────────────────────────────────────────────────────┘
              ▼                                    ▲
    ┌──────────────────┐                  ┌────────────────┐
    │   Dashboard      │                  │    Attack      │
    │  (Streamlit)     │                  │   Simulator    │
    └──────────────────┘                  └────────────────┘
```

### 📦 Bileşenler

| Bileşen | Teknoloji | Görev |
|---------|-----------|-------|
| **Bridge** | Python + asyncio | OCPP ↔ CAN dönüşümü ve güvenlik |
| **Blockchain** | SHA-256 + ECDSA | Tamper-evident logging |
| **Rule-IDS** | Custom logic | Bilinen saldırı kalıpları |
| **ML-IDS** | Isolation Forest | Bilinmeyen anomali tespiti |
| **API** | FastAPI + WebSocket | Dashboard entegrasyonu |
| **Dashboard** | Streamlit + Plotly | Real-time monitoring |

---

## 🚀 Kurulum

### 1. Sistem Gereksinimleri

- **OS**: Linux (Ubuntu 20.04+, Debian, Arch vb.)
- **Python**: 3.9+
- **CAN Interface**: `vcan0` (sanal) veya gerçek CAN adaptör

### 2. Bağımlılıkları Kur

```bash
# Python virtual environment oluştur
python3 -m venv venv
source venv/bin/activate

# Paketleri kur
pip install -r requirements.txt
```

### 3. Virtual CAN (vcan0) Kurulumu

```bash
# vcan modülünü yükle
sudo modprobe vcan

# vcan0 interface oluştur
sudo ip link add dev vcan0 type vcan

# Interface'i aktif et
sudo ip link set up vcan0

# Doğrula
ip link show vcan0
```

### 4. Konfigürasyon

`.env` dosyası oluştur (`.env.example`'dan kopyala):

```bash
cp .env.example .env
nano .env
```

**Temel ayarlar:**
```env
# OCPP
CSMS_URL=ws://localhost:9000/ocpp
CHARGE_POINT_ID=CP_001

# CAN-Bus
CAN_INTERFACE=vcan0

# IDS
ENABLE_ML_IDS=true
ANOMALY_THRESHOLD=0.7

# API
API_PORT=8000

# Dashboard
DASHBOARD_PORT=8501
```

---

## 🧪 Test ve Eğitim

### 1. Sistem Testlerini Çalıştır

```bash
python tests/test_system.py
```

**Beklenen çıktı:**
```
✅ Blockchain: BAŞARILI
✅ OCPP → CAN Mapping: BAŞARILI
✅ Rule-Based IDS: BAŞARILI
✅ ML-Based IDS: BAŞARILI
✅ Feature Extraction: BAŞARILI
```

### 2. ML Modelini Eğit

```bash
python training/train_ml_model.py
```

Bu script:
- 1000 normal trafik örneği üretir
- Isolation Forest modelini eğitir
- `./models/isolation_forest.pkl` olarak kaydeder

---

## ▶️ Kullanım

### Senaryo 1: Tam Sistem (OCPP + CAN + Dashboard)

**Terminal 1: CSMS Sunucusu (Simüle)**
```bash
# Basit OCPP WebSocket sunucusu (test için)
# Not: Gerçek bir CSMS kullanabilirsiniz
python -m websockets ws://localhost:9000/ocpp
```

**Terminal 2: Secure Bridge**
```bash
python secure_bridge.py
```

**Terminal 3: API Server**
```bash
python api_server.py
```

**Terminal 4: Dashboard**
```bash
streamlit run dashboard.py
```

Dashboard'a tarayıcıdan erişin: `http://localhost:8501`

---

### Senaryo 2: Standalone CAN Monitoring (OCPP olmadan)

```bash
# OCPP sunucusu olmadan sadece CAN-Bus dinle
python secure_bridge.py
```

Sistem otomatik olarak "standalone mode"a geçer.

---

### Senaryo 3: Saldırı Simülasyonu

**Terminal 5: Attack Simulator**

```bash
# Tek saldırı tipi
python attack_simulator.py --attack injection

# Kombine saldırı
python attack_simulator.py --attack combined

# Tüm saldırılar
python attack_simulator.py --attack all
```

**Dashboard'da göreceksiniz:**
- 🚨 Kırmızı alert'ler
- 📈 CAN frame frekansı artışı
- ⛓️ Blockchain'e kaydedilen alert blokları

---

### 🆕 Senaryo 4: Duplicate Booking Attack (BSG Modülü)

Bu senaryo, profesyonel OCPP simülatörü (`src/bsg/`) kullanarak **Duplicate Booking** saldırısını gösterir.

**Terminal 1: CSMS Sunucusu (Vulnerable Mode)**
```bash
# Güvenlik açığı olan mod
python -m src.bsg.cli server --port 9000 --vulnerable
```

**Terminal 2: Meşru Kullanıcı**
```bash
python examples/1_legit_user.py
```

**Terminal 3: Saldırgan (Aynı Reservation ID ile)**
```bash
python examples/2_attacker.py
```

**Beklenen Sonuç (Vulnerable Mode):**
- ⚠️ Saldırgan aynı reservation ID ile şarj başlatabilir
- İki işlem aynı anda aktif olur (güvenlik açığı)

**Terminal 1: CSMS Sunucusu (Secure Mode)**
```bash
# Güvenli mod
python -m src.bsg.cli server --port 9000 --secure
```

**Beklenen Sonuç (Secure Mode):**
- 🛡️ Saldırganın isteği reddedilir
- Yalnızca meşru kullanıcının işlemi aktif kalır

---

## 🎯 Saldırı Senaryoları

### **Temel Saldırılar**

| Saldırı | Açıklama | Tespit Yöntemi |
|---------|----------|----------------|
| **Unauthorized Injection** | Bridge'den bağımsız CAN frame | Rule-IDS (whitelist check) |
| **CAN Flood** | Saniyede 100+ frame | Rule-IDS (frequency analysis) |
| **Replay Attack** | Aynı mesajın tekrarı | Rule-IDS (timestamp + hash) |
| **Invalid CAN ID** | Whitelist dışı ID | Rule-IDS (ID check) |
| **High Entropy** | Rastgele payload | ML-IDS (entropy calculation) |

### **🎓 Gelişmiş Anomali Senaryoları**

#### **📋 Senaryo #1: MitM OCPP Manipulation**
- **Tip:** Man-in-the-Middle Attack
- **Hedef:** OCPP → CAN mapping
- **Yöntem:** RemoteStart'ı RemoteStop'a çevirme
- **Tespit:** K1 (Timing), K2 (Fingerprint), K3 (Mapping)
- **Dokümantasyon:** `SCENARIO_01_GUIDE.md`

**Test:**
```bash
python attack_simulator.py --attack mitm --mitm-scenario timing_anomaly
```

#### **📋 Senaryo #2: OCPP Message Flooding (DoS)**
- **Tip:** Denial of Service
- **Hedef:** CSMS (Merkezi Yönetim Sistemi)
- **Yöntem:** 20+ mesaj/saniye bombardımanı
- **Tespit:** Rate limiting + ML burst detection
- **Dokümantasyon:** `SCENARIO_02_GUIDE.md`

**Test:**
```bash
python attack_simulator.py --attack ocpp_flood --ocpp-rate 20 --ocpp-duration 5.0
```

**IDS Kuralları:**
- **Eşik:** 5 mesaj/saniye
- **Pencere:** 1 saniye
- **Müdahale Süresi:** < 30 saniye
- **Doğruluk:** ≥%95

#### **📋 Senaryo #3: Sampling Manipulation (Energy Theft)**
- **Tip:** Data Manipulation / Energy Theft
- **Hedef:** MeterValues / Enerji Ölçüm Sistemi
- **Yöntem:** Örnekleme oranı düşürme + Peak gizleme
- **Tespit:** Sampling rate + Variance analysis + Buffer monitoring
- **Dokümantasyon:** `SCENARIO_03_GUIDE.md`

**Test:**
```bash
# Rate drop (1s → 60s)
python attack_simulator.py --attack sampling --sampling-scenario rate_drop

# Peak smoothing (yüksek değerleri ortala)
python attack_simulator.py --attack sampling --sampling-scenario peak_smoothing

# Buffer manipulation (veri gönderme)
python attack_simulator.py --attack sampling --sampling-scenario buffer_manipulation
```

**IDS Kuralları:**
- **Kural-1:** samples/min < 30 → `SAMPLING_RATE_DROP`
- **Kural-2:** variance drop > %70 → `ENERGY_VARIANCE_DROP`
- **Kural-3:** raw/sent ratio > 2x → `BUFFER_MANIPULATION`
- **Finansal Etki:** %15-30 gelir kaybı

---

---

## 🆕 BSG Modülü API

### ChargePointSimulator

```python
from src.bsg.chargepoint import ChargePointSimulator

# Yeni ChargePoint oluştur
cp = ChargePointSimulator(
    charge_point_id="CP_001",
    csms_url="ws://localhost:9000"
)

# Bağlan
await cp.start()

# İşlem başlat
response = await cp.send_start_transaction(
    reservation_id="RES_12345",
    id_tag="USER_001",
    connector_id=1
)

# İşlem durdur
await cp.send_stop_transaction(transaction_id=response['transaction_id'])

# Bağlantıyı kapat
await cp.stop()
```

### CSMSimulator

```python
from src.bsg.csms import CSMSimulator

# CSMS sunucusu oluştur
csms = CSMSimulator(
    host="0.0.0.0",
    port=9000,
    secure_mode=True  # Güvenli mod (duplicate booking engellenir)
)

# Sunucuyu başlat
await csms.start()

# İstatistikleri al
stats = csms.get_statistics()

# Sunucuyu durdur
await csms.stop()
```

### CLI Kullanımı

```bash
# Sunucu başlat (güvenli mod)
python -m src.bsg.cli server --port 9000 --secure

# Sunucu başlat (güvenlik açığı modu)
python -m src.bsg.cli server --port 9000 --vulnerable

# Yardım
python -m src.bsg.cli --help
```

---

## 📊 API Endpoints

| Endpoint | Metod | Açıklama |
|----------|-------|----------|
| `/api/health` | GET | Sistem sağlık durumu |
| `/api/blockchain/stats` | GET | Blockchain istatistikleri |
| `/api/blockchain/blocks` | GET | Son N bloğu getir |
| `/api/ids/stats` | GET | IDS istatistikleri |
| `/api/alerts` | GET | Alert listesi |
| `/api/ml/train` | GET | ML modelini eğit |
| `/ws` | WebSocket | Real-time event stream |

**Örnek kullanım:**
```bash
# Blockchain istatistikleri
curl http://localhost:8000/api/blockchain/stats

# Son 5 alert
curl http://localhost:8000/api/alerts?count=5&severity=HIGH
```

---

## 🔬 Anomali Senaryoları İçin Hazırlık

### Senaryoları Eklemek İçin:

1. `tests/anomaly_scenarios.py` oluştur:

```python
ANOMALY_SCENARIOS = [
    {
        "name": "Replay Attack",
        "description": "Eski OCPP mesajını tekrar gönder",
        "steps": [...],
        "expected_detection": "Rule-based IDS (timestamp check)"
    },
    # Senin 10 senaryonu buraya
]
```

2. `attack_simulator.py`'ye yeni fonksiyon ekle
3. `dashboard.py`'de senaryoya özel metrik görüntüle

---

## 📈 Performans Metrikleri

Test ortamında (Intel i5, 8GB RAM):

- **Blockchain write**: ~0.5ms/blok
- **Rule-IDS latency**: <1ms
- **ML-IDS latency**: ~10-15ms
- **CAN frame throughput**: 1000+ frame/s
- **Dashboard refresh**: 3s (configurable)

---

## 🛡️ Güvenlik Özellikleri

### Blockchain Bütünlüğü
- Her blok önceki bloğun hash'ini içerir
- SHA-256 hash algoritması
- ECDSA dijital imza (opsiyonel)
- Tamper-evident: Herhangi bir değişiklik zinciri kırar

### IDS Kuralları
1. **Whitelist Validation**: Sadece kayıtlı CAN ID'ler
2. **Authorization Check**: OCPP → CAN mapping doğrulama
3. **Frequency Analysis**: Flood detection
4. **Temporal Validation**: Replay detection
5. **ML Anomaly Score**: Threshold-based classification

---

## 🧩 Modüler Yapı

```
elektrikli-arac-sarj-istasyon-guvenligi-g10/
├── src/                       # 🆕 Professional OCPP Simulator Package
│   └── bsg/
│       ├── __init__.py
│       ├── cli.py             # CLI arayüzü (server komutu)
│       ├── chargepoint/
│       │   ├── __init__.py
│       │   └── simulator.py   # ChargePoint simülatörü
│       ├── csms/
│       │   ├── __init__.py
│       │   └── server.py      # CSMS sunucu simülatörü
│       └── utils/
│           ├── __init__.py
│           └── logging.py     # Logging utilities
├── examples/                  # 🆕 Örnek Senaryolar
│   ├── __init__.py
│   ├── 1_legit_user.py        # Meşru kullanıcı simülasyonu
│   └── 2_attacker.py          # Saldırgan simülasyonu (Duplicate Booking)
├── utils/
│   ├── blockchain.py          # Blockchain core
│   ├── can_handler.py         # CAN-Bus interface
│   ├── ids.py                 # Rule-based IDS
│   └── ml_ids.py              # ML-based IDS
├── secure_bridge.py           # Ana bridge servisi
├── api_server.py              # REST API + WebSocket
├── dashboard.py               # Streamlit dashboard
├── attack_simulator.py        # Saldırı simülatörü
├── csms_simulator.py          # Basit CSMS (test için)
├── training/
│   └── train_ml_model.py      # ML eğitim scripti
├── tests/
│   ├── test_system.py         # Birim testleri
│   ├── scenario_01_mitm_ocpp_manipulation.py
│   ├── scenario_02_ocpp_dos_flooding.py
│   └── scenario_03_sampling_manipulation.py
├── models/                    # Eğitilmiş ML modelleri
├── logs/                      # Log dosyaları
├── pytest.ini                 # 🆕 Pytest konfigürasyonu
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔧 Sorun Giderme

### Problem: `vcan0: No such device`

**Çözüm:**
```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

### Problem: `OCPP connection failed`

**Çözüm:**
- CSMS sunucusunun çalıştığından emin olun
- `.env` dosyasındaki `CSMS_URL` doğru mu kontrol edin
- Firewall kurallarını kontrol edin

### Problem: `sklearn not found`

**Çözüm:**
```bash
pip install scikit-learn numpy pandas
```

### Problem: Dashboard açılmıyor

**Çözüm:**
```bash
# API sunucusunun çalıştığından emin olun
curl http://localhost:8000/api/health

# Streamlit'i restart edin
streamlit run dashboard.py --server.port 8501
```

---

## 📚 Referanslar

### Kullanılan Teknolojiler
- **OCPP**: [Open Charge Point Protocol](https://www.openchargealliance.org/)
- **CAN-Bus**: [python-can](https://python-can.readthedocs.io/)
- **Blockchain**: Custom implementation (SHA-256 + ECDSA)
- **ML**: [scikit-learn Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- **API**: [FastAPI](https://fastapi.tiangolo.com/)
- **Dashboard**: [Streamlit](https://streamlit.io/)

### İlgili Makaleler
1. Koscher et al. (2010) - "Experimental Security Analysis of a Modern Automobile"
2. Miller & Valasek (2015) - "Remote Exploitation of an Unaltered Passenger Vehicle"
3. Cho & Shin (2016) - "Error Handling of In-Vehicle Networks Makes Them Vulnerable"

---

## 👥 Katkıda Bulunma

Bu proje eğitim amaçlıdır. Geliştirme önerileri için:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

---

## ⚠️ Yasal Uyarı

**ÖNEMLİ:** Bu sistem yalnızca **eğitim ve araştırma** amaçlıdır.

- ✅ İzole test ortamlarında kullanın
- ✅ Sanal CAN (vcan0) ile test edin
- ✅ Kendi ekipmanlarınızda çalıştırın
- ❌ Gerçek araçlarda izinsiz test yapmayın
- ❌ Üretime alınmış sistemlerde kullanmayın
- ❌ Yasadışı aktiviteler için kullanmayın

**Etik Kurallar:**
- Tüm testler yazılı izin ile yapılmalıdır
- Loglar ve sonuçlar gizli tutulmalıdır
- Bulgu paylaşımı responsible disclosure ile yapılmalıdır

---

## 📝 Lisans

Bu proje MIT lisansı altındadır. Detaylar için `LICENSE` dosyasına bakın.

---

## 📧 İletişim

**Proje Sahibi:** University IoT Security Research Team  
**E-posta:** [proje-mail@example.com]  
**GitHub:** https://github.com/your-repo/secure-ocpp-can-bridge

---

## 🎓 Akademik Kullanım

Bu projeyi akademik çalışmanızda kullanıyorsanız lütfen şu şekilde atıf yapın:

```bibtex
@misc{secure_ocpp_can_bridge_2024,
  title={Secure OCPP-to-CAN Bridge: Blockchain-Based Automotive Security},
  author={University Research Team},
  year={2024},
  url={https://github.com/your-repo/secure-ocpp-can-bridge}
}
```

---

**🚀 Projeyi başarıyla çalıştırdıysanız, lütfen ⭐ verin!**

---

## 🔄 Versiyon Geçmişi

### v1.0.0 (2024-11-23)
- ✅ İlk stabil sürüm
- ✅ Blockchain implementasyonu
- ✅ Hybrid IDS (Rule + ML)
- ✅ Streamlit Dashboard
- ✅ Attack Simulator
- ✅ Kapsamlı dokümantasyon

