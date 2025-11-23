# 🚀 Hızlı Başvuru Kılavuzu

## ⚡ 30 Saniyede Başlangıç

```bash
# 1. Virtual environment kur
python3 -m venv venv && source venv/bin/activate

# 2. Bağımlılıkları kur
pip install -r requirements.txt

# 3. vcan0 kur
bash setup_vcan.sh

# 4. ML modelini eğit (opsiyonel)
python training/train_ml_model.py

# 5. Testleri çalıştır
python tests/test_system.py

# 6. Sistemi başlat (4 terminal gerekli)
# Terminal 1: CSMS
python csms_simulator.py

# Terminal 2: Bridge
python secure_bridge.py

# Terminal 3: API
python api_server.py

# Terminal 4: Dashboard
streamlit run dashboard.py

# 7. Saldırı simüle et (5. terminal)
python attack_simulator.py --attack combined
```

---

## 📁 Dosya Yapısı Özeti

```
githubsmlsyn/
├── 🔧 Core Files
│   ├── secure_bridge.py         # Ana bridge servisi
│   ├── api_server.py            # REST API + WebSocket
│   ├── dashboard.py             # Streamlit dashboard
│   ├── attack_simulator.py      # Saldırı simülatörü
│   └── csms_simulator.py        # Test CSMS sunucusu
│
├── 🛠️ Utils
│   ├── blockchain.py            # Blockchain implementasyonu
│   ├── can_handler.py           # CAN-Bus interface
│   ├── ids.py                   # Rule-based IDS
│   └── ml_ids.py                # ML-based IDS
│
├── 🧪 Tests
│   ├── test_system.py           # Birim testleri
│   └── anomaly_scenarios_template.py  # Senaryo template
│
├── 🎓 Training
│   └── train_ml_model.py        # ML model eğitimi
│
├── 🚀 Scripts
│   ├── setup_vcan.sh            # vcan0 kurulumu
│   └── quick_start.sh           # Hızlı başlatma
│
└── 📄 Docs
    ├── README.md                # Ana dokümantasyon
    ├── QUICK_REFERENCE.md       # Bu dosya
    └── LICENSE                  # MIT License
```

---

## 🎯 Yaygın Komutlar

### Sistem Kontrolleri

```bash
# vcan0 durumu
ip link show vcan0

# Python paketleri
pip list | grep -E "ocpp|can|fastapi|streamlit|sklearn"

# Logları görüntüle
tail -f logs/bridge.log

# Blockchain doğrula
curl http://localhost:8000/api/blockchain/stats

# IDS istatistikleri
curl http://localhost:8000/api/ids/stats

# Son alert'ler
curl http://localhost:8000/api/alerts?count=5
```

### Testler

```bash
# Tüm testler
python tests/test_system.py

# Sadece blockchain
python -c "from utils.blockchain import *; bc = Blockchain(); print(bc)"

# Sadece IDS
python -c "from utils.ids import *; ids = RuleBasedIDS(); print(ids.get_stats())"

# ML model test
python -c "from utils.ml_ids import *; print('ML available:', SKLEARN_AVAILABLE)"
```

### Saldırı Simülasyonları

```bash
# Unauthorized injection
python attack_simulator.py --attack injection

# CAN flood
python attack_simulator.py --attack flood

# Replay attack
python attack_simulator.py --attack replay

# Invalid CAN ID
python attack_simulator.py --attack invalid_id

# High entropy (ML için)
python attack_simulator.py --attack entropy

# Kombine saldırı
python attack_simulator.py --attack combined

# Tümü
python attack_simulator.py --attack all
```

---

## 🔍 Sorun Giderme Checklist

### ❌ Problem: Sistem başlamıyor

**Kontroller:**
- [ ] `venv` aktif mi? → `source venv/bin/activate`
- [ ] Paketler kurulu mu? → `pip install -r requirements.txt`
- [ ] `vcan0` var mı? → `ip link show vcan0`
- [ ] `.env` dosyası var mı? → `cp .env.example .env`
- [ ] Port'lar boş mu? → `lsof -i :8000,8501,9000`

### ❌ Problem: Dashboard veri göstermiyor

**Kontroller:**
- [ ] API çalışıyor mu? → `curl http://localhost:8000/api/health`
- [ ] Bridge çalışıyor mu? → `ps aux | grep secure_bridge`
- [ ] Logları kontrol et → `tail logs/bridge.log`

### ❌ Problem: CAN frame gönderilmiyor

**Kontroller:**
- [ ] `vcan0` up durumunda mı? → `ip link show vcan0`
- [ ] python-can kurulu mu? → `pip show python-can`
- [ ] Hata logları → Bridge terminaline bak

### ❌ Problem: ML model çalışmıyor

**Kontroller:**
- [ ] sklearn kurulu mu? → `pip install scikit-learn`
- [ ] Model eğitildi mi? → `ls -lh models/isolation_forest.pkl`
- [ ] `.env`'de ML aktif mi? → `ENABLE_ML_IDS=true`

---

