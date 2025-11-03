# Kullanım Kılavuzu

## 📋 Hızlı Başlangıç

### 1. Kurulum

```bash
# Bağımlılıkları kur
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# veya: venv\Scripts\activate  # Windows

pip install -r requirements.txt

# Sanal CAN arayüzünü kur
chmod +x scripts/setup_vcan.sh
sudo bash scripts/setup_vcan.sh

# Sertifikaları oluştur
chmod +x scripts/generate_certs.sh
bash scripts/generate_certs.sh
```

### 2. Can-utils Kurulumu (CAN Trafiği İzlemek İçin)

```bash
# Ubuntu/Debian
sudo apt-get install can-utils

# Diğer dağıtımlar için can-utils kaynak koddan derle
```

### 3. Demo Çalıştırma

```bash
# Senaryo 1: Plain WebSocket (En zayıf)
bash scripts/run_demo.sh plain_ws

# Senaryo 2: Zayıf TLS
bash scripts/run_demo.sh weak_tls

# Senaryo 3: Güçlü TLS
bash scripts/run_demo.sh strong_tls
```

## 🔧 Manuel Çalıştırma

### Terminal 1: CSMS Başlatma

```bash
# Plain WebSocket
python -m src.ocpp.central_system.simulator --scenario plain_ws --port 9000

# Zayıf TLS
python -m src.ocpp.central_system.simulator --scenario weak_tls --port 9000

# Güçlü TLS
python -m src.ocpp.central_system.simulator --scenario strong_tls --port 9000
```

### Terminal 2: Charge Point Başlatma

```bash
# Plain WebSocket
python -m src.ocpp.charge_point.simulator --scenario plain_ws --cp-id CP001

# Zayıf TLS
python -m src.ocpp.charge_point.simulator --scenario weak_tls --cp-id CP001

# Güçlü TLS
python -m src.ocpp.charge_point.simulator --scenario strong_tls --cp-id CP001
```

### Terminal 3: CAN Trafiğini İzleme

```bash
# vcan0 trafiğini izle
candump vcan0

# Belirli CAN ID'lerini filtrele
candump vcan0 | grep "0x200\|0x201\|0x300"

# Her mesajın detayını göster
candump vcan0 -L -a
```

### Terminal 4: MitM Proxy (Opcak)

```bash
# Plain WebSocket için MitM saldırısı
python -m src.attacks.mitm_proxy --proxy-port 9090 --target-port 9000
```

## 🧪 Test Senaryoları

### Senaryo 1: Plain WebSocket Test

```bash
pytest tests/scenario_1_plain_ws.py -v -s
```

**Beklenen Davranış:**
- ✅ CSMS ve CP arasında bağlantı kurulur
- ✅ BootNotification gönderilir
- ✅ RemoteStartTransaction mesajları CAN'a çevrilir
- ⚠️  Güvenlik yok - MitM saldırılarına açık

### Senaryo 2: Weak TLS Test

```bash
# Test dosyası eklenecek
pytest tests/scenario_2_weak_tls.py -v -s
```

**Beklenen Davranış:**
- ✅ TLS şifreleme aktif
- ⚠️  TLS 1.0 kullanılıyor (eski protokol)
- ⚠️  Self-signed sertifikalar
- ⚠️  Certificate verification kapalı

### Senaryo 3: Strong TLS Test

```bash
# Test dosyası eklenecek
pytest tests/scenario_3_strong_tls.py -v -s
```

**Beklenen Davranış:**
- ✅ TLS 1.2+ kullanılıyor
- ✅ Güçlü cipher suites
- ✅ Certificate verification açık
- ✅ Mutual TLS desteği

## 📊 CAN IDS Demo

```bash
# CAN Intrusion Detection System demo'sunu çalıştır
python -m src.detection.can_ids

# Çıktı:
# CAN Intrusion Detection System Demo
# ==================================================
# 1. Normal mesajlar gönderiliyor...
# ✅ Baseline oluşturuldu: 3 CAN ID
# 2. Anomali tespiti test ediliyor...
# 🚨 ANOMALI TESPİT EDİLDİ: Beklenmeyen CAN ID: 0x9ff
#    ✅ Anomali tespit edildi: Beklenmeyen CAN ID: 0x9ff
# 📊 İstatistikler:
#    Toplam mesaj: 21
#    Benzersiz ID: 4
#    Anomali sayısı: 1
```

