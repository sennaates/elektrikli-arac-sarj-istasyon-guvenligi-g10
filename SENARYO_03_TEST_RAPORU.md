# 📊 SENARYO #3 TEST RAPORU

## ✅ Kurulum Durumu
- **Python ortamı:** ✅ Kuruldu (7.2 saniye)
- **Bağımlılıklar:** ✅ Yüklendi
- **CAN-Bus:** ⚠️ Mock mode (vcan0 Windows'ta desteklenmiyor)

## 🎯 Senaryonuz: Adaptive Sampling Manipulation

### Tespit Edilen 3 Saldırı Tekniği:

#### 1️⃣ Rate Drop (Örnekleme Düşürme)
```
Normal: 60 sample/dakika (her saniye)
Saldırı: 1 sample/dakika (her 60 saniye)
Tespit: samples_per_minute < 30
Alert: SAMPLING_RATE_DROP (HIGH)
Süre: <60 saniye
```

#### 2️⃣ Peak Smoothing (Tepe Değer Gizleme)
```
Normal: Varyans 0.3-1.5 kWh²
Saldırı: Varyans 0.01-0.1 kWh² (peak'ler ortalanmış)
Tespit: variance < historical_variance * 0.30
Alert: ENERGY_VARIANCE_DROP (CRITICAL)
Süre: <300 saniye
```

#### 3️⃣ Buffer Manipulation (Veri Saklama)
```
Normal: Buffer/Sent = 1:1
Saldırı: Buffer/Sent = 30:1 (veriler gönderilmiyor)
Tespit: buffer_ratio > 2.0
Alert: BUFFER_MANIPULATION (CRITICAL)
Süre: <30 saniye
```

## 💰 Finansal Etki
```
Senaryo: 1,000 oturum/ay × 50 kWh × 0.20 €/kWh × %30 kayıp
Aylık Kayıp: 3,000 €
Yıllık Kayıp: 36,000 €
```

## 📁 Proje Dosyalarınız

### Kod Dosyaları
- ✅ `attack_simulator.py` - Saldırı simülatörü (694 satır)
- ✅ `utils/ids.py` - IDS tespit kuralları
- ✅ `tests/scenario_03_sampling_manipulation.py` - Test senaryosu (381 satır)

### Dokümantasyon
- ✅ `README_SCENARIO_03.md` - Senaryo özeti (346 satır)
- ✅ `SCENARIO_03_GUIDE.md` - Kullanım kılavuzu (373 satır)

### Test Komutları
```bash
# Test 1: Rate Drop
python attack_simulator.py --attack sampling --sampling-scenario rate_drop --sampling-duration 60

# Test 2: Peak Smoothing
python attack_simulator.py --attack sampling --sampling-scenario peak_smoothing --sampling-duration 60

# Test 3: Buffer Manipulation
python attack_simulator.py --attack sampling --sampling-scenario buffer_manipulation --sampling-duration 60
```

## 🔍 Kod Özeti

### IDS Tespit Kuralları (utils/ids.py)
```python
def check_meter_values(meter_value, timestamp, raw_buffer_size, session_id):
    # 1. Sampling rate kontrolü
    if samples_per_minute < 30:
        return Alert("SAMPLING_RATE_DROP", "HIGH", ...)
    
    # 2. Variance kontrolü
    if current_variance < historical_variance * 0.30:
        return Alert("ENERGY_VARIANCE_DROP", "CRITICAL", ...)
    
    # 3. Buffer kontrolü
    if raw_buffer_size / sent_count > 2.0:
        return Alert("BUFFER_MANIPULATION", "CRITICAL", ...)
```

### Saldırı Simülasyonu (attack_simulator.py)
```python
def sampling_manipulation(scenario, duration):
    if scenario == "rate_drop":
        # 1s → 60s örnekleme düşür
        normal_rate = 1.0  # saniye
        attack_rate = 60.0
        
    elif scenario == "peak_smoothing":
        # Peak değerleri ortala
        smoothed_value = np.mean(peak_values)
        
    elif scenario == "buffer_manipulation":
        # Veriyi buffer'da tut
        buffer.append(sample)
        # Sadece %10'unu gönder
```

## 📈 Test Sonuçları (Beklenen)

| Test ID | Senaryo | Beklenen Alert | Tespit Süresi | Durum |
|---------|---------|----------------|---------------|-------|
| TC-03-001 | Rate Drop | SAMPLING_RATE_DROP | <60s | ⏳ CAN gerekli |
| TC-03-002 | Peak Smoothing | ENERGY_VARIANCE_DROP | <300s | ⏳ CAN gerekli |
| TC-03-003 | Buffer Manip | BUFFER_MANIPULATION | <30s | ⏳ CAN gerekli |
| TC-03-004 | Combined | Tümü | <60s | ⏳ CAN gerekli |

## 🐧 Linux'ta Tam Test İçin

```bash
# 1. vcan0 kur
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# 2. Tam sistem testi
# Terminal 1: CSMS
python csms_simulator.py

# Terminal 2: Bridge
python secure_bridge.py

# Terminal 3: Dashboard
streamlit run dashboard.py

# Terminal 4: Saldırı
python attack_simulator.py --attack sampling --sampling-scenario rate_drop
```

## ✅ Değerlendirme

### Tamamlanan
- ✅ Senaryo tasarımı ve dokümantasyonu
- ✅ IDS tespit kuralları yazıldı
- ✅ Saldırı simülatörü kodlandı
- ✅ Test senaryoları hazırlandı
- ✅ Finansal etki analizi yapıldı

### Teknik Detaylar
- **Toplam Kod:** ~1,315 satır
- **Dokümantasyon:** ~719 satır
- **Test Coverage:** 3 ayrı manipülasyon tekniği
- **Alert Tipleri:** 3 (SAMPLING_RATE_DROP, ENERGY_VARIANCE_DROP, BUFFER_MANIPULATION)

---

**Sonuç:** Senaryonuz tam olarak geliştirilmiş ve dokümante edilmiştir. 
Windows'ta CAN-Bus simülasyonu sınırlı olduğundan, tam testler için 
Linux ortamı (Docker/WSL/VM) önerilir.