## 📊 Beklenen Çıktılar

### ✅ Başarılı Bridge Başlangıcı

```
========================================
SECURE OCPP-TO-CAN BRIDGE BAŞLATILIYOR
========================================
[1/3] ✓ CAN Bus'a bağlanıldı: vcan0
[2/3] ✓ Blockchain başlatıldı
[3/3] ✓ IDS aktif
✓ Bridge aktif!
```

### ✅ Başarılı Test Çıktısı

```
🧪 ========================================
🧪  SİSTEM TESTLERİ BAŞLATILIYOR
🧪 ========================================

✅ Blockchain: BAŞARILI
✅ OCPP → CAN Mapping: BAŞARILI
✅ Rule-Based IDS: BAŞARILI
✅ ML-Based IDS: BAŞARILI
✅ Feature Extraction: BAŞARILI

Toplam: 5/5 test başarılı (100%)
```

### ✅ Başarılı Saldırı Tespiti

```
🚨 SALDIRI: Unauthorized CAN Injection başlatılıyor...
⚠ IDS Alert: CAN ID 0x200 için yetkisiz frame tespit edildi
✓ Blockchain'e ALERT bloğu eklendi
✓ Dashboard'a bildirim gönderildi
```

---

## 🎓 Anomali Senaryolarını Ekleme

### 1. Template'i Kopyala

```bash
cp tests/anomaly_scenarios_template.py tests/my_scenarios.py
```

### 2. Senaryonu Tanımla

```python
{
    "id": 11,
    "name": "Senaryom",
    "category": "Injection",
    "severity": "HIGH",
    "description": "Detaylı açıklama",
    "attack_steps": ["Adım 1", "Adım 2"],
    "expected_detection": {
        "method": "Rule-based IDS",
        "rule": "UNAUTHORIZED_CAN_INJECTION",
        "alert_severity": "HIGH"
    },
    "implementation": "custom_attack_function()",
    "success_criteria": ["Kriter 1", "Kriter 2"]
}
```

### 3. Attack Simulator'a Ekle

```python
# attack_simulator.py içine
def my_custom_attack(self):
    """Senaryom implementasyonu"""
    # Saldırı kodu
    pass
```

### 4. Test Et

```bash
python attack_simulator.py --attack my_custom
```

---

## 📈 Performans Metrikleri (Referans)

| Metrik | Değer | Not |
|--------|-------|-----|
| Blockchain write | ~0.5ms | SHA-256 + ECDSA |
| Rule-IDS latency | <1ms | Python native |
| ML-IDS latency | ~10ms | Isolation Forest |
| CAN throughput | 1000+ fps | vcan0 |
| Dashboard refresh | 3s | Configurable |
| API response | <50ms | FastAPI |

---

## 🔗 Faydalı Linkler

### Dokümantasyon
- [OCPP 1.6 Spec](https://www.openchargealliance.org/protocols/ocpp-16/)
- [python-can Docs](https://python-can.readthedocs.io/)
- [Isolation Forest Paper](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)

### API Endpoints
- Health: http://localhost:8000/api/health
- Blockchain: http://localhost:8000/api/blockchain/stats
- IDS: http://localhost:8000/api/ids/stats
- Alerts: http://localhost:8000/api/alerts
- Docs: http://localhost:8000/docs (Swagger UI)

### Dashboard
- Main: http://localhost:8501
- Metrics: http://localhost:8501/?stats=1

---

## 💡 Pro Tips

### 1. tmux Kullanımı (Önerilen)

```bash
# Session başlat
tmux new -s ocpp

# Window'ları ayır
Ctrl+B, C  # Yeni window
Ctrl+B, N  # Sonraki window
Ctrl+B, P  # Önceki window
Ctrl+B, D  # Detach

# Geri dön
tmux attach -t ocpp

# Kapat
tmux kill-session -t ocpp
```

### 2. Log Monitoring

```bash
# Real-time log takibi
tail -f logs/bridge.log | grep -E "ALERT|ERROR|WARNING"

# Sadece alert'ler
tail -f logs/bridge.log | grep ALERT

# Son 100 satır
tail -n 100 logs/bridge.log
```

### 3. Dashboard Optimizasyonu

`.env` dosyasında:
```env
# Yüksek performans
DASHBOARD_REFRESH_INTERVAL=1

# Düşük kaynak kullanımı
DASHBOARD_REFRESH_INTERVAL=10
```

### 4. ML Model Fine-Tuning

```python
# training/train_ml_model.py içinde
ml_ids = MLBasedIDS(
    contamination=0.05,  # Daha hassas (daha çok anomali)
    # contamination=0.2  # Daha toleranslı
)
```

---

## 📞 Destek

Sorularınız için:
- 📖 README.md'yi inceleyin
- 🧪 `tests/test_system.py`'yi çalıştırın
- 📊 Dashboard loglarını kontrol edin
- 🔍 GitHub Issues'a bakın

---

**Son Güncelleme:** 2024-11-23  
**Versiyon:** 1.0.0