## 🎭 MitM Saldırısı Testi

### Adım 1: Normal Akışı Başlat

```bash
# Terminal 1
python -m src.ocpp.central_system.simulator --scenario plain_ws --port 9000

# Terminal 2
python -m src.ocpp.charge_point.simulator --scenario plain_ws --cp-id CP001 --csms-url ws://localhost:9000/charge_point/cp001
```

### Adım 2: MitM Proxy Başlat

```bash
# Terminal 3
python -m src.attacks.mitm_proxy --proxy-port 9090 --target-port 9000
```

### Adım 3: CP'yi Proxy Üzerinden Bağla

```bash
# Terminal 4 (yeni CP)
python -m src.ocpp.charge_point.simulator --scenario plain_ws --cp-id CP002 --csms-url ws://localhost:9090/charge_point/cp002
```

**Sonuç:**
- ✅ Proxy tüm mesajları intercept eder
- ⚠️  RemoteStartTransaction mesajları manipüle edilir
- 🚨 Mesaj bütünlüğü bozulur

## 📈 Performans Testi

```bash
# Tüm senaryolar için performans testi
pytest tests/ -v --durations=10

# CAN trafiği analizi
python scripts/analyze_can_traffic.py

# Güvenlik analizi
python scripts/security_analysis.py
```

## 🔍 Debugging

### Log Seviyesini Değiştirme

```bash
# DEBUG seviyesinde çalıştır
python -m src.ocpp.central_system.simulator --scenario plain_ws --log-level DEBUG

# Sadece WARNING ve ERROR göster
python -m src.ocpp.charge_point.simulator --scenario plain_ws --log-level WARNING
```

### CAN Hatalarını Giderme

```bash
# CAN arayüzü durumunu kontrol et
ip link show vcan0

# CAN arayüzünü yeniden başlat
sudo ip link delete vcan0
sudo bash scripts/setup_vcan.sh

# CAN trafiğini manuel olarak test et
cansend vcan0 200#1234ABCDEF
candump vcan0
```

## 🛠️ Gelişmiş Kullanım

### Custom CAN Mapping

```python
from src.bridge.mapper import OCPPCANMapper

mapper = OCPPCANMapper()

# Custom mapping ekle
mapper.mappings['CustomAction'] = CANMapping(
    can_id=0x400,
    name='CustomAction',
    direction='ocpp_to_can',
    payload_format='HH'
)
```

### Multiple CP Bağlantıları

```bash
# Terminal 1: CSMS
python -m src.ocpp.central_system.simulator --scenario plain_ws

# Terminal 2: CP1
python -m src.ocpp.charge_point.simulator --scenario plain_ws --cp-id CP001

# Terminal 3: CP2
python -m src.ocpp.charge_point.simulator --scenario plain_ws --cp-id CP002

# Terminal 4: CP3
python -m src.ocpp.charge_point.simulator --scenario plain_ws --cp-id CP003
```

## 📚 Daha Fazla Bilgi

- [README.md](README.md) - Proje genel bakış
- [config/](config/) - Yapılandırma dosyaları
- [docs/](docs/) - Detaylı dokümantasyon

## ⚠️ Önemli Notlar

1. **Güvenlik**: Tüm testler izole ortamda yapılmalı
2. **Root Gereksinimi**: vcan0 kurulumu için sudo gerekir
3. **Port Çakışmaları**: Aynı anda sadece bir CSMS çalışabilir
4. **CAN Hızı**: Gerçek CAN bus'larda farklı bitrate'ler kullanılabilir

## 🐛 Sorun Giderme

### "ModuleNotFoundError: No module named 'src'"

```bash
# Proje root dizininde olduğunuzdan emin olun
pwd  # /home/sudem/bsg olmalı

# veya PYTHONPATH'i ayarlayın
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### "PermissionError: cannot create virtual CAN interface"

```bash
# Root yetkisiyle çalıştırın
sudo bash scripts/setup_vcan.sh
```

### "WebSocket connection failed"

```bash
# Portların başka bir şey tarafından kullanılmadığını kontrol edin
sudo netstat -tulpn | grep 9000

# Veya farklı bir port kullanın
python -m src.ocpp.central_system.simulator --port 9001
```

## 📞 Destek

Sorularınız için proje issue tracker'ını kullanın.

