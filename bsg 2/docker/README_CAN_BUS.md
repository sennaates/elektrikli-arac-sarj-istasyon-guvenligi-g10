# CAN Bus Desteği - Önemli Notlar

## ⚠️ macOS Sınırlaması

**macOS'ta Docker container içinde CAN bus desteği sınırlıdır!**

### Neden?

1. **Kernel Modülleri**: macOS kernel'inde CAN bus modülleri yok
2. **Docker Limitation**: Container host kernel'ini kullanır, macOS'ta CAN modülleri yok
3. **Virtual CAN**: `vcan` modülü Linux kernel'ine özgü

### Çözümler

#### Seçenek 1: Linux VM (Önerilen)

```bash
# Linux VM içinde çalıştırın (Ubuntu, Debian, vb.)
# VM içinde:
sudo modprobe can can_raw vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
python3 tests/scenario_clac_sco.py
```

#### Seçenek 2: Linux Host

Gerçek bir Linux makinede çalıştırın:
- Ubuntu/Debian
- Fedora
- Herhangi bir Linux dağıtımı

#### Seçenek 3: Docker Desktop Linux Container (Deneme)

Docker Desktop'un Linux container desteği varsa deneyebilirsiniz, ama macOS'ta genellikle çalışmaz.

## 🔧 Linux'ta Çalıştırma

### Ubuntu/Debian

```bash
# CAN modüllerini yükle
sudo modprobe can can_raw vcan

# vcan0 oluştur
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# Kontrol et
ip link show vcan0

# Test çalıştır
python3 tests/scenario_clac_sco.py
```

### Docker ile (Linux Host'ta)

```bash
./docker/run_test.sh
```

## 📊 CAN Bus Testi

CAN bus'ın çalıştığını test etmek için:

```bash
# Terminal 1: CAN mesajlarını dinle
candump vcan0

# Terminal 2: CAN mesajı gönder
cansend vcan0 200#1234ABCDEF

# Terminal 1'de mesajı görmelisiniz
```

## 🎓 Akademik Kullanım İçin

Eğer hoca gerçek CAN bus istiyorsa:

1. **Linux VM kullanın** (VirtualBox, VMware, Parallels)
2. **Cloud Linux instance** (AWS EC2, DigitalOcean, vb.)
3. **Fiziksel Linux makine**

macOS'ta Docker ile gerçek CAN bus desteği **mümkün değil**.

## ✅ Mock Mode vs Real CAN Bus

| Özellik | Mock Mode | Real CAN Bus |
|---------|-----------|--------------|
| CAN mesajları | Simüle edilir | Gerçek CAN frame'ler |
| vcan0 | Gerekmez | Gerekli |
| Kernel modülleri | Gerekmez | Gerekli |
| macOS'ta çalışır | ✅ Evet | ❌ Hayır |
| Linux'ta çalışır | ✅ Evet | ✅ Evet |
| Test geçer | ✅ Evet | ✅ Evet |

**Not**: Mock mode'da da testler geçiyor ve senaryo çalışıyor, ama gerçek CAN bus trafiği yok.

---

**Öneri**: Hoca gerçek CAN bus istiyorsa, Linux VM kullanın veya Linux host'ta çalıştırın.

