# 📊 DASHBOARD TEST RAPORU

**Proje:** Elektrikli Araç Şarj İstasyonu Güvenliği - G10  
**Dashboard:** Streamlit Web Application  
**Port:** 8501 (Dashboard) / 8000 (API)  
**Tarih:** Aralık 2024

---

## 🎯 **PROJE ÖZETİ**

Bu proje, **OCPP (Open Charge Point Protocol)** ile **CAN-Bus** arasında güvenli bir köprü sistemi sunar. Sistem, **blockchain** tabanlı veri bütünlüğü ve **hibrit IDS (Intrusion Detection System)** ile gerçek zamanlı saldırı tespiti sağlar.

### **Temel Bileşenler:**

| Bileşen | Dosya | Port | Görev |
|---------|-------|------|-------|
| **API Server** | `api_server.py` | 8000 | REST API + WebSocket |
| **Dashboard** | `dashboard.py` | 8501 | Streamlit görselleştirme |
| **Secure Bridge** | `secure_bridge.py` | - | OCPP ↔ CAN dönüşümü |
| **CSMS Simulator** | `csms_simulator.py` | 9000 | Test CSMS sunucusu |
| **BSG Module** | `src/bsg/` | 9000 | Profesyonel OCPP simülatörü |
| **Attack Simulator** | `attack_simulator.py` | - | Saldırı test aracı |

---

## 📋 **DASHBOARD BİLEŞENLERİ**

### **1️⃣ Ana Başlık (Header)**
```
🔐 Secure OCPP-to-CAN Bridge
Real-Time Monitoring | Blockchain-Secured | ML-Powered IDS
```

### **2️⃣ Sidebar (Kontrol Paneli)**
```
├── ⚙️ Kontrol Paneli
│   ├── 🔄 Otomatik Yenileme (checkbox)
│   └── ⏱️ Yenileme Süresi (slider: 1-10 sn)
├── 📊 Filtreler
│   ├── 🚨 Alert'ler (checkbox)
│   ├── ⛓️ Blockchain (checkbox)
│   ├── 📡 Trafik (checkbox)
│   └── 🤖 ML-IDS (checkbox)
├── ✅ Sistem Durumu Göstergesi
└── 🌐 API URL Bilgisi
```

### **3️⃣ Ana Panel Bölümleri**

#### **A) KPI Kartları (4 Sütun)**
| Kart | İkon | Veri Kaynağı |
|------|------|--------------|
| Toplam Blok | 📦 | `/api/stats` → `blockchain.total_blocks` |
| Toplam Alert | 🚨 | `/api/alerts?count=100` |
| CAN Frame | 📡 | `/api/stats` → `ids.total_can_frames` |
| ML-IDS | 🤖 | `/api/stats` → `ml.is_trained` |

#### **B) Alert Bölümü**
- **Severity Distribution:** CRITICAL / HIGH / MEDIUM / LOW sayıları
- **Son Alert'ler:** Renk kodlu alert kartları (son 10)
- **Alert Kartı Formatı:**
  ```
  ┌─────────────────────────────────────────┐
  │ [SEVERITY BADGE]              [ZAMAN]   │
  │ ALERT_TYPE                              │
  │ Description text...                     │
  └─────────────────────────────────────────┘
  ```

#### **C) Blockchain Durumu**
- **Doğrulama Durumu:** ✅ GEÇERLİ / ❌ GEÇERSİZ
- **Genesis Hash:** İlk 20 karakter
- **En Son Hash:** İlk 20 karakter
- **Dijital İmza:** Etkin / Devre Dışı
- **Blok Tipi Dağılımı:** Pie chart (Plotly)
- **Son Bloklar Tablosu:** Index, Tip, Hash, Önceki Hash, Zaman

#### **D) Trafik Analizi**
- **CAN ID Frekansı:** Bar chart (Plotly)
- **OCPP Action Frekansı:** Bar chart (Plotly)

#### **E) Makine Öğrenmesi (ML-IDS)**
- **Model Durumu:** Eğitilmiş / Eğitilmemiş
- **Eğitim Verisi:** Örnek sayısı
- **Anomali Oranı:** Contamination değeri
- **Eğit Butonu:** "🎓 Modeli Eğit"

---

## 🎨 **TASARIM ÖZELLİKLERİ**

### **Renk Paleti (CSS Variables)**

