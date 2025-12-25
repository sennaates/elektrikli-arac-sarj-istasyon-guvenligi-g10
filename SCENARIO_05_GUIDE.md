# Senaryo #5: Duplicate Booking Attack - Detaylı Kullanım Kılavuzu

## 🎯 Senaryo Hakkında

**Senaryo #5**, OCPP ReserveNow mekanizmasındaki güvenlik açığını test eder. Saldırgan, rezervasyon sistemini manipüle ederek yetkisiz şarj erişimi kazanmaya çalışır.

## 📋 Gereksinimler

- Python 3.9+
- CSMS Simülatörü çalışıyor olmalı
- Bridge çalışıyor olmalı (opsiyonel, IDS testi için)

## 🚀 Adım Adım Test

### Adım 1: Ortamı Hazırla

```bash
# Terminal 1: CSMS Simülatörünü başlat
python csms_simulator.py

# Terminal 2: Bridge'i başlat (opsiyonel)
python secure_bridge.py

# Terminal 3: Dashboard'u başlat (opsiyonel)
streamlit run dashboard.py
```

### Adım 2: Saldırı Senaryolarını Test Et

#### Senaryo 1: Duplicate Reservation ID

```bash
python attack_simulator.py \
    --attack duplicate_booking \
    --booking-scenario duplicate_id \
    --csms-url ws://localhost:9000
```

**Beklenen Davranış:**
- İlk ReserveNow isteği başarılı olur
- İkinci ReserveNow isteği (aynı reservationId) gönderilir
- IDS `DUPLICATE_RESERVATION_ID` alert'i üretir
- Severity: CRITICAL

#### Senaryo 2: Multiple Connector Reservations

```bash
python attack_simulator.py \
    --attack duplicate_booking \
    --booking-scenario multiple_connector \
    --csms-url ws://localhost:9000
```

**Beklenen Davranış:**
- Aynı connectorId için iki rezervasyon oluşturulur
- IDS `MULTIPLE_CONNECTOR_RESERVATIONS` alert'i üretir
- Severity: CRITICAL

#### Senaryo 3: Reservation ID Reuse

```bash
python attack_simulator.py \
    --attack duplicate_booking \
    --booking-scenario id_reuse \
    --csms-url ws://localhost:9000
```

**Beklenen Davranış:**
- İlk rezervasyon oluşturulur ve iptal edilir
- Aynı reservationId tekrar kullanılır
- IDS `RESERVATION_ID_REUSE` alert'i üretir
- Severity: HIGH

#### Senaryo 4: Reservation-Transaction Mismatch

```bash
python attack_simulator.py \
    --attack duplicate_booking \
    --booking-scenario mismatch_transaction \
    --csms-url ws://localhost:9000
```

**Beklenen Davranış:**
- Meşru bir rezervasyon oluşturulur (idTag: LEGITIMATE_TAG)
- Farklı idTag ile StartTransaction gönderilir (idTag: ATTACKER_TAG)
- IDS `RESERVATION_TRANSACTION_MISMATCH` alert'i üretir
- Severity: CRITICAL

### Adım 3: Tüm Senaryoları Test Et

```bash
python test_duplicate_booking_scenario.py
```

Bu script, tüm senaryoları sırayla test eder.

## 🔍 IDS Tespit Kuralları Detayı

### Kural-1: DUPLICATE_RESERVATION_ID

```python
# Tespit Koşulu
if reservation_id in existing_reservations:
    if time_diff <= 60.0:  # 60 saniye içinde
        alert = CRITICAL
```

**Örnek Senaryo:**
```
T=0s: ReserveNow(reservationId="RES-001", idTag="TAG-1")
T=1s: ReserveNow(reservationId="RES-001", idTag="TAG-2")  # DUPLICATE!
→ Alert: DUPLICATE_RESERVATION_ID
```

### Kural-2: MULTIPLE_CONNECTOR_RESERVATIONS

```python
# Tespit Koşulu
if len(connector_reservations[connector_id]) > 1:
    alert = CRITICAL
```

**Örnek Senaryo:**
```
ReserveNow(connectorId=1, reservationId="RES-001")
ReserveNow(connectorId=1, reservationId="RES-002")  # AYNI CONNECTOR!
→ Alert: MULTIPLE_CONNECTOR_RESERVATIONS
```

