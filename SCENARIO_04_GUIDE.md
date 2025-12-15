# 🔴 Senaryo #4: Fail-Open Davranışı - Auth Servis Kapalı

## 📋 Senaryo Özeti

**Saldırı Tipi:** Denial of Service (DoS) + Authentication Bypass  
**Hedef:** Auth Servis (CSMS) / Kimlik Doğrulama Akışı  
**Severity:** CRITICAL  
**Risk Skoru:** 9.2/10  
**Tespit Yöntemi:** Rule-Based IDS (4 kural)

---

## 🎯 Saldırı Akışı

### Adım 1: DoS Saldırısı
Saldırgan, Auth Servis'e yüksek trafikli DoS saldırısı başlatır:
- Saniyede 100+ auth isteği gönderilir
- Auth Servis kaynak tükenmesi yaşar
- Servis erişilemez hale gelir

### Adım 2: Auth Timeout'ları
EVSE, Auth Servis'e kimlik doğrulama isteği gönderir:
- Yanıt alamaz (timeout)
- Ardışık timeout'lar oluşur (3+ timeout / 60 saniye)

### Adım 3: Fail-Open Davranışı
Sistem, güvenlik politikasını ihlal eder:
- **Beklenen:** Fail-Closed (Auth başarısız → Şarj başlamaz)
- **Gerçek:** Fail-Open (Auth başarısız → Şarj başlar)

### Adım 4: Yetkisiz Şarj
Auth olmadan şarj işlemi başlatılır:
- Ücretsiz enerji kullanımı
- Log kaydı eksik
- Gelir kaybı

---

## 🔬 Tespit Kuralları

### Kural 1: Auth Servis Erişilemezlik Tespiti
**Alert Tipi:** `AUTH_SERVICE_UNAVAILABLE`  
**Severity:** HIGH  
**Koşul:** Son 60 saniyede 3+ auth timeout  
**Eşik:** 3 timeout / 60 saniye

```python
if timeout_count >= 3 in 60 seconds:
    alert = AUTH_SERVICE_UNAVAILABLE
```

### Kural 2: Fail-Open Davranış Tespiti
**Alert Tipi:** `FAIL_OPEN_BEHAVIOR`  
**Severity:** CRITICAL  
**Koşul:** Auth başarısız ama şarj başladı  
**Eşik:** 1 olay (tek bir olay bile kritik)

```python
if charge_started == True AND auth_status in ["FAILED", "TIMEOUT", "UNAVAILABLE"]:
    alert = FAIL_OPEN_BEHAVIOR
```

### Kural 3: Auth Timeout Pattern
**Alert Tipi:** `AUTH_TIMEOUT_PATTERN`  
**Severity:** HIGH  
**Koşul:** 5+ ardışık auth timeout  
**Eşik:** 5 ardışık timeout

```python
if consecutive_timeouts >= 5:
    alert = AUTH_TIMEOUT_PATTERN
```

### Kural 4: Unauthorized Charge Start
**Alert Tipi:** `UNAUTHORIZED_CHARGE_START`  
**Severity:** CRITICAL  
**Koşul:** Auth başarısız ama şarj başladı  
**Eşik:** 1 olay

```python
if charge_started == True AND auth_status == "FAILED":
    alert = UNAUTHORIZED_CHARGE_START
```

---

## 🧪 Test Senaryoları

### Test 1: Auth Servis DoS Saldırısı

```bash
python attack_simulator.py --attack fail_open \
    --csms-url ws://localhost:9000/ocpp \
    --fail-open-duration 300 \
    --dos-rate 100
```

**Beklenen Sonuç:**
- ✅ IDS Alert: `AUTH_SERVICE_UNAVAILABLE` (HIGH)
- ✅ IDS Alert: `FAIL_OPEN_BEHAVIOR` (CRITICAL)
- ✅ IDS Alert: `UNAUTHORIZED_CHARGE_START` (CRITICAL)
- ✅ Dashboard'da kırmızı alert'ler görünür

### Test 2: Auth Timeout Pattern