```css
/* Alert Seviyeleri */
CRITICAL: #ef4444 (Kırmızı)
HIGH:     #f59e0b (Turuncu)
MEDIUM:   #eab308 (Sarı)
LOW:      #10b981 (Yeşil)

/* Gradient Temalar */
Header:   linear-gradient(135deg, #667eea 0%, #764ba2 100%)
Sidebar:  linear-gradient(180deg, #667eea 0%, #764ba2 100%)
Background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)

/* Blockchain */
VALID:    #10b981 (Yeşil gradient)
INVALID:  #ef4444 (Kırmızı gradient)
```

### **UI Özellikleri**
- **Glassmorphism:** Yarı saydam kartlar + backdrop-filter blur
- **Hover Efektleri:** Transform + box-shadow transitions
- **Custom Scrollbar:** Gradient renkli
- **Responsive Layout:** Wide layout (3-4 sütun)

---

## 🔌 **API ENDPOİNTLERİ**

### **REST API (Port 8000)**

| Endpoint | Metod | Açıklama |
|----------|-------|----------|
| `/` | GET | API bilgisi |
| `/api/health` | GET | Sistem sağlık durumu |
| `/api/stats` | GET | Tüm istatistikler |
| `/api/blockchain/stats` | GET | Blockchain istatistikleri |
| `/api/blockchain/blocks` | GET | Son N bloğu getir |
| `/api/blockchain/blocks/{index}` | GET | Belirli bloğu getir |
| `/api/blockchain/blocks/type/{type}` | GET | Tipteki blokları getir |
| `/api/ids/stats` | GET | IDS istatistikleri |
| `/api/alerts` | GET | Alert listesi |
| `/api/alerts` | POST | Alert ekle (test için) |
| `/api/bridge/register` | POST | Bridge state kaydet |
| `/api/bridge/status` | GET | Bridge durumu |
| `/api/ml/train` | GET | ML modelini eğit |
| `/api/ml/save` | POST | ML modelini kaydet |
| `/ws` | WebSocket | Real-time event stream |

### **WebSocket Mesaj Formatı**
```json
{
    "type": "alert | ocpp_message | can_frame | blockchain_update",
    "data": {...},
    "timestamp": 1702500000.0
}
```

---

## 🚀 **ÇALIŞTIRMA ADIMLARI**

### **Senaryo 1: Tam Sistem (Bridge + Dashboard)**

```bash
# Terminal 1: Virtual CAN (Linux)
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# Terminal 2: CSMS Simulator
python csms_simulator.py --port 9000

# Terminal 3: API Server
python api_server.py

# Terminal 4: Secure Bridge
python secure_bridge.py

# Terminal 5: Dashboard
streamlit run dashboard.py

# Tarayıcı: http://localhost:8501
```

### **Senaryo 2: BSG ile Duplicate Booking Testi**

```bash
# Terminal 1: BSG CSMS (Vulnerable Mode)
python -m src.bsg.cli server --port 9000 --vulnerable

# Terminal 2: Meşru Kullanıcı
python examples/1_legit_user.py

# Terminal 3: Saldırgan
python examples/2_attacker.py
```

### **Senaryo 3: Saldırı Simülasyonu**

```bash
# Terminal: Attack Simulator
python attack_simulator.py --attack injection
python attack_simulator.py --attack combined
python attack_simulator.py --attack all
python attack_simulator.py --attack mitm --mitm-scenario timing_anomaly
python attack_simulator.py --attack ocpp_flood --ocpp-rate 20 --ocpp-duration 5.0
```

---

## 📁 **PROJE DOSYA YAPISI**

