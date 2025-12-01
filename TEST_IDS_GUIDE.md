# 🧪 IDS Test Kılavuzu

Bu kılavuz, 3 anomali senaryosunu test etmek için iki farklı yöntem sunar.

---

## 📋 Test Yöntemleri

### Yöntem 1: Direkt IDS Testi (Önerilen)

IDS'i direkt test eder, OCPP mesajlarını simüle eder. Bridge'e bağlı olmadan çalışır.

**Kullanım:**
```bash
# Virtual environment'ı aktif et
source venv/bin/activate

# Test scriptini çalıştır
python test_ids_directly.py
```

**Beklenen Çıktı:**
```
✅ Senaryo #1 (Timing Anomaly): BAŞARILI
✅ Senaryo #2 (OCPP Flooding): BAŞARILI
✅ Senaryo #3 (Sampling Manipulation): BAŞARILI
```

**Avantajlar:**
- Hızlı test (birkaç saniye)
- Bridge'e bağlı olmadan çalışır
- Alert'ler API server'a otomatik gönderilir
- Dashboard'da görülebilir

---

### Yöntem 2: CSMS Simülatörü ile Otomatik Test

CSMS simülatörü bridge'e otomatik test komutları gönderir.

**Kullanım:**
```bash
# Terminal 1: Bridge'i başlat
source venv/bin/activate
python secure_bridge.py

# Terminal 2: CSMS simülatörünü otomatik test moduyla başlat
source venv/bin/activate
python csms_simulator.py --auto-test
```

**Beklenen Davranış:**
1. Bridge CSMS'e bağlanır
2. CSMS otomatik olarak test komutlarını gönderir:
   - Senaryo #1: RemoteStartTransaction → 1 saniye sonra RemoteStopTransaction
   - Senaryo #2: 20 Heartbeat mesajı (20 mesaj/saniye)
   - Senaryo #3: Düşük frekanslı MeterValues

**Avantajlar:**
- Gerçek OCPP trafiği simüle eder
- Bridge'in tam akışını test eder
- Gerçekçi senaryo

---

## 🎯 Test Senaryoları

### Senaryo #1: Timing Anomaly (MitM OCPP Manipulation)

**Test:** RemoteStartTransaction sonrası 1 saniye içinde RemoteStopTransaction

**Beklenen Alert:**
- `TIMING_MISMATCH_K1`
- Severity: `HIGH`
- Kural: K1 (Timing Mismatch)

**Kod:**
```python
ids.check_ocpp_message("RemoteStartTransaction", {...}, time.time())
time.sleep(1.0)
ids.check_ocpp_message("RemoteStopTransaction", {...}, time.time())
```

---

### Senaryo #2: OCPP Message Flooding (DoS)

**Test:** 20 mesaj/saniye gönder (eşik: 5 mesaj/saniye)

**Beklenen Alert:**
- `OCPP_RATE_LIMIT_EXCEEDED`
- Severity: `CRITICAL`
- Rate: ~20-25 mesaj/saniye

**Kod:**
```python
for i in range(20):
    ids.check_ocpp_message("Heartbeat", {}, time.time())
    time.sleep(0.05)  # 20 mesaj/saniye
```

---

### Senaryo #3: Sampling Rate Drop (Energy Theft)

**Test:** Örnekleme oranını düşür (60 sample/min → 1 sample/min)

**Beklenen Alert:**
- `SAMPLING_RATE_DROP`
- Severity: `HIGH`
- Minimum: 30 sample/min

**Kod:**
```python
# Düşük rate simüle et
ids.check_meter_values(meter_value=10.0, timestamp=time.time() - 60, ...)
ids.check_meter_values(meter_value=10.1, timestamp=time.time(), ...)
```

---

## 📊 Dashboard'da Görüntüleme

Test scripti çalıştırıldıktan sonra:

1. **Dashboard'ı aç:** http://localhost:8501
2. **Alert'leri kontrol et:**
   - Real-Time Alerts bölümünde yeni alert'ler görünmeli
   - Son Alert'ler listesinde detaylar görünmeli
3. **Blockchain'i kontrol et:**
   - Son Bloklar tablosunda ALERT tipi bloklar görünmeli

---

## 🔧 Sorun Giderme

### Problem: Alert'ler görünmüyor

**Çözüm:**
1. API server'ın çalıştığından emin olun:
   ```bash
   ps aux | grep api_server
   ```

2. API server'ı başlatın:
   ```bash
   python api_server.py
   ```

3. Test scriptini tekrar çalıştırın

### Problem: Senaryo #3 alert vermiyor

**Çözüm:**
- Senaryo #3 için yeterli sample gönderilmesi gerekir
- Minimum 5 sample ve 60 saniyelik pencere gerekir
- Test scripti bunu otomatik yapar

### Problem: CSMS simülatörü komut göndermiyor

**Çözüm:**
1. `--auto-test` flag'ini kullandığınızdan emin olun
2. Bridge'in CSMS'e bağlandığını kontrol edin
3. BootNotification'ın başarılı olduğunu kontrol edin

---

## 📝 Notlar

- Test scripti (`test_ids_directly.py`) IDS'i direkt test eder
- Alert'ler otomatik olarak API server'a gönderilir
- Dashboard'da görüntülemek için API server'ın çalışıyor olması gerekir
- CSMS simülatörü ile test daha gerçekçi ama daha yavaştır

---

## ✅ Başarı Kriterleri

Test başarılı sayılır eğer:
- ✅ Senaryo #1: `TIMING_MISMATCH_K1` alert'i görünüyor
- ✅ Senaryo #2: `OCPP_RATE_LIMIT_EXCEEDED` alert'i görünüyor
- ✅ Senaryo #3: `SAMPLING_RATE_DROP` alert'i görünüyor
- ✅ Dashboard'da alert'ler görünüyor
- ✅ Blockchain'e ALERT blokları ekleniyor

---

**Son Güncelleme:** 2025-12-01