```python
from utils.ids import RuleBasedIDS
import time

ids = RuleBasedIDS()
t = time.time()

# 5 ardışık timeout oluştur
for i in range(5):
    ids.check_auth_failure("TIMEOUT", t + i)

# Alert kontrolü
alerts = ids.get_recent_alerts(10)
for alert in alerts:
    if alert.alert_type == "AUTH_TIMEOUT_PATTERN":
        print(f"✅ Alert: {alert.alert_type}")
```

**Beklenen Sonuç:**
- ✅ IDS Alert: `AUTH_TIMEOUT_PATTERN` (HIGH)

### Test 3: Yetkisiz Şarj Başlatma

```python
from utils.ids import RuleBasedIDS
import time

ids = RuleBasedIDS()
t = time.time()

# Auth başarısız
ids.check_auth_failure("FAILED", t)

# Şarj başlat (Fail-Open)
alert = ids.check_charge_without_auth(True, "FAILED", t + 1)
print(f"Alert: {alert.alert_type if alert else None}")
```

**Beklenen Sonuç:**
- ✅ IDS Alert: `FAIL_OPEN_BEHAVIOR` (CRITICAL)
- ✅ IDS Alert: `UNAUTHORIZED_CHARGE_START` (CRITICAL)

---

## 📊 Beklenen Sonuçlar

### IDS Alert'leri
- `AUTH_SERVICE_UNAVAILABLE` (HIGH) - Auth Servis erişilemez
- `AUTH_TIMEOUT_PATTERN` (HIGH) - Ardışık timeout pattern
- `FAIL_OPEN_BEHAVIOR` (CRITICAL) - Fail-open davranışı tespit edildi
- `UNAUTHORIZED_CHARGE_START` (CRITICAL) - Yetkisiz şarj başlatma

### Dashboard Metrikleri
- Auth başarısızlık oranı artar
- Şarj başlatma sayısı artar (auth olmadan)
- Alert sayısı artar (CRITICAL)

### Sistem Etkileri
- **Finansal:** Ücretsiz şarj işlemleri → Gelir kaybı
- **Operasyonel:** Sunucu arızasında sistem güvenli modda kalamaz
- **Güvenlik:** Kimlik doğrulama atlanır → Yetkisiz kullanım
- **İtibar:** Sistemin kötüye kullanılması → Güven kaybı

---

## 🛡️ Azaltma Stratejileri

### 1. Fail-Closed Politikası
Sistem mantığı fail-closed davranışına geçmelidir:
- Auth başarısız → Şarj başlamaz
- Exception handling'de güvenlik öncelikli olmalı

### 2. Offline Cache / Whitelist
Sadece belirli kullanıcılar için offline cache veya whitelist uygulanmalı:
- Güvenilir kullanıcılar için cache
- Whitelist kontrolü
- Rate limiting

### 3. DoS Dayanıklılığı
DoS dayanıklılığı load balancer ve rate limitlerle güçlendirilmelidir:
- Rate limiting (auth istekleri için)
- Load balancer
- Resource monitoring

### 4. Loglama ve Alarm
Fail-open durumları için loglama ve alarm mekanizması eklenmelidir:
- Tüm fail-open olayları loglanmalı
- Otomatik alarm sistemi
- Dashboard entegrasyonu

---

## 📚 CWE/OWASP Sınıflandırması

- **CWE-703:** Improper Handling of Exceptional Conditions
- **CWE-287:** Improper Authentication
- **OWASP A07-2021:** Identification and Authentication Failures

---

## 🔗 İlgili Dosyalar

- **Senaryo Dosyası:** `tests/scenario_04_fail_open.py`
- **IDS Kuralları:** `utils/ids.py` - `check_auth_failure()`, `check_charge_without_auth()`
- **Attack Simulator:** `attack_simulator.py` - `fail_open_attack()`
- **README:** `README_SCENARIO_04.md`

---

## 📝 Notlar

- Bu senaryo, güvenlik politikası ihlali odaklıdır
- Fail-open davranışı, kritik sistemler için kabul edilemez
- Tespit süresi: < 10 saniye (kritik alert)
- Risk skoru: 9.2/10 (CRITICAL)

---

**Son Güncelleme:** 2025-12-14  
**Versiyon:** 1.0

