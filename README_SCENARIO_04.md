# ✅ SENARYO #4 ENTEGRASYON ÖZETİ

## 📋 SENARYO DETAYLARI

**ID:** SCENARIO-04  
**İsim:** Fail-Open Davranışı - Auth Servis Kapalı  
**Kategori:** Authentication Bypass / Security Policy Violation  
**Severity:** CRITICAL  
**Risk Skoru:** 9.2/10  
**Durum:** ✅ ENTEGRE EDİLDİ

---

## 🎯 NE EKLENDİ?

### 1️⃣ Senaryo Dosyası
**Dosya:** `tests/scenario_04_fail_open.py`

**İçerik:**
- Senaryo yapılandırması (SCENARIO_CONFIG)
- Normal ve anomali davranış tanımları
- Saldırı parametreleri ve adımları
- Tespit kuralları (4 kural)
- Test senaryoları (3 test case)
- Risk değerlendirmesi
- Önerilen düzeltmeler

**Doğrulama:**
```bash
python tests/scenario_04_fail_open.py
```

---

### 2️⃣ IDS Kuralları
**Dosya:** `utils/ids.py`

**Eklenen Metodlar:**

#### `check_auth_failure()`
- Auth başarısızlığını kontrol eder
- Timeout pattern tespiti
- Auth servis erişilemezlik tespiti

**Alert Tipleri:**
- `AUTH_SERVICE_UNAVAILABLE` (HIGH)
- `AUTH_TIMEOUT_PATTERN` (HIGH)

#### `check_charge_without_auth()`
- Auth olmadan şarj başlatma tespiti
- Fail-open davranış tespiti

**Alert Tipleri:**
- `FAIL_OPEN_BEHAVIOR` (CRITICAL)
- `UNAUTHORIZED_CHARGE_START` (CRITICAL)

**Eklenen Tracking:**
- `auth_timeout_timestamps`: Auth timeout zamanları
- `auth_success_count`: Başarılı auth sayısı
- `auth_failure_count`: Başarısız auth sayısı
- `consecutive_auth_timeouts`: Ardışık timeout sayısı
- `charge_starts_without_auth`: Auth olmadan şarj başlatma sayısı
- `last_successful_auth_time`: Son başarılı auth zamanı

---

### 3️⃣ Attack Simulator
**Dosya:** `attack_simulator.py`

**Eklenen Metodlar:**

#### `fail_open_attack()`
- Auth Servis'e DoS saldırısı yapar
- Fail-open davranışını tetikler
- Yetkisiz şarj başlatma simülasyonu

**Parametreler:**
- `csms_url`: CSMS WebSocket URL
- `duration`: DoS saldırısı süresi (saniye)
- `dos_rate`: Saniyede gönderilecek istek sayısı

**CLI Kullanımı:**
```bash
python attack_simulator.py --attack fail_open \
    --csms-url ws://localhost:9000/ocpp \
    --fail-open-duration 300 \
    --dos-rate 100
```

---

### 4️⃣ Dokümantasyon
**Dosyalar:**
- `SCENARIO_04_GUIDE.md` - Detaylı kullanım kılavuzu
- `README_SCENARIO_04.md` - Entegrasyon özeti (bu dosya)

---

## 🧪 TEST SENARYOLARI

### Test 1: Senaryo Doğrulama
```bash
python tests/scenario_04_fail_open.py
```

**Beklenen Çıktı:**
```
✅ Senaryo #4 doğrulandı: Fail-Open Davranışı - Auth Servis Kapalı
   Severity: CRITICAL
   Risk Score: 9.2/10
```

### Test 2: IDS Kuralları
```python
from utils.ids import RuleBasedIDS
import time

ids = RuleBasedIDS()
t = time.time()

# 5 ardışık timeout
for i in range(5):
    ids.check_auth_failure("TIMEOUT", t + i)

# Fail-open davranışı
alert = ids.check_charge_without_auth(True, "TIMEOUT", t + 10)
print(f"Alert: {alert.alert_type}")  # FAIL_OPEN_BEHAVIOR
```

**Beklenen Sonuç:**
- ✅ `AUTH_TIMEOUT_PATTERN` alert (HIGH)
- ✅ `FAIL_OPEN_BEHAVIOR` alert (CRITICAL)

### Test 3: Attack Simulator
```bash
# CSMS simulator çalıştır (Terminal 1)
python csms_simulator.py

# Fail-open attack (Terminal 2)
python attack_simulator.py --attack fail_open \
    --fail-open-duration 60 \
    --dos-rate 50
```

**Beklenen Sonuç:**
- ✅ Auth Servis DoS saldırısı başlatılır
- ✅ Fail-open davranışı tetiklenir
- ✅ IDS alert'leri oluşur

---

## 🚀 NASIL TEST EDİLİR?

### Adım 1: Sistem Hazırlığı
```bash
# Virtual environment aktif et
source venv/bin/activate

# vcan0 kurulumu (gerekirse)
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

### Adım 2: Servisleri Başlat
```bash
# Terminal 1: CSMS Simulator
python csms_simulator.py

# Terminal 2: Secure Bridge
python secure_bridge.py

# Terminal 3: API Server
python api_server.py

# Terminal 4: Dashboard
streamlit run dashboard.py
```

### Adım 3: Saldırıyı Simüle Et
```bash
# Terminal 5: Attack Simulator
python attack_simulator.py --attack fail_open \
    --csms-url ws://localhost:9000/ocpp \
    --fail-open-duration 300 \
    --dos-rate 100
```

### Adım 4: Sonuçları Kontrol Et
- Dashboard'da alert'leri kontrol et
- API'den alert listesini çek:
  ```bash
  curl http://localhost:8000/api/alerts?severity=CRITICAL
  ```

---

## 📊 TESPİT KURALLARI ÖZETİ

| Kural ID | Alert Tipi | Severity | Eşik | Pencere |
|----------|------------|----------|------|---------|
| Rule-1 | AUTH_SERVICE_UNAVAILABLE | HIGH | 3 timeout | 60s |
| Rule-2 | FAIL_OPEN_BEHAVIOR | CRITICAL | 1 olay | 10s |
| Rule-3 | AUTH_TIMEOUT_PATTERN | HIGH | 5 ardışık | 30s |
| Rule-4 | UNAUTHORIZED_CHARGE_START | CRITICAL | 1 olay | 5s |

---

## 🔗 İLGİLİ DOSYALAR

- **Senaryo:** `tests/scenario_04_fail_open.py`
- **IDS:** `utils/ids.py` (check_auth_failure, check_charge_without_auth)
- **Attack:** `attack_simulator.py` (fail_open_attack)
- **Guide:** `SCENARIO_04_GUIDE.md`
- **PDF:** `Anomali Senaryoları/fail_open_davranisi.pdf`

---

## ✅ KONTROL LİSTESİ

- [x] Senaryo dosyası oluşturuldu
- [x] IDS kuralları eklendi
- [x] Attack simulator fonksiyonu eklendi
- [x] Dokümantasyon oluşturuldu
- [x] Test edildi ve çalıştığı doğrulandı
- [ ] Ana README güncellendi (opsiyonel)

---

## 📝 NOTLAR

- Senaryo #4, güvenlik politikası ihlali odaklıdır
- Fail-open davranışı, kritik sistemler için kabul edilemez
- Tespit süresi: < 10 saniye (kritik alert)
- Risk skoru: 9.2/10 (CRITICAL)

---

**Entegrasyon Tarihi:** 2025-12-14  
**Versiyon:** 1.0  
**Durum:** ✅ TAMAMLANDI