### Kural-3: RESERVATION_ID_REUSE

```python
# Tespit Koşulu
if reservation_id in used_reservation_ids:
    alert = HIGH
```

**Örnek Senaryo:**
```
T=0s: ReserveNow(reservationId="RES-001") → Accepted
T=5s: CancelReservation(reservationId="RES-001")
T=10s: ReserveNow(reservationId="RES-001")  # REUSE!
→ Alert: RESERVATION_ID_REUSE
```

### Kural-5: RESERVATION_TRANSACTION_MISMATCH

```python
# Tespit Koşulu
if reservation_id_tag != transaction_id_tag:
    alert = CRITICAL
```

**Örnek Senaryo:**
```
ReserveNow(reservationId="RES-001", idTag="LEGITIMATE")
StartTransaction(idTag="ATTACKER")  # MISMATCH!
→ Alert: RESERVATION_TRANSACTION_MISMATCH
```

## 📊 Dashboard'da Görüntüleme

### Alert Listesi
- 🚨 `DUPLICATE_RESERVATION_ID` - CRITICAL
- 🚨 `MULTIPLE_CONNECTOR_RESERVATIONS` - CRITICAL
- ⚠️ `RESERVATION_ID_REUSE` - HIGH
- 🚨 `RESERVATION_TRANSACTION_MISMATCH` - CRITICAL

### İstatistikler
- Toplam rezervasyon sayısı
- Aktif rezervasyon sayısı
- Connector başına rezervasyon sayısı
- Rezervasyon ID tekrar kullanım oranı

## 🛠️ Geliştirme Notları

### Yeni Senaryo Ekleme

1. `tests/scenario_05_duplicate_booking.py` dosyasına senaryo ekle
2. `attack_simulator.py` içinde `duplicate_booking_attack_async` metodunu güncelle
3. `utils/ids.py` içinde yeni tespit kuralı ekle (gerekirse)
4. Test script'ini güncelle

### IDS Kuralı Ekleme

```python
# utils/ids.py içinde
def check_reservation(self, ...):
    # Yeni kural ekle
    if new_condition:
        alert = self._create_alert(
            alert_type="NEW_RULE",
            severity="CRITICAL",
            description="...",
            source="OCPP",
            data={...}
        )
        return alert
```

## 📝 Troubleshooting

### Problem: CSMS'e bağlanılamıyor

**Çözüm:**
```bash
# CSMS simülatörünün çalıştığını kontrol et
ps aux | grep csms_simulator

# Port 9000'in açık olduğunu kontrol et
netstat -tuln | grep 9000
```

### Problem: IDS alert üretilmiyor

**Çözüm:**
1. Bridge'in çalıştığını kontrol et
2. IDS'in aktif olduğunu kontrol et
3. Rezervasyon tracking'in doğru çalıştığını kontrol et

### Problem: Test script hata veriyor

**Çözüm:**
```bash
# Bağımlılıkları kontrol et
pip install -r requirements.txt

# Python path'i kontrol et
python -c "import sys; print(sys.path)"
```

## 🎓 Öğrenme Hedefleri

Bu senaryo ile öğrenilecekler:

1. ✅ OCPP ReserveNow mekanizmasının güvenlik açıkları
2. ✅ Rezervasyon ID yönetimi ve benzersizlik kontrolü
3. ✅ Connector rezervasyon politikaları
4. ✅ Rezervasyon-Transaction eşleşmesi kontrolü
5. ✅ IDS kural tabanlı tespit mekanizması
6. ✅ Blockchain tabanlı audit logging

## 📚 İlgili Dosyalar

- `tests/scenario_05_duplicate_booking.py` - Senaryo tanımı
- `attack_simulator.py` - Saldırı simülasyonu
- `utils/ids.py` - IDS tespit kuralları
- `secure_bridge.py` - ReserveNow handler
- `test_duplicate_booking_scenario.py` - Test script'i

## ✅ Başarı Kriterleri

- [x] Senaryo tanımı oluşturuldu
- [x] Saldırı simülasyonu eklendi
- [x] IDS tespit kuralları eklendi
- [x] Bridge entegrasyonu yapıldı
- [x] Test script'i oluşturuldu
- [x] Dokümantasyon hazırlandı

