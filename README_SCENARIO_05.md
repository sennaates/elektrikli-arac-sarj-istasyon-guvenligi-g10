# Senaryo #5: Sahte Rezervasyon (A4: Duplicate Booking) Kullanarak Yetkisiz Şarj Erişimi

## 📋 Senaryo Özeti

Bu senaryo, OCPP ReserveNow mekanizmasındaki güvenlik açığını test eder. Saldırgan, aynı rezervasyon ID'sini veya aynı connector'ı birden fazla kez rezerve ederek yetkisiz şarj erişimi kazanmaya çalışır.

## 🎯 Saldırı Tipi

- **OWASP Kategorisi**: A4 - Insecure Direct Object References
- **CWE**: CWE-639, CWE-284, CWE-285
- **Severity**: CRITICAL
- **Risk Score**: 8.5/10

## 🔍 Saldırı Senaryoları

### 1. Duplicate Reservation ID
Aynı `reservationId` ile iki ReserveNow isteği gönderilir.

### 2. Multiple Connector Reservations
Aynı `connectorId` için birden fazla aktif rezervasyon oluşturulur.

### 3. Reservation ID Reuse
Daha önce kullanılmış bir `reservationId` tekrar kullanılır.

### 4. Reservation-Transaction Mismatch
Rezervasyondaki `idTag` ile farklı bir `idTag` ile şarj başlatılır.

## 🛡️ Tespit Kuralları

### Kural-1: DUPLICATE_RESERVATION_ID (CRITICAL)
- **Koşul**: Aynı reservationId ile birden fazla ReserveNow isteği
- **Pencere**: 60 saniye
- **Severity**: CRITICAL

### Kural-2: MULTIPLE_CONNECTOR_RESERVATIONS (CRITICAL)
- **Koşul**: Aynı connectorId için aktif rezervasyon sayısı > 1
- **Pencere**: 5 saniye
- **Severity**: CRITICAL

### Kural-3: RESERVATION_ID_REUSE (HIGH)
- **Koşul**: Daha önce kullanılmış reservationId tekrar kullanıldı
- **Pencere**: 300 saniye (5 dakika)
- **Severity**: HIGH

### Kural-4: UNAUTHORIZED_RESERVATION_ACCESS (CRITICAL)
- **Koşul**: Rezervasyon olmadan veya geçersiz idTag ile şarj başlatma
- **Pencere**: 10 saniye
- **Severity**: CRITICAL

### Kural-5: RESERVATION_TRANSACTION_MISMATCH (CRITICAL)
- **Koşul**: StartTransaction'da kullanılan idTag, rezervasyondaki idTag ile eşleşmiyor
- **Pencere**: 30 saniye
- **Severity**: CRITICAL

## 🚀 Test Etme

### 1. CSMS Simülatörünü Başlat

```bash
python csms_simulator.py
```

### 2. Bridge'i Başlat (Opsiyonel)

```bash
python secure_bridge.py
```

### 3. Saldırıyı Simüle Et

```bash
# Duplicate Reservation ID saldırısı
python attack_simulator.py --attack duplicate_booking --booking-scenario duplicate_id

# Multiple Connector Reservations saldırısı
python attack_simulator.py --attack duplicate_booking --booking-scenario multiple_connector

# Reservation ID Reuse saldırısı
python attack_simulator.py --attack duplicate_booking --booking-scenario id_reuse

# Reservation-Transaction Mismatch saldırısı
python attack_simulator.py --attack duplicate_booking --booking-scenario mismatch_transaction
```

### 4. Test Script'i Çalıştır

```bash
python test_duplicate_booking_scenario.py
```

## 📊 Beklenen Sonuçlar

### IDS Alerts
- ✅ `DUPLICATE_RESERVATION_ID` alert'i tetiklenmeli
- ✅ `MULTIPLE_CONNECTOR_RESERVATIONS` alert'i tetiklenmeli
- ✅ `RESERVATION_ID_REUSE` alert'i tetiklenmeli
- ✅ `RESERVATION_TRANSACTION_MISMATCH` alert'i tetiklenmeli

### Dashboard
- 🚨 Kırmızı alarm görünmeli
- 📊 Rezervasyon istatistikleri anormal olmalı
- 🔴 CRITICAL severity alert'ler listelenmeli

### Blockchain
- ⛓️ Tüm rezervasyon işlemleri blockchain'e kaydedilmeli
- 🚨 Alert'ler ALERT bloğu olarak kaydedilmeli

## 🔧 Önerilen Düzeltmeler

1. **Rezervasyon ID Benzersizliği**: UUID kullanarak rezervasyon ID'lerinin benzersizliğini garanti et
2. **Connector Tek Rezervasyon**: Aynı connector için aynı anda tek rezervasyon politikası uygula
3. **Rezervasyon Doğrulama**: Rezervasyon ID'nin daha önce kullanılmış olup olmadığını kontrol et
4. **idTag Eşleşmesi**: StartTransaction'da rezervasyon-idTag eşleşmesini zorunlu kıl
5. **Süre Kontrolü**: Rezervasyon süresi ve expiry kontrolü yap
6. **Müsaitlik Kontrolü**: Connector müsaitlik kontrolü yap (zaten rezerve edilmiş mi?)
7. **Blockchain Logging**: Rezervasyon loglarını blockchain'e kaydet (non-repudiation)
8. **Rate Limiting**: Aynı idTag için çok fazla rezervasyon isteğini engelle

## 📚 Referanslar

- **OWASP Top 10**: A01:2021 - Broken Access Control
- **CWE-639**: Authorization Bypass Through User-Controlled Key
- **CWE-284**: Improper Access Control
- **CWE-285**: Improper Authorization
- **OCPP 1.6 Specification**: ReserveNow Action

## 📝 Notlar

- Bu senaryo, OCPP rezervasyon mekanizmasındaki güvenlik açıklarını test eder
- Saldırgan, rezervasyon sistemini bypass ederek yetkisiz şarj erişimi kazanmaya çalışır
- IDS, çoklu tespit kuralları ile bu saldırıları gerçek zamanlı olarak tespit eder
- Senaryo, gelir kaybı ve güvenlik ihlali risklerini gösterir

