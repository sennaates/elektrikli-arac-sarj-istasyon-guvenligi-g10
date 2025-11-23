```markdown
# 📋 SENARYO #3: ADAPTİF ÖRNEKLEME MANİPÜLASYONU

## 🎯 **ÖZET**

**Saldırı Tipi:** Data Manipulation / Energy Theft  
**Hedef:** MeterValues / Enerji Ölçüm Sistemi  
**Yöntem:** Örnekleme oranı düşürme + Peak değerleri gizleme  
**Tespit:** Sampling rate + Variance analysis + Buffer monitoring  
**Severity:** 🔴 CRITICAL

---

## 📊 **SENARYO DETAYLARI**

### **Saldırı Mekanizması**

```
NORMAL DURUM:
┌────────────────────────────────────────┐
│  Charge Point (CP)                    │
│  ✅ 60 sample/minute (her saniye)     │
│  ✅ Yüksek varyans (peak'ler görünür) │
│  ✅ Raw = Sent (1:1)                  │
└─────────────────┬──────────────────────┘
                  │
                  ▼
         [ CSMS Metering System ]
         ✅ Doğru faturalandırma
         ✅ Peak load algılama


MANİPÜLE EDİLMİŞ DURUM:
┌────────────────────────────────────────┐
│  Charge Point (Compromised)           │
│  ❌ 1 sample/minute (her 60 saniye)   │
│  ❌ Düşük varyans (peak'ler gizli)    │
│  ❌ Raw:Sent = 30:1 (buffer dolu)     │
└─────────────────┬──────────────────────┘
                  │
                  ▼
         [ CSMS Metering System ]
         ❌ Eksik ücretlendirme (%15-30)
         ❌ Peak load görünmez
         ❌ Kapasite planlama hatası
```

### **3 Manipülasyon Tekniği**

#### **1️⃣ Rate Drop (Örnekleme Düşürme)**
```
Normal:    |---|---|---|---|---|  (1 sample/s)
Manipüle:  |----------(60s)-------|  (1 sample/60s)

Sonuç: Kısa süreli yüksek tüketimler kaçırılır
```

#### **2️⃣ Peak Smoothing (Tepe Düzeltme)**
```
Real Power:  [7kW, 14kW, 8kW, 15kW, 9kW]
Sent Power:  [10.6kW]  (ortalama)

Sonuç: 15kW peak görünmez, fatura düşük
```

#### **3️⃣ Buffer Manipulation (Veri Tutma)**
```
Raw Buffer:  180 samples (cihazda)
Sent:        5 samples (CSMS'e)
Ratio:       36:1

Sonuç: Çoğu veri hiç gönderilmez
```

---

## 🛡️ **TESPİT YÖNTEMLERİ**

### **Kural-1: SAMPLING_RATE_DROP**

**Koşul:** `samples_per_minute < 30`  
**Eşik:** 30 sample/minute  
**Pencere:** 60 saniye

```python
# utils/ids.py
recent_samples = [
    (t, v) for t, v in meter_samples 
    if timestamp - t <= 60.0
]
samples_per_minute = len(recent_samples)

if samples_per_minute < 30:
    alert = "SAMPLING_RATE_DROP"
```

### **Kural-2: ENERGY_VARIANCE_DROP**

**Koşul:** `current_variance < historical_variance * 0.30`  
**Eşik:** %30 düşüş  
**Pencere:** 300 saniye (5 dakika)

```python
current_variance = np.var(recent_values)
historical_variance = np.var(old_values)

if current_variance < historical_variance * 0.30:
    alert = "ENERGY_VARIANCE_DROP"
    # Peak değerler gizleniyor!
```

### **Kural-3: BUFFER_MANIPULATION**

**Koşul:** `raw_buffer_size / sent_count > 2.0`  
**Eşik:** 2x ratio

```python
buffer_ratio = raw_buffer_size / sent_sample_count

if buffer_ratio > 2.0:
    alert = "BUFFER_MANIPULATION"
    # Yerelde veri birikiyor!
```

---

## 🚀 **SALDIRI SİMÜLASYONU**

### **Test 1: Rate Drop**

```bash
python attack_simulator.py --attack sampling \
    --sampling-scenario rate_drop \
    --sampling-duration 120
```

**Beklenen Çıktı:**
```
🚨 SALDIRI: Sampling Manipulation başlatılıyor...
   Senaryo: rate_drop
   [Simülasyon] Normal örnekleme: 1 sample/saniye
   [Manipülasyon] Örnekleme oranı düşürülüyor → 1 sample/60 saniye
   
✓ Rate Drop tamamlandı: 2 sample, 1.0 sample/min
   Beklenen IDS Alert: SAMPLING_RATE_DROP
```

### **Test 2: Peak Smoothing**

```bash
python attack_simulator.py --attack sampling \
    --sampling-scenario peak_smoothing \
    --sampling-duration 120
```

**Beklenen Alert:**
```json
{
  "alert_type": "ENERGY_VARIANCE_DROP",
  "severity": "CRITICAL",
  "current_variance": 0.08,
  "historical_variance": 0.65,
  "drop_ratio": 0.12,
  "note": "Peak değerler gizleniyor olabilir"
}
```

### **Test 3: Buffer Manipulation**

```bash
python attack_simulator.py --attack sampling \
    --sampling-scenario buffer_manipulation \
    --sampling-duration 120
```

**Beklenen Log:**
```
[Buffer] 180 raw | [Sent] 6 | Ratio: 30.0x
🚨 CRITICAL: BUFFER_MANIPULATION
   Yerelde veri birikiyor → Manipülasyon şüphesi
```

---

## 📈 **BEKLENEN SONUÇLAR**

### **✅ Başarılı Tespit Örneği**

```json
{
  "session_id": "SESSION-12345",
  "timestamp": "2025-11-23 12:34:56",
  "alerts": [
    {
      "alert_type": "SAMPLING_RATE_DROP",
      "severity": "HIGH",
      "samples_per_minute": 5,
      "threshold": 30,
      "detection_time": "45s"
    },
    {
      "alert_type": "ENERGY_VARIANCE_DROP",
      "severity": "CRITICAL",
      "current_variance": 0.08,
      "historical_variance": 0.65,
      "drop_percentage": 88,
      "detection_time": "180s"
    },
    {
      "alert_type": "BUFFER_MANIPULATION",
      "severity": "CRITICAL",
      "raw_buffer": 180,
      "sent_count": 5,
      "ratio": 36.0,
      "detection_time": "25s"
    }
  ]
}
```

### **💰 Finansal Etki Analizi**

| Senaryo | Gerçek Tüketim | Faturalanan | Kayıp | Kayıp % |
|---------|----------------|-------------|-------|---------|
| **Normal** | 10.0 kWh | 10.0 kWh | 0 | %0 |
| **Rate Drop** | 10.0 kWh | 8.5 kWh | 1.5 kWh | %15 |
| **Peak Smoothing** | 10.0 kWh | 7.0 kWh | 3.0 kWh | %30 |
| **Combined** | 10.0 kWh | 6.5 kWh | 3.5 kWh | %35 |

**Örnek Hesaplama:**
- Aylık 1000 session
- Ortalama 50 kWh/session
- Birim fiyat: 0.20 €/kWh
- **Aylık Kayıp:** 1000 × 50 × 0.30 × 0.20 = **3,000 €**

---

## 🧪 **TEST SENARYOLARI**

### **TC-03-001: Rate Drop Detection**

**Hedef:** 60s interval'e düşürülen örneklemeyi tespit et

**Adımlar:**
1. Normal başlat (1 sample/s)
2. 30 saniye sonra → 60s interval'e geç
3. IDS tespiti bekle

**Beklenen:**
- ✅ Alert: `SAMPLING_RATE_DROP`
- ✅ Tespit süresi: < 60 saniye
- ✅ Dashboard: Kırmızı alarm

### **TC-03-002: Peak Smoothing Detection**

**Hedef:** Ortalama ile gizlenen peak'leri tespit et

**Adımlar:**
1. Yüksek varyans oluştur (7-15 kW)
2. Her 10 sample'ı ortala ve gönder
3. Variance düşüşünü izle

**Beklenen:**
- ✅ Alert: `ENERGY_VARIANCE_DROP`
- ✅ Variance drop: > %70
- ✅ Tespit süresi: < 5 dakika

### **TC-03-003: Buffer Manipulation Detection**

**Hedef:** Buffer'da biriken veriyi tespit et

**Adımlar:**
1. Her saniye raw sample üret (60/min)
2. Her 30 saniyede 1 sample gönder (2/min)
3. Buffer ratio'yu hesapla

**Beklenen:**
- ✅ Alert: `BUFFER_MANIPULATION`
- ✅ Ratio: 30:1
- ✅ Tespit süresi: < 30 saniye

---

## 🔧 **MİTİGASYON STRATEJİLERİ**

### **1️⃣ Önleyici (Preventive)**

```python
# Firmware seviyesi
MIN_SAMPLING_RATE = 30  # sample/minute
MAX_SAMPLING_INTERVAL = 2.0  # saniye

# Örnekleme parametreleri imzalanır
sampling_config = {
    "rate": 60,
    "interval": 1.0,
    "signature": sign(sampling_config, private_key)
}

# Değişiklik algılandığında
if verify_signature(config) == False:
    raise TamperDetected("Sampling config manipüle edilmiş!")
```

### **2️⃣ Tespit Edici (Detective)**

```python
# Çapraz doğrulama: BMS vs CP
bms_energy = vehicle.get_battery_consumption()  # Araçtan
cp_energy = charge_point.get_metered_energy()  # İstasyondan

if abs(bms_energy - cp_energy) > 0.10 * bms_energy:  # %10 fark
    alert("Cross-validation failed: BMS-CP mismatch")
```

### **3️⃣ Düzeltici (Corrective)**

```python
# Anomali tespit edilince
if alert.type == "SAMPLING_RATE_DROP":
    # Yüksek frekanslı moda geç
    charge_point.set_sampling_rate(120)  # 2 sample/s
    
    # Detaylı loglama aktif et
    enable_detailed_logging(session_id)
    
    # Operatöre alarm
    notify_operator(alert)
```

### **4️⃣ Reaktif (Reactive)**

```python
# Forensic analiz
if alert.severity == "CRITICAL":
    # Raw data backup
    backup_raw_samples(session_id)
    
    # Eksik enerji tahmini
    estimated_missing = estimate_hidden_energy(session)
    
    # Fatura düzeltmesi
    invoice.add_adjustment(estimated_missing, reason="sampling_manipulation")
```

---

## 📚 **REFERANSLAR**

- **ISO 15118:** Vehicle-to-Grid Communication Interface
- **OCPP 1.6:** Section 5.14 - MeterValues
- **IEC 61850:** Power utility automation

---

## ✅ **DOĞRULAMA**

Senaryo başarılı sayılır eğer:
- ✅ 5 sample/min düşüşü < 60s'de tespit edilir
- ✅ Variance %70+ düşüşü < 5 dakikada tespit edilir
- ✅ Buffer ratio 30:1 < 30s'de tespit edilir
- ✅ Tespit doğruluğu ≥%95
- ✅ Yanlış alarm ≤%3
- ✅ Dashboard'da tüm alert'ler görünür

---

**Son Güncelleme:** 2025-11-23  
**Senaryo Durumu:** ✅ ENTEGRE EDİLDİ  
**Test Durumu:** 🔄 TEST EDİLECEK
```

