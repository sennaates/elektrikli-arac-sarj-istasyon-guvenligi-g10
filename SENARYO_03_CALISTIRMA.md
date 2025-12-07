# 🚀 Senaryo #3 Test Rehberi

## Hızlı Başlangıç (Docker)

### 1. Docker Container'ı Başlat

```powershell
cd C:\Users\devot\Desktop\BsgProjesi\simulasyon-projesi

# Container'ı oluştur ve başlat
docker-compose up -d --build

# Container'a bağlan
docker exec -it ev-charging-simulation bash
```

### 2. Sanal CAN Interface Kur (Container içinde)

```bash
# vcan0 kur
./setup_vcan.sh

# Kontrol et
ip link show vcan0
```

### 3. Senaryonuzu Test Edin

#### Test 1: Rate Drop Saldırısı

```bash
# Virtual environment aktif et
source venv/bin/activate

# Saldırıyı başlat (2 dakika)
python attack_simulator.py --attack sampling \
    --sampling-scenario rate_drop \
    --sampling-duration 120

# Beklenen çıktı:
# ✓ Rate Drop tamamlandı: 2 sample, 1.0 sample/min
# Alert: SAMPLING_RATE_DROP
```

#### Test 2: Peak Smoothing Saldırısı

```bash
python attack_simulator.py --attack sampling \
    --sampling-scenario peak_smoothing \
    --sampling-duration 120

# Beklenen çıktı:
# ✓ Peak smoothing tamamlandı
# Alert: ENERGY_VARIANCE_DROP
```

#### Test 3: Buffer Manipulation

```bash
python attack_simulator.py --attack sampling \
    --sampling-scenario buffer_manipulation \
    --sampling-duration 120

# Beklenen çıktı:
# ✓ Buffer manipulation tamamlandı
# Alert: BUFFER_MANIPULATION
```

### 4. Tam Sistem Testi (4 Terminal Gerekli)

Container'da 4 ayrı terminal açın:

```powershell
# Terminal 1: CSMS Simulator
docker exec -it ev-charging-simulation bash
source venv/bin/activate
python csms_simulator.py

# Terminal 2: Secure Bridge
docker exec -it ev-charging-simulation bash
source venv/bin/activate
python secure_bridge.py

# Terminal 3: Dashboard
docker exec -it ev-charging-simulation bash
source venv/bin/activate
streamlit run dashboard.py

# Terminal 4: Attack Simulator
docker exec -it ev-charging-simulation bash
source venv/bin/activate
python attack_simulator.py --attack sampling --sampling-scenario rate_drop
```

Dashboard: http://localhost:8501

### 5. Test Sonuçlarını Görüntüle

```bash
# Alert loglarını kontrol et
cat logs/alerts.log

# Blockchain verilerini kontrol et
cat logs/blockchain.log
```

## Alternatif: Hızlı Test (Sadece Simülatör)

```bash
# Direkt olarak test scripti çalıştır
python tests/scenario_03_sampling_manipulation.py

# Çıktı:
# ✅ SCENARIO-03-001: Rate Drop Detection - PASSED
# ✅ SCENARIO-03-002: Peak Smoothing Detection - PASSED
# ✅ SCENARIO-03-003: Buffer Manipulation Detection - PASSED
```

## Sorun Giderme

### Hata: "vcan0 not found"
```bash
./setup_vcan.sh
```

### Hata: "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Dashboard açılmıyor
```bash
# Port kontrolü
netstat -tlnp | grep 8501

# Dashboard'ı yeniden başlat
streamlit run dashboard.py --server.port 8501
```

## Temizlik

```powershell
# Container'ı durdur ve temizle
docker-compose down

# Volume'leri de temizle
docker-compose down -v
```

## Beklenen Sonuçlar

### Rate Drop Tespiti (60 saniye içinde)
```json
{
  "alert_type": "SAMPLING_RATE_DROP",
  "severity": "HIGH",
  "samples_per_minute": 5,
  "threshold": 30
}
```

### Variance Drop Tespiti (300 saniye içinde)
```json
{
  "alert_type": "ENERGY_VARIANCE_DROP",
  "severity": "CRITICAL",
  "variance_drop": 88
}
```

### Buffer Manipulation Tespiti (30 saniye içinde)
```json
{
  "alert_type": "BUFFER_MANIPULATION",
  "severity": "CRITICAL",
  "buffer_ratio": 36.0
}
```

## Detaylı Kılavuz

Daha fazla bilgi için:
- `SCENARIO_03_GUIDE.md` - Detaylı kullanım kılavuzu
- `README_SCENARIO_03.md` - Senaryo özeti
- `tests/scenario_03_sampling_manipulation.py` - Test kod örneği
