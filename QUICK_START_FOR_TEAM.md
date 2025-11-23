# 🚀 Ekip Arkadaşları İçin Hızlı Başlangıç

Bu rehber, ekip arkadaşlarının projeyi hızlıca kurup senaryo eklemeye başlaması için hazırlanmıştır.

---

## 📥 1. Projeyi İndir ve Kur

```bash
# 1. Repository'yi clone et
git clone https://github.com/sennaates/elektrikli-arac-sarj-istasyon-guvenligi-g10.git
cd elektrikli-arac-sarj-istasyon-guvenligi-g10

# 2. güncelsimülasyonumuz branch'ine geç
git checkout güncelsimülasyonumuz

# 3. Virtual environment oluştur
python3 -m venv venv

# 4. Virtual environment'ı aktif et
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 5. Bağımlılıkları kur
pip install -r requirements.txt
```

---

## 🔧 2. Sistem Gereksinimleri

### Linux (Önerilen)

```bash
# vcan0 kurulumu
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# Kontrol et
ip link show vcan0
```

### Windows

Windows'ta `virtual` interface kullanılır (otomatik çalışır, kurulum gerekmez).

---

## 📋 3. Senaryo Ekleme Süreci

### Adım 1: Senaryo Numarasını Belirle

Hangi senaryoyu ekleyeceğini belirle:
- Senaryo #4, #5, #6, #7, #8, #9, veya #10

### Adım 2: Senaryo Dosyasını Oluştur

```bash
# Senaryo dosyası oluştur
touch tests/scenario_XX_[senaryo_adi].py
```

**Template:** `SCENARIO_ADDITION_GUIDE.md` dosyasındaki template'i kullan.

### Adım 3: IDS Kuralı Ekle

`utils/ids.py` dosyasını düzenle:
- Yeni alert tipi ekle
- Tespit metodu ekle

**Örnek:** Senaryo #2 ve #3'ü incele.

### Adım 4: Attack Simulator Ekle

`attack_simulator.py` dosyasını düzenle:
- Saldırı simülasyon fonksiyonu ekle
- CLI argümanları ekle

**Örnek:** `ocpp_message_flooding()` fonksiyonunu incele.

### Adım 5: Dokümantasyon Oluştur

```bash
# Kullanım kılavuzu
touch SCENARIO_XX_GUIDE.md

# README
touch README_SCENARIO_XX.md
```

**Template:** `SCENARIO_ADDITION_GUIDE.md` dosyasındaki template'leri kullan.

### Adım 6: Test Et

```bash
# Senaryo testi
python tests/scenario_XX_*.py

# Attack simulator testi
python attack_simulator.py --attack your_scenario --param value
```

### Adım 7: Git Commit ve Push

```bash
# Değişiklikleri ekle
git add tests/scenario_XX_*.py
git add SCENARIO_XX_GUIDE.md
git add README_SCENARIO_XX.md
git add utils/ids.py
git add attack_simulator.py

# Commit et
git commit -m "feat: Senaryo #XX eklendi - [Senaryo Adı]"

# Push et
git push origin güncelsimülasyonumuz
```

---

## 📚 4. Referans Senaryolar

### Senaryo #1: MitM OCPP Manipulation
- **Dosya:** `tests/scenario_01_mitm_ocpp_manipulation.py`
- **IDS:** `utils/ids.py` - `check_ocpp_message()` içinde K1, K2, K3
- **Attack:** `attack_simulator.py` - `mitm_ocpp_manipulation()`

### Senaryo #2: OCPP Message Flooding
- **Dosya:** `tests/scenario_02_ocpp_dos_flooding.py`
- **IDS:** `utils/ids.py` - Rate limiting
- **Attack:** `attack_simulator.py` - `ocpp_message_flooding()`
- **ML:** `utils/ml_ids.py` - `extract_ocpp_features()`

### Senaryo #3: Sampling Manipulation
- **Dosya:** `tests/scenario_03_sampling_manipulation.py`
- **IDS:** `utils/ids.py` - `check_meter_values()`
- **Attack:** `attack_simulator.py` - `sampling_manipulation()`
- **ML:** `utils/ml_ids.py` - `extract_sampling_features()`

---

## 🆘 5. Sorun Giderme

### Problem: vcan0 bulunamadı (Linux)

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

### Problem: Python modülü bulunamadı

```bash
# Virtual environment aktif mi kontrol et
which python  # venv/bin/python göstermeli

# Bağımlılıkları tekrar kur
pip install -r requirements.txt
```

### Problem: Git push hatası

```bash
# Önce pull yap
git pull origin güncelsimülasyonumuz

# Sonra push yap
git push origin güncelsimülasyonumuz
```

---

## 📖 6. Detaylı Dokümantasyon

Daha detaylı bilgi için:
- **`SCENARIO_ADDITION_GUIDE.md`** - Senaryo ekleme rehberi
- **`README.md`** - Ana proje dokümantasyonu
- **`SCENARIO_XX_GUIDE.md`** - Mevcut senaryo kılavuzları

---

## ✅ Kontrol Listesi

Senaryo eklemeden önce:

- [ ] Proje clone edildi ve kuruldu
- [ ] `güncelsimülasyonumuz` branch'ine geçildi
- [ ] Virtual environment aktif
- [ ] Bağımlılıklar kuruldu
- [ ] Senaryo dosyası oluşturuldu
- [ ] IDS kuralı eklendi
- [ ] Attack simulator eklendi
- [ ] Dokümantasyon oluşturuldu
- [ ] Test edildi
- [ ] Git commit ve push yapıldı

---

**İyi çalışmalar! 🚀**