```
elektrikli-arac-sarj-istasyon-guvenligi-g10/
├── 📂 src/                        # BSG OCPP Simülatör Paketi
│   └── bsg/
│       ├── __init__.py
│       ├── cli.py                 # CLI arayüzü
│       ├── chargepoint/
│       │   ├── __init__.py
│       │   └── simulator.py       # ChargePoint simülatörü
│       ├── csms/
│       │   ├── __init__.py
│       │   └── server.py          # CSMS sunucu (secure/vulnerable)
│       └── utils/
│           ├── __init__.py
│           └── logging.py
├── 📂 examples/                   # Örnek Senaryolar
│   ├── __init__.py
│   ├── 1_legit_user.py           # Meşru kullanıcı
│   └── 2_attacker.py             # Saldırgan (Duplicate Booking)
├── 📂 utils/                      # Güvenlik Altyapısı
│   ├── blockchain.py             # Blockchain core
│   ├── can_handler.py            # CAN-Bus interface
│   ├── ids.py                    # Rule-based IDS
│   └── ml_ids.py                 # ML-based IDS (Isolation Forest)
├── 📂 tests/                      # Test Senaryoları
│   ├── test_system.py
│   ├── scenario_01_mitm_ocpp_manipulation.py
│   ├── scenario_02_ocpp_dos_flooding.py
│   └── scenario_03_sampling_manipulation.py
├── 📂 training/
│   └── train_ml_model.py         # ML eğitim scripti
├── 🐍 api_server.py              # FastAPI REST API
├── 🐍 dashboard.py               # Streamlit Dashboard (~740 satır)
├── 🐍 secure_bridge.py           # Ana köprü servisi
├── 🐍 csms_simulator.py          # Test CSMS
├── 🐍 attack_simulator.py        # Saldırı simülatörü
├── 📄 pytest.ini                 # Test konfigürasyonu
├── 📄 requirements.txt           # Python bağımlılıkları
└── 📄 README.md                  # Ana dokümantasyon
```

---

## 📊 **DASHBOARD EKRAN GÖRÜNÜMÜ**

### **Bridge Aktif Değilken:**
```
┌─────────────────────────────────────────────────────────────┐
│  🔐 Secure OCPP-to-CAN Bridge                               │
│  Real-Time Monitoring | Blockchain-Secured | ML-Powered IDS │
├─────────────────────────────────────────────────────────────┤
│  ℹ️ Bridge henüz başlatılmamış. Veriler görünmeyecek.       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┬──────────┬──────────┬──────────┐             │
│  │ 📦 0     │ 🚨 0     │ 📡 0     │ 🤖 ⚠️   │             │
│  │ Toplam   │ Toplam   │ CAN      │ ML-IDS   │             │
│  │ Blok     │ Alert    │ Frame    │ Eğitilme.│             │
│  └──────────┴──────────┴──────────┴──────────┘             │
│                                                             │
│  🚨 Real-Time Alerts                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ✅ Sistem Güvenli                                   │   │
│  │     Hiç alert yok                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### **Bridge Aktifken + Saldırı Tespit:**
```
┌─────────────────────────────────────────────────────────────┐
│  ┌──────────┬──────────┬──────────┬──────────┐             │
│  │ 📦 156   │ 🚨 12    │ 📡 1,247 │ 🤖 ✅   │             │
│  │ Toplam   │ Toplam   │ CAN      │ ML-IDS   │             │
│  │ Blok     │ Alert    │ Frame    │ Aktif    │             │
│  └──────────┴──────────┴──────────┴──────────┘             │
│                                                             │
│  ┌──────────┬──────────┬──────────┬──────────┐             │
│  │🔴 3      │🟠 5      │🟡 3      │🟢 1      │             │
│  │CRITICAL  │HIGH      │MEDIUM    │LOW       │             │
│  └──────────┴──────────┴──────────┴──────────┘             │
│                                                             │
│  📋 Son Alert'ler                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [CRITICAL]                           14:19:28       │   │
│  │ CAN_FLOOD_ATTACK                                    │   │
│  │ Rate: 180 frame/s (Eşik: 100 frame/s)              │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [HIGH]                               14:19:41       │   │
│  │ UNAUTHORIZED_CAN_INJECTION                          │   │
│  │ CAN ID 0x200 whitelist'te değil                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ⛓️ Blockchain Durumu                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Doğrulama: ✅ GEÇERLİ                               │   │
│  │ Genesis:   b8e1a3f2c9d7e8...                       │   │
│  │ Son Hash:  a3f2c9d7e8b1a3...                       │   │
│  │ İmza:      ✅ Etkin                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  📋 Son Bloklar                                            │
│  ┌───────┬────────────┬──────────────┬──────────┐         │
│  │ Index │ Tip        │ Hash         │ Zaman    │         │
│  ├───────┼────────────┼──────────────┼──────────┤         │
│  │ 156   │ ALERT      │ b8e1a3f2...  │ 14:20:15 │         │
│  │ 155   │ CAN_FRAME  │ a3f2c9d7...  │ 14:20:12 │         │
│  │ 154   │ OCPP_MSG   │ 9d7e8b1a...  │ 14:20:09 │         │
│  └───────┴────────────┴──────────────┴──────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 **TEST SENARYOLARI**

