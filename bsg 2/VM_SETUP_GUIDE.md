# 🐧 Ubuntu VM'de CLAC-SCO Senaryosu Çalıştırma Rehberi

## 📋 Adım 1: Projeyi VM'e Aktarma

### Seçenek A: Git ile Clone (Önerilen)
```bash
# Ubuntu VM'de terminal aç
sudo apt-get update
sudo apt-get install -y git

# Projeyi klonla (GitHub'da ise)
git clone <repo-url> bsg
cd bsg

# VEYA macOS'tan kopyaladıysanız, direkt devam edin
```

### Seçenek B: Shared Folder (UTM)
1. UTM'de VM ayarlarına git
2. "Shared Directory" ekle
3. macOS'taki `/Users/earth/Downloads/bsg` klasörünü seç
4. Ubuntu'da `/mnt` altında görünecek

### Seçenek C: SCP ile Kopyalama (macOS'tan)
```bash
# macOS terminal'inde
scp -r /Users/earth/Downloads/bsg ubuntu@<vm-ip>:/home/ubuntu/
```

---

## 🔧 Adım 2: Sistem Paketlerini Kurma

Ubuntu VM'de terminal açın ve şunları çalıştırın:

```bash
# Sistem güncellemesi
sudo apt-get update

# Gerekli paketler
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    can-utils \
    iproute2 \
    git

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

---

## 📦 Adım 3: Proje Bağımlılıklarını Kurma

```bash
# Proje dizinine git
cd ~/bsg  # veya projenin bulunduğu dizin

# Virtual environment oluştur
python3 -m venv venv

# Activate et
source venv/bin/activate

# Bağımlılıkları yükle
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ✅ Adım 4: CAN Bus'ı Test Etme

```bash
# Terminal 1: CAN trafiğini dinle
candump vcan0

# Terminal 2: Test mesajı gönder
cansend vcan0 200#1234ABCDEF

# Terminal 1'de mesajı görmelisiniz!
```

---

## 🚀 Adım 5: CLAC-SCO Senaryosunu Çalıştırma

```bash
# Virtual environment aktif olduğundan emin ol
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

### CAN modülleri yüklenemiyor
```bash
# Kernel modüllerini kontrol et
lsmod | grep can

# Manuel yükle
sudo modprobe can can_raw vcan
```

### vcan0 oluşturulamıyor
```bash
# Mevcut vcan0'i sil
sudo ip link delete vcan0

# Yeniden oluştur
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

### Port zaten kullanımda
- Test scripti otomatik olarak rastgele port seçer
- Eğer sorun devam ederse, test dosyasındaki port aralığını değiştirin

---

## 📝 Notlar

- **CAN Bus**: Gerçek CAN bus desteği için Linux kernel gerekli (macOS'ta yok)
- **VM**: UTM, VirtualBox, VMware hepsi çalışır
- **RAM**: En az 2GB RAM önerilir
- **Disk**: En az 5GB boş alan

---

**Hazırlayan**: Auto (Cursor AI)
**Tarih**: 2025-01-27

