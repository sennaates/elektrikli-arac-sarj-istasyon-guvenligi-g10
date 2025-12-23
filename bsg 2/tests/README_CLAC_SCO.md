# CLAC-SCO Senaryosu Dokümantasyonu

## 📋 Senaryo Özeti

**CLAC-SCO**: Coordinated Load Alteration via Compromised Smart Charging Orchestrator

Bu senaryo, ele geçirilen bir akıllı şarj orkestratörünün vasıtasıyla çok sayıda şarj noktasına eşzamanlı olarak şarj profili değişikliği enjekte ederek dağıtım/iletim şebekesinde ani yük değişimleri oluşturmasını simüle eder.

## 🎯 Senaryo Özellikleri

- **Çoklu Charge Point Simülasyonu**: 5 adet Charge Point eşzamanlı bağlanır
- **Koordineli Saldırı**: Tüm CP'lere aynı anda SetChargingProfile komutu gönderilir
- **Anomali Tespiti**: CAN IDS ile burst pattern ve temporal correlation tespiti
- **Tespit Göstergeleri**: 
  - Temporal correlation (zaman korelasyonu)
  - Burst pattern (ani mesaj patlaması)
  - Anormal profil değişiklikleri

## 🚀 Senaryoyu Çalıştırma

### Yöntem 1: pytest ile

```bash
# Virtual environment'ı aktif et
source venv/bin/activate

# Senaryoyu çalıştır
pytest tests/scenario_clac_sco.py::test_clac_sco_coordinated_attack -v -s

# Tespit göstergeleri testini çalıştır
pytest tests/scenario_clac_sco.py::test_clac_sco_detection_indicators -v -s

# Tüm CLAC-SCO testlerini çalıştır
pytest tests/scenario_clac_sco.py -v -s
```

### Yöntem 2: Python ile direkt

```bash
cd /Users/earth/Downloads/bsg
source venv/bin/activate
python tests/scenario_clac_sco.py
```

## 📊 Beklenen Çıktı

```
================================================================================
CLAC-SCO: COORDINATED LOAD ALTERATION ATTACK
================================================================================
🔌 5 Charge Point başlatılıyor...
✅ 5 Charge Point bağlandı
📊 Normal akış başlatılıyor (baseline)...
📋 Bağlı CP ID'leri: ['cp_clac_001', 'cp_clac_002', ...]
✅ Baseline oluşturuldu
🚨 SALDIRI BAŞLATILIYOR: CLAC-SCO Coordinated Attack
   → Ele geçirilen orkestratör tüm CP'lere eşzamanlı komut gönderiyor...
⚠️  5/5 CP'ye saldırı komutu gönderildi
🔍 Anomali tespiti yapılıyor...
📊 Tespit İstatistikleri:
   - Toplam CAN mesajı: 5
   - Profil değişikliği sayısı: 5
   - IDS anomali sayısı: 0
✅ CLAC-SCO saldırı senaryosu başarıyla tamamlandı!
   → Koordineli yük değişikliği tespit edildi
   → Temporal correlation gözlemlendi
```

## 🔍 Tespit Mekanizmaları

### 1. Temporal Correlation
- Aynı zamanda 3+ CP'de profil değişikliği
- Zaman penceresi içinde koordineli değişiklikler

### 2. Burst Pattern
- Kısa sürede çok sayıda CAN mesajı
- Normal trafikten sapma

### 3. Anormal Profil Değişiklikleri
- Şüpheli profil ID (999)
- Anormal yüksek akım değerleri (50A)

## ⚙️ Senaryo Parametreleri

Test dosyasında değiştirilebilir parametreler:

```python
NUM_CHARGE_POINTS = 5  # Simüle edilecek CP sayısı
ATTACK_MAX_CURRENT = 50  # Saldırı akım değeri (A)
ATTACK_PROFILE_ID = 999  # Şüpheli profil ID
```

## 🐛 Sorun Giderme

### "Port already in use" hatası

```bash
# Eski process'leri temizle
pkill -f "csms\|charge_point"
sleep 2
```

### "CP bağlantısı kurulamadı" hatası

```bash
# CSMS'in başladığından emin olun
# Port 9030'un kullanılabilir olduğunu kontrol edin
netstat -an | grep 9030
```

### "CAN bus error" hatası

```bash
# vcan0 arayüzünü kontrol edin
ip link show vcan0

# Yoksa oluşturun
sudo bash scripts/setup_vcan.sh
```

## 📚 Referanslar

- Acharya et al., 'MaDEVIoT: Cyberattacks on EV Charging Can Disrupt Power Grids', arXiv 2023
- Ghafouri et al., 'Coordinated Charging and Discharging of Electric Vehicles', ACM 2022
- Jahangir et al., 'Charge manipulation attacks against smart electric vehicle charging systems', WRAP 2024

## 👤 Hazırlayan

**Şeref (Osama)** - 2025-01-27

---

**Not**: Bu senaryo yalnızca izole laboratuvar ortamında test edilmelidir.

