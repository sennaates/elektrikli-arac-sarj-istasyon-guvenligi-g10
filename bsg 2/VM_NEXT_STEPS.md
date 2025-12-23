# 🐧 Ubuntu VM'de Sonraki Adımlar

## ✅ Adım 1: Shared Folder'ı Bulun

Ubuntu VM'de terminal açın ve şunları çalıştırın:

```bash
# Shared folder'ı ara
ls -la /mnt/
ls -la /media/
ls -la ~/Desktop/

# Eğer görünmüyorsa, mount edin
sudo mkdir -p /mnt/bsg
```

## 📋 Adım 2: Projeyi Home Dizinine Kopyalayın

```bash
# Projeyi home dizinine kopyala (daha kolay çalışmak için)
cp -r /mnt/bsg ~/bsg
# VEYA eğer başka bir yerdeyse:
# cp -r /media/bsg ~/bsg
# cp -r ~/Desktop/bsg ~/bsg

# Kontrol et
cd ~/bsg
ls -la
# requirements.txt, tests/, src/ klasörlerini görmelisiniz
```

## 🔧 Adım 3: Sistem Paketlerini Kurun

```bash
# Sistem güncellemesi
sudo apt-get update

# Gerekli paketler
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    can-utils \
    iproute2

# CAN modüllerini yükle
sudo modprobe can
sudo modprobe can_raw
sudo modprobe vcan

# vcan0 oluştur
sudo ip link add dev vcan0 type vcan 2>/dev/null || true
sudo ip link set up vcan0

# Kontrol et
ip link show vcan0
# Çıktı: vcan0: <NOARP,UP,LOWER_UP> ... state UNKNOWN
```

## 📦 Adım 4: Proje Bağımlılıklarını Kurun

```bash
# Proje dizininde olduğunuzdan emin olun
cd ~/bsg

# Virtual environment oluştur
python3 -m venv venv

# Activate et
source venv/bin/activate

# Bağımlılıkları yükle
pip install --upgrade pip
pip install -r requirements.txt
```

## ✅ Adım 5: CAN Bus'ı Test Edin

```bash
# Terminal 1: CAN trafiğini dinle
candump vcan0

# Yeni bir terminal açın (Terminal 2)
# Test mesajı gönder
cansend vcan0 200#1234ABCDEF

# Terminal 1'de mesajı görmelisiniz!
```

## 🚀 Adım 6: CLAC-SCO Senaryosunu Çalıştırın

```bash
# Virtual environment aktif olduğundan emin ol
cd ~/bsg
source venv/bin/activate

# Senaryoyu çalıştır
python3 tests/scenario_clac_sco.py
```

---

## 🎯 Beklenen Çıktı

Başarılı çalıştırmada şunları görmelisiniz:

```
================================================================================
CLAC-SCO: COORDINATED LOAD ALTERATION ATTACK
================================================================================
🔌 5 Charge Point başlatılıyor...
✅ 5 Charge Point bağlandı
📊 Normal akış başlatılıyor (baseline)...
✅ Baseline oluşturuldu
🚨 SALDIRI BAŞLATILIYOR: CLAC-SCO Coordinated Attack
⚠️  5/5 CP'ye saldırı komutu gönderildi
🔍 Anomali tespiti yapılıyor...
✅ CLAC-SCO saldırı senaryosu başarıyla tamamlandı!
```

---

## 🔍 Sorun Giderme

### Shared folder görünmüyor
```bash
# Farklı yerlerde ara
find /mnt -name "bsg" 2>/dev/null
find /media -name "bsg" 2>/dev/null
find ~ -name "requirements.txt" 2>/dev/null
```

### CAN modülleri yüklenemiyor
```bash
# Kernel modüllerini kontrol et
lsmod | grep can

# Manuel yükle
sudo modprobe can can_raw vcan
```

### vcan0 zaten var
```bash
# Mevcut vcan0'i sil ve yeniden oluştur
sudo ip link delete vcan0
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

---

**Hazırlayan**: Auto (Cursor AI)
**Tarih**: 2025-01-27

