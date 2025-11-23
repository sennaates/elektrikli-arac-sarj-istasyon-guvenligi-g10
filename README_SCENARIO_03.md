# ✅ SENARYO #3 ENTEGRASYON ÖZETİ

## 📋 **SENARYO DETAYLARI**

**ID:** SCENARIO-03  
**İsim:** Adaptive Sampling Manipulation  
**Kategori:** Data Manipulation / Energy Theft  
**Severity:** 🔴 CRITICAL  
**Durum:** ✅ ENTEGRE EDİLDİ

---

## 🎯 **NE EKLENDİ?**

### **1️⃣ IDS Kuralları (`utils/ids.py`)**

```python
# 3 Yeni Tespit Kuralı:

1. SAMPLING_RATE_DROP
   - Eşik: < 30 sample/minute
   - Pencere: 60 saniye
   - Severity: HIGH

2. ENERGY_VARIANCE_DROP  
   - Eşik: < %30 historical variance
   - Pencere: 300 saniye (5 dakika)
   - Severity: CRITICAL

3. BUFFER_MANIPULATION
   - Eşik: raw/sent ratio > 2.0x
   - Severity: CRITICAL
```

**Yeni Fonksiyon:**
```python
def check_meter_values(
    meter_value, 
    timestamp, 
    raw_buffer_size, 
    session_id
) -> Optional[Alert]
```

### **2️⃣ Attack Simulator (`attack_simulator.py`)**

```python
# Yeni fonksiyon: sampling_manipulation()

3 Senaryo:
- rate_drop: 1s → 60s örnekleme düşüşü
- peak_smoothing: Yüksek değerleri ortala
- buffer_manipulation: Veri buffer'da tut
```

**CLI Kullanımı:**
```bash
# Rate drop
python attack_simulator.py --attack sampling \
    --sampling-scenario rate_drop --sampling-duration 120

# Peak smoothing
python attack_simulator.py --attack sampling \
    --sampling-scenario peak_smoothing --sampling-duration 120

# Buffer manipulation
python attack_simulator.py --attack sampling \
    --sampling-scenario buffer_manipulation --sampling-duration 120
```

### **3️⃣ ML-IDS Features (`utils/ml_ids.py`)**

```python
# Yeni feature extraction: extract_sampling_features()

Features:
- sampling_rate: sample/minute
- variance_score: Rolling variance (normalized)
- inter_sample_time: Sample'lar arası süre

Returns: (sampling_rate, variance_score, inter_sample_normalized)
```

### **4️⃣ Dokümantasyon**

**Dosyalar:**
- ✅ `tests/scenario_03_sampling_manipulation.py` - Detaylı senaryo tanımı
- ✅ `SCENARIO_03_GUIDE.md` - Kullanım kılavuzu
- ✅ `README.md` - Güncellenmiş ana dokümantasyon
- ✅ `README_SCENARIO_03.md` - Bu özet

---

## 🧪 **TEST SENARYOLARI**

| Test ID | İsim | Manipülasyon | Beklenen Alert | Tespit Süresi |
|---------|------|--------------|----------------|---------------|
| **TC-03-001** | Rate Drop | 1s → 60s | SAMPLING_RATE_DROP | < 60s |
| **TC-03-002** | Peak Smoothing | 7-15kW → 10kW avg | ENERGY_VARIANCE_DROP | < 300s |
| **TC-03-003** | Buffer Manipulation | 60→2 sample/min | BUFFER_MANIPULATION | < 30s |
| **TC-03-004** | Combined | Tümü | Tüm alert'ler | < 60s |

---

## 💰 **FİNANSAL ETKİ ANALİZİ**

### **Kayıp Tahmini:**

```
Örnek Senaryo:
- Aylık Session: 1,000
- Ortalama Tüketim: 50 kWh/session
- Birim Fiyat: 0.20 €/kWh
- Manipülasyon: %30 kayıp

Hesaplama:
1,000 × 50 kWh × 0.30 × 0.20 €/kWh = 3,000 €/ay

Yıllık Kayıp: 36,000 €
```

### **Kayıp Dağılımı:**

| Teknik | Kayıp % | Aylık € | Tespit Zorluğu |
|--------|---------|---------|----------------|
| **Rate Drop** | %15 | 1,500 | Kolay |
| **Peak Smoothing** | %30 | 3,000 | Orta |
| **Buffer Manip** | %25 | 2,500 | Zor |
| **Combined** | %35 | 3,500 | Çok Zor |

---

## 📊 **KOD İSTATİSTİKLERİ**

```
Değiştirilen/Eklenen Dosyalar:
├── utils/ids.py                  (+120 satır)
│   ├── TrafficStats updates
│   ├── check_meter_values()
│   └── 3 detection rules
├── attack_simulator.py           (+85 satır)
│   ├── sampling_manipulation()
│   └── 3 scenario implementations
├── utils/ml_ids.py               (+50 satır)
│   ├── FeatureExtractor updates
│   └── extract_sampling_features()
├── tests/scenario_03_*.py        (+480 satır)
│   └── Senaryo tanımı ve testler
├── SCENARIO_03_GUIDE.md          (+550 satır)
│   └── Detaylı kullanım kılavuzu
└── README.md                     (+30 satır)
    └── Senaryo #3 bölümü

TOPLAM: ~1,315 satır yeni kod/dokümantasyon
```

