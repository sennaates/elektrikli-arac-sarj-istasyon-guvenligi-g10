# Kurulum Kılavuzu

## 📋 Sistem Gereksinimleri

### İşletim Sistemi
- **Linux** (Ubuntu 20.04+ önerilir)
- **WSL2** (Windows üzerinde)
- **macOS** (sınırlı destek)

### Python
- Python 3.9 veya üzeri

### Sistem Paketleri

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    python3-venv \
    python3-pip \
    linux-modules-extra-$(uname -r) \
    can-utils \
    iproute2 \
    openssl

# CAN kernel modules yüklü olmalı
sudo modprobe can
sudo modprobe can_raw
sudo modprobe vcan
```

### Ağ İzleme Araçları (Opsiyonel)

```bash
# MitM ve analiz için
sudo apt-get install -y \
    wireshark \
    tcpdump \
    net-tools

# veya Homebrew (macOS)
brew install wireshark
```

## 🚀 Kurulum Adımları

### 1. Projeyi İndirin

```bash
cd /path/to/your/workspace
# Eğer git repo ise:
# git clone <repo-url> bsg
# cd bsg
```

### 2. Sanal Ortam Oluşturun

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# veya Windows: venv\Scripts\activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Not**: Bazı paketler derleme gerektirebilir. Eğer hata alırsanız:

```bash
# System dependencies
sudo apt-get install -y python3-dev libssl-dev build-essential

# Tekrar deneyin
pip install -r requirements.txt
```

### 4. CAN Arayüzünü Kurun

```bash
# Scriptleri çalıştırılabilir yap
chmod +x scripts/*.sh

# Sanal CAN arayüzü oluştur
sudo bash scripts/setup_vcan.sh

# Kontrol
ip link show vcan0
# "UP,LOWER_UP" görmelisiniz
```

### 5. Sertifikaları Oluşturun

```bash
# Test TLS sertifikaları oluştur
bash scripts/generate_certs.sh

# Kontrol
ls -la certs/weak/
ls -la certs/strong/
```

## ✅ Kurulum Doğrulama

### Test 1: Python Modülleri

```bash
python -c "import can; import websockets; import cryptography; print('✅ Tüm modüller yüklü')"
```

### Test 2: CAN Arayüzü

```bash
# CAN mesajı gönder
cansend vcan0 123#DEADBEEF

# CAN mesajı dinle (başka terminalde)
candump vcan0

# Sonucu görmelisiniz
```

### Test 3: Proje İmportları

```bash
python -c "
from src.ocpp.central_system.simulator import CSMSimulator
from src.ocpp.charge_point.simulator import ChargePointSimulator
from src.can_bus.can_simulator import CANBusSimulator
from src.bridge.gateway import OCPPCANGateway
print('✅ Proje modülleri çalışıyor')
"
```

### Test 4: Unit Testler

```bash
# Tüm testleri çalıştır
pytest tests/ -v

# Veya belirli bir senaryoyu test et
pytest tests/scenario_1_plain_ws.py -v -s
```

## 🔧 Yapılandırma

### OCPP Yapılandırması

`config/ocpp_config.yaml` dosyasını düzenleyebilirsiniz:

```yaml
central_system:
  host: "localhost"
  port: 9000

charge_point:
  default_cp_id: "CP001"
  connectors:
    - id: 1
      type: "Type2"
      max_power: 22
```

### CAN Yapılandırması

`config/can_config.yaml` dosyasını düzenleyebilirsiniz:

```yaml
interface:
  name: "vcan0"
  bitrate: 500000

can_ids:
  ocpp:
    remote_start: 0x200
    meter_values: 0x300
```

## 🐛 Sorun Giderme

### Problem: "Permission denied" / vcan0 oluşturulamıyor

**Çözüm:**
```bash
# Root olarak çalıştırın
sudo bash scripts/setup_vcan.sh

# veya kernel modüllerini kontrol edin
sudo modprobe can can_raw vcan
```

### Problem: "Module not found: src"

**Çözüm:**
```bash
# Proje root dizininde olduğunuzdan emin olun
pwd  # /path/to/bsg olmalı

# PYTHONPATH ayarlayın
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Problem: "No module named 'can'"

**Çözüm:**
```bash
# Virtual environment aktif mi kontrol edin
which python  # venv/bin/python göstermeli

# Tekrar yükleyin
pip install python-can
```

### Problem: CAN mesajları görünmüyor

**Çözüm:**
```bash
# vcan0 arayüzü UP mi?
ip link show vcan0

# Kullanıcı izinleri
sudo ip link set vcan0 type can

# can-utils test
cansend vcan0 123#TEST
```

### Problem: TLS hataları

**Çözüm:**
```bash
# Sertifikaları yeniden oluşturun
rm -rf certs/
bash scripts/generate_certs.sh

# OpenSSL versiyonunu kontrol edin
openssl version
```

### Problem: Port kullanımda

**Çözüm:**
```bash
# Hangi process 9000 portunu kullanıyor?
sudo netstat -tulpn | grep 9000

# Process'i sonlandırın
kill -9 <PID>

# Veya farklı port kullanın
python -m src.ocpp.central_system.simulator --port 9001
```

## 🚀 Hızlı Başlangıç

Kurulum tamamlandıktan sonra:

```bash
# Senaryo 1: Plain WebSocket demo
bash scripts/run_demo.sh plain_ws

# Veya manuel
python -m src.ocpp.central_system.simulator --scenario plain_ws &
python -m src.ocpp.charge_point.simulator --scenario plain_ws
```

## 📚 Sonraki Adımlar

1. [USAGE.md](USAGE.md) - Kullanım kılavuzunu okuyun
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Proje mimarisini inceleyin
3. Demo senaryolarını deneyin
4. Test senaryolarını çalıştırın

## 🔗 Kaynaklar

- [CAN-Bus Spec](https://en.wikipedia.org/wiki/CAN_bus)
- [OCPP Protocol](https://www.openchargealliance.org/)
- [python-can Docs](https://python-can.readthedocs.io/)
- [WebSockets Library](https://websockets.readthedocs.io/)

## 💡 İpuçları

- `venv` her yeni terminalde aktif etmeyi unutmayın
- Root olmadan CAN arayüzlerini kurmak için `sudoers` ayarlayın
- Gerçek donanım testleri için USB-CAN adaptör kullanın
- Logları inceleyerek problemleri teşhis edin

## 📞 Yardım

Sorun yaşarsanız:
1. Log dosyalarını kontrol edin
2. `pytest tests/ -v` ile testleri çalıştırın
3. GitHub issue oluşturun