### **Senaryo #1: MitM OCPP Manipulation**
```bash
python attack_simulator.py --attack mitm --mitm-scenario timing_anomaly
```
- **Hedef:** OCPP → CAN mapping
- **Tespit:** Timing anomaly (K1), Fingerprint (K2), Mapping (K3)

### **Senaryo #2: OCPP DoS Flooding**
```bash
python attack_simulator.py --attack ocpp_flood --ocpp-rate 20 --ocpp-duration 5.0
```
- **Hedef:** CSMS
- **Tespit:** Rate limiting (5 msg/s eşik)

### **Senaryo #3: Sampling Manipulation**
```bash
python attack_simulator.py --attack sampling --sampling-scenario rate_drop
python attack_simulator.py --attack sampling --sampling-scenario peak_smoothing
python attack_simulator.py --attack sampling --sampling-scenario buffer_manipulation
```
- **Hedef:** MeterValues / Enerji ölçümü
- **Tespit:** Sampling rate + Variance analysis

### **Senaryo #4: Duplicate Booking (BSG)**
```bash
# Vulnerable mode
python -m src.bsg.cli server --port 9000 --vulnerable
python examples/1_legit_user.py  # Terminal 2
python examples/2_attacker.py    # Terminal 3 → ⚠️ Saldırı başarılı

# Secure mode
python -m src.bsg.cli server --port 9000 --secure
python examples/1_legit_user.py  # Terminal 2
python examples/2_attacker.py    # Terminal 3 → 🛡️ Saldırı engellendi
```

---

## ⚙️ **KONFİGÜRASYON**

### **Dashboard Ayarları (dashboard.py)**
```python
API_URL = "http://127.0.0.1:8000"
REFRESH_INTERVAL = 3  # saniye (slider: 1-10)
MAX_ALERTS_DISPLAY = 10
```

### **API Server Ayarları (api_server.py)**
```python
API_HOST = "0.0.0.0"
API_PORT = 8000
```

### **Environment Variables (.env)**
```env
CSMS_URL=ws://localhost:9000/ocpp
CHARGE_POINT_ID=CP_001
CAN_INTERFACE=vcan0
ENABLE_ML_IDS=true
ANOMALY_THRESHOLD=0.7
API_PORT=8000
DASHBOARD_PORT=8501
```

---

## 📈 **PERFORMANS**

| Metrik | Değer | Hedef |
|--------|-------|-------|
| Dashboard Başlangıç | ~3s | < 5s |
| API Response Time | ~50ms | < 200ms |
| Auto-refresh Interval | 3s | 1-10s |
| Blockchain Write | ~0.5ms/blok | < 1ms |
| Rule-IDS Latency | < 1ms | < 5ms |
| ML-IDS Latency | ~10-15ms | < 50ms |

---

## 🛡️ **GÜVENLİK ÖZELLİKLERİ**

### **Blockchain**
- SHA-256 hash chain
- ECDSA dijital imza (opsiyonel)
- Tamper-evident logging
- Chain integrity verification

### **IDS Kuralları**
1. **Whitelist Validation:** Kayıtlı CAN ID'ler
2. **Authorization Check:** OCPP → CAN mapping
3. **Frequency Analysis:** Flood detection (100+ frame/s)
4. **Temporal Validation:** Replay detection
5. **ML Anomaly Score:** Isolation Forest

### **BSG Güvenlik Modları**
- **Vulnerable Mode:** Duplicate booking kabul edilir
- **Secure Mode:** Duplicate booking engellenir (reservation ID kontrolü)

---

## 📝 **NOTLAR**

1. **macOS/Windows:** `vcan0` yerine mock CAN kullanın veya standalone mode
2. **ML Model:** İlk eğitim için en az 100 örnek gerekli
3. **Dashboard:** Bridge olmadan temel metrikler görünür, detaylı veri için Bridge gerekli
4. **WebSocket:** Real-time event stream için `/ws` endpoint kullanın

---

**Proje Ekibi:** G10 - Elektrikli Araç Şarj İstasyonu Güvenliği  
**Üniversite:** IoT Security Research  
**Versiyon:** 1.0.0

---

**🚀 Dashboard'u başlatmak için:**
```bash
streamlit run dashboard.py
# Tarayıcı: http://localhost:8501
```
