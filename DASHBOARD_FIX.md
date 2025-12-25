# 🔧 Dashboard Sonuçları Düzeltme

## Sorun: Dashboard'da sonuçlar doğru değil

### 🔍 Sorun Analizi

Dashboard'da veri görünmüyorsa muhtemelen:

1. **Bridge çalışmıyor** → Veri yok
2. **Senaryo #5 test edilmedi** → Alert'ler yok
3. **API state boş** → İstatistikler 0

### ✅ Çözüm 1: Senaryo #5 Test Alert'leri Oluştur

Dashboard'da Senaryo #5 alert'lerini görmek için:

```bash
cd /home/semih/elektrikli-arac-sarj-istasyon-guvenligi-g10
source venv/bin/activate
python test_scenario_05_dashboard.py
```

Bu script:
- ✅ API bağlantısını test eder
- ✅ Senaryo #5 alert'lerini oluşturur
- ✅ Dashboard'da görünmesini sağlar

### ✅ Çözüm 2: Bridge'i Başlat (Gerçek Veri İçin)

**Terminal 3: Bridge**
```bash
cd /home/semih/elektrikli-arac-sarj-istasyon-guvenligi-g10
source venv/bin/activate
python secure_bridge.py
```

Bridge başlatıldığında:
- ✅ Blockchain'e bloklar eklenir
- ✅ CAN frame'ler işlenir
- ✅ OCPP mesajları alınır
- ✅ İstatistikler güncellenir

### ✅ Çözüm 3: Senaryo #5 Saldırısını Test Et

**Terminal 4: Saldırı Simülatörü**
```bash
cd /home/semih/elektrikli-arac-sarj-istasyon-guvenligi-g10
source venv/bin/activate

# Önce CSMS simülatörünü başlat (Terminal 5)
# python csms_simulator.py

# Sonra saldırıyı başlat
python attack_simulator.py --attack duplicate_booking --booking-scenario duplicate_id
```

Bu komut:
- ✅ Gerçek OCPP mesajları gönderir
- ✅ IDS alert'leri üretir
- ✅ Dashboard'da görünür

## 📊 Beklenen Dashboard Görünümü

### Senaryo #5 Alert'leri Sonrası:

```
🚨 Real-Time Alerts
├── 🔴 CRITICAL: 3
├── 🟠 HIGH: 1
├── 🟡 MEDIUM: 0
└── 🟢 LOW: 0

📋 Son Alert'ler:
├── [CRITICAL] DUPLICATE_RESERVATION_ID
├── [CRITICAL] MULTIPLE_CONNECTOR_RESERVATIONS
├── [CRITICAL] RESERVATION_TRANSACTION_MISMATCH
└── [HIGH] RESERVATION_ID_REUSE
```

## 🔄 Adım Adım Test

### 1. API Server Çalışıyor mu?
```bash
python3 -c "import requests; print('OK' if requests.get('http://localhost:8000/api/health').status_code == 200 else 'FAIL')"
```

### 2. Test Alert'leri Oluştur
```bash
python test_scenario_05_dashboard.py
```

### 3. Dashboard'u Yenile
- Browser'da F5 veya Ctrl+R
- Alert'ler görünmeli

### 4. Gerçek Saldırı Test Et
```bash
# CSMS başlat
python csms_simulator.py

# Saldırı başlat
python attack_simulator.py --attack duplicate_booking
```

## 🐛 Sorun Giderme

### Alert'ler görünmüyor:

1. **API'yi kontrol et:**
   ```bash
   python3 -c "import requests; print(requests.get('http://localhost:8000/api/alerts?count=10').json())"
   ```

2. **Dashboard'u yenile:**
   - F5 veya Ctrl+R
   - Otomatik yenileme aktif mi kontrol et (sidebar)

3. **API log'larını kontrol et:**
   ```bash
   tail -f logs/api_server.log
   ```

### İstatistikler 0 görünüyor:

1. **Bridge çalışıyor mu?**
   ```bash
   ps aux | grep secure_bridge
   ```

2. **Bridge'i başlat:**
   ```bash
   python secure_bridge.py
   ```

3. **Bridge state'i kontrol et:**
   ```bash
   python3 -c "import requests; print(requests.get('http://localhost:8000/api/bridge/status').json())"
   ```

## ✅ Başarı Kriterleri

- ✅ Dashboard açılıyor: http://localhost:8501
- ✅ API çalışıyor: http://localhost:8000/api/health
- ✅ Alert'ler görünüyor: Senaryo #5 alert'leri listede
- ✅ İstatistikler güncelleniyor: Blok sayısı, alert sayısı artıyor

## 📝 Notlar

- Test alert'leri geçicidir, sayfayı yenilediğinizde kaybolabilir
- Gerçek alert'ler için bridge ve saldırı simülatörünü çalıştırın
- Bridge çalışmadan istatistikler 0 kalır (normal)