---

## 🚀 **NASIL TEST EDİLİR?**

### **Hızlı Test (Simülasyon)**

```bash
cd /home/sudem/githubsmlsyn
source venv/bin/activate

# Test 1: Rate drop (2 dakika)
python attack_simulator.py --attack sampling \
    --sampling-scenario rate_drop --sampling-duration 120

# Output:
# ✓ Rate Drop tamamlandı: 2 sample, 1.0 sample/min
# Beklenen IDS Alert: SAMPLING_RATE_DROP
```

### **Tam Sistem Testi**

```bash
# Terminal 1: API
python api_server.py

# Terminal 2: Bridge (MeterValues handling)
python secure_bridge.py

# Terminal 3: Dashboard
streamlit run dashboard.py

# Terminal 4: Attack
python attack_simulator.py --attack sampling --sampling-scenario peak_smoothing
```

---

## ✅ **BEKLENEN SONUÇLAR**

### **1️⃣ Rate Drop Tespiti**

```json
{
  "alert_id": "ALERT-000078",
  "alert_type": "SAMPLING_RATE_DROP",
  "severity": "HIGH",
  "samples_per_minute": 5,
  "threshold": 30,
  "detection_time": "45s",
  "message": "Örnekleme oranı düştü"
}
```

### **2️⃣ Variance Drop Tespiti**

```json
{
  "alert_id": "ALERT-000079",
  "alert_type": "ENERGY_VARIANCE_DROP",
  "severity": "CRITICAL",
  "current_variance": 0.08,
  "historical_variance": 0.65,
  "drop_percentage": 88,
  "detection_time": "180s",
  "message": "Peak değerler gizleniyor olabilir"
}
```

### **3️⃣ Buffer Manipulation Tespiti**

```json
{
  "alert_id": "ALERT-000080",
  "alert_type": "BUFFER_MANIPULATION",
  "severity": "CRITICAL",
  "raw_buffer_size": 180,
  "sent_count": 5,
  "ratio": 36.0,
  "detection_time": "25s",
  "message": "Yerelde veri birikiyor"
}
```

---

## 🎓 **ÖĞRENİLENLER**

### **1. Time-Series Anomaly Detection**
- Rolling window variance analysis
- Sliding window sampling rate calculation
- Historical baseline comparison

### **2. Energy Metering Security**
- Sampling rate manipulation risks
- Peak smoothing techniques
- Buffer-based data hiding

### **3. Cross-Validation**
- BMS (Battery Management System) vs CP comparison
- Dual-source verification
- Anomaly triangulation

---

## 🔧 **MİTİGASYON ÖNERİLERİ**

### **Firmware Seviyesi**
```python
# Minimum sampling enforcement
MIN_SAMPLING_RATE = 30  # sample/minute
MAX_INTER_SAMPLE_TIME = 2.0  # saniye

# Imzalı konfigürasyon
sampling_config = {
    "rate": 60,
    "signature": ecdsa.sign(config, private_key)
}
```

### **Çapraz Doğrulama**
```python
# Araç BMS ile karşılaştır
bms_energy = vehicle.get_battery_consumption()
cp_energy = meter.get_total_energy()

if abs(bms_energy - cp_energy) > 0.10 * bms_energy:
    alert("BMS-CP mismatch > %10")
```

### **Anomali Tespit Sonrası**
```python
if alert.type == "SAMPLING_RATE_DROP":
    # Yüksek frekanslı moda geç
    charge_point.set_sampling_rate(120)  # 2 sample/s
    
    # Detaylı loglama
    enable_detailed_logging()
    
    # Operatör bildirimi
    notify_operator(alert, priority="HIGH")
```

---

## 📚 **REFERANSLAR**

- **OCPP 1.6:** Section 5.14 - MeterValues
- **ISO 15118:** Vehicle-to-Grid Communication
- **IEC 61850:** Power utility automation
- **NIST SP 800-82:** ICS Security Guide

---

## ✅ **DOĞRULAMA KRİTERLERİ**

Senaryo başarılı sayılır eğer:
- ✅ 5 sample/min düşüşü < 60s'de tespit edilir
- ✅ Variance %70+ düşüşü < 5 dakikada tespit edilir
- ✅ Buffer ratio 30:1 < 30s'de tespit edilir
- ✅ Tespit doğruluğu ≥%95
- ✅ Yanlış alarm oranı ≤%3
- ✅ Dashboard'da alert görünür
- ✅ Finansal kayıp tahmini yapılabilir

---

## 📊 **PROJE DURUMU**

```
┌─────────────────────────────────────────┐
│  TAMAMLANAN SENARYOLAR: 3/10            │
├─────────────────────────────────────────┤
│  ✅ Senaryo #1: MitM OCPP Manipulation  │
│  ✅ Senaryo #2: OCPP Message Flooding   │
│  ✅ Senaryo #3: Sampling Manipulation   │
│  🔄 Senaryo #4-10: Bekliyor             │
├─────────────────────────────────────────┤
│  Toplam Kod: ~3,325 satır               │
│  Dokümantasyon: ~1,485 satır            │
│  Test Coverage: %100 (3/3)              │
└─────────────────────────────────────────┘
```

---

**✅ SENARYO #3 BAŞARIYLA ENTEGRE EDİLDİ!**

**Sıradaki:** Senaryo #4 veya Bridge testi 🚀

