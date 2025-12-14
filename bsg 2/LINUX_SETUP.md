# 🐧 Linux'ta CAN Bus ile Çalıştırma Rehberi

**ÖNEMLİ**: macOS'ta Docker container içinde CAN bus desteği **mümkün değil**. Gerçek CAN bus için Linux gerekli.

## 🚀 Hızlı Çözüm: Linux VM

### Seçenek 1: VirtualBox (Ücretsiz)

1. **VirtualBox İndir**: https://www.virtualbox.org/
2. **Ubuntu 22.04 ISO İndir**: https://ubuntu.com/download
3. **VM Oluştur**: 
   - RAM: En az 2GB
   - Disk: En az 20GB
   - Network: NAT veya Bridged
4. **Ubuntu Kur**: Standart kurulum
5. **CAN Bus Kur**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y can-utils iproute2
   sudo modprobe can can_raw vcan
   sudo ip link add dev vcan0 type vcan
   sudo ip link set up vcan0
   ```
6. **Projeyi Kopyala**: VM içine projeyi kopyalayın
7. **Test Çalıştır**: `python3 tests/scenario_clac_sco.py`

### Seçenek 2: Parallels/VMware (macOS için)

Aynı adımlar, sadece VM yazılımı farklı.

### Seçenek 3: Cloud Linux (AWS EC2, DigitalOcean, vb.)

1. Linux instance oluştur
2. SSH ile bağlan
3. CAN bus kur
4. Projeyi yükle
5. Test çalıştır

## 📋 Linux'ta Adım Adım Kurulum

### 1. Sistem Gereksinimleri

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv can-utils iproute2
```

### 2. CAN Bus Kurulumu

```bash
# CAN modüllerini yükle
sudo modprobe can
sudo modprobe can_raw
sudo modprobe vcan

# vcan0 oluştur
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# Kontrol et
ip link show vcan0
# Çıktı: vcan0: <NOARP,UP,LOWER_UP> ... state UNKNOWN
```

### 3. Proje Kurulumu

```bash
# Projeyi klonla/kopyala
cd /path/to/bsg

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 4. Test Çalıştırma

```bash
# CAN bus'ın çalıştığını test et
candump vcan0  # Terminal 1

# Başka terminal'de
cansend vcan0 200#1234ABCDEF

# Test çalıştır
python3 tests/scenario_clac_sco.py
```

## 🔧 Otomatik Kurulum Scripti

```bash
# Linux'ta çalıştır
sudo bash docker/setup_can_linux.sh
```

## ⚠️ macOS'ta Neden Çalışmıyor?

1. **Kernel Modülleri**: macOS kernel'inde CAN bus modülleri yok
2. **Docker Limitation**: Container host kernel'ini kullanır
3. **Virtual CAN**: `vcan` Linux kernel'ine özgü

**Çözüm**: Linux VM veya Linux host kullanın.

## 📊 Test Sonuçları

Linux'ta çalıştırdığınızda:
- ✅ vcan0 oluşturulur
- ✅ CAN modülleri yüklenir
- ✅ Gerçek CAN mesajları gönderilir/alınır
- ✅ `candump vcan0` ile trafik görülebilir

## 🎓 Dönem Ödevi İçin

Hoca gerçek CAN bus istiyorsa:

1. **Linux VM kullanın** (en kolay çözüm)
2. **Test sonuçlarını gösterin**:
   - `candump vcan0` çıktısı
   - CAN mesaj logları
   - Test başarı mesajları
3. **Dokümantasyonda belirtin**: "Linux VM'de test edilmiştir"

---

**Öneri**: VirtualBox ile Ubuntu VM oluşturup orada çalıştırın. 30 dakikada hazır olur.

