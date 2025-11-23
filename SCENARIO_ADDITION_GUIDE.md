# 📋 Anomali Senaryosu Ekleme Rehberi

Bu rehber, ekip arkadaşlarının kalan anomali senaryolarını (4-10) projeye nasıl ekleyeceğini açıklar.

---

## 🎯 Genel Bakış

Projede şu anda **3 senaryo** entegre edilmiş durumda:
- ✅ **Senaryo #1:** MitM OCPP Manipulation
- ✅ **Senaryo #2:** OCPP Message Flooding (DoS)
- ✅ **Senaryo #3:** Adaptive Sampling Manipulation

**Kalan Senaryolar:** 4, 5, 6, 7, 8, 9, 10

---

## 📁 Senaryo Dosya Yapısı

Her senaryo için aşağıdaki dosyalar oluşturulmalı:

```
tests/
├── scenario_01_mitm_ocpp_manipulation.py      ✅ (Mevcut)
├── scenario_02_ocpp_dos_flooding.py            ✅ (Mevcut)
├── scenario_03_sampling_manipulation.py         ✅ (Mevcut)
├── scenario_04_[SENARYO_ADI].py                ⏳ (Eklenecek)
├── scenario_05_[SENARYO_ADI].py                ⏳ (Eklenecek)
├── ...
└── scenario_10_[SENARYO_ADI].py                ⏳ (Eklenecek)

SCENARIO_04_GUIDE.md                            ⏳ (Eklenecek)
SCENARIO_05_GUIDE.md                            ⏳ (Eklenecek)
...
SCENARIO_10_GUIDE.md                            ⏳ (Eklenecek)

README_SCENARIO_04.md                           ⏳ (Eklenecek)
README_SCENARIO_05.md                           ⏳ (Eklenecek)
...
README_SCENARIO_10.md                           ⏳ (Eklenecek)
```

---

## 🔧 Senaryo Ekleme Adımları

### 1️⃣ Senaryo Tanım Dosyası Oluştur

**Dosya:** `tests/scenario_XX_[senaryo_adi].py`

**Template:**

```python
"""
SENARYO #XX: [SENARYO ADI]

Tehdit Sınıflandırması:
- Saldırı Tipi: [Saldırı Tipi]
- Hedeflenen Varlık: [Hedef Varlık]
- Etkilenen Özellik: [Güvenlik Özelliği]
- Kategori: [Kategori]
"""

# SENARYO PARAMETRELERİ
SCENARIO_CONFIG = {
    "id": "SCENARIO-XX",
    "name": "[Senaryo Adı]",
    "severity": "CRITICAL|HIGH|MEDIUM|LOW",
    "category": "[Kategori]",
    
    # Normal Davranış
    "normal_behavior": {
        # Normal sistem davranışı parametreleri
    },
    
    # Anomali Davranış
    "anomaly_behavior": {
        # Anomali durumunda sistem davranışı
    },
    
    # Saldırı Parametreleri
    "attack": {
        "type": "[SALDIRI_TİPİ]",
        "target": "[HEDEF]",
        "method": "[YÖNTEM]",
    },
    
    # Tespit Kuralları
    "detection": {
        "rule_1": {
            "id": "[RULE_ID]",
            "name": "[Kural Adı]",
            "condition": "[Koşul]",
            "severity": "CRITICAL|HIGH|MEDIUM|LOW",
            "threshold": "[Eşik Değeri]"
        },
        # Daha fazla kural...
    },
    
    # Test Senaryoları
    "test_cases": [
        {
            "id": "TC-XX-001",
            "name": "[Test Adı]",
            "description": "[Açıklama]",
            "expected_alert": "[Alert Tipi]"
        }
    ],
    
    # Etkiler
    "impacts": {
        "functional": "[Fonksiyonel Etki]",
        "operational": "[Operasyonel Etki]",
        "financial": "[Finansal Etki]",
        "safety": "[Güvenlik Etkisi]"
    }
}

# Senaryo validasyonu
if __name__ == "__main__":
    print(f"Senaryo #XX: {SCENARIO_CONFIG['name']}")
    print(f"Severity: {SCENARIO_CONFIG['severity']}")
    # ...
```

**Örnek Referans:** `tests/scenario_01_mitm_ocpp_manipulation.py`

---

### 2️⃣ IDS Kuralları Ekle

**Dosya:** `utils/ids.py`

**Eklenmesi Gerekenler:**

1. **Yeni Alert Tipleri:**
```python
# utils/ids.py içinde AlertType enum'a ekle
class AlertType(Enum):
    # ... mevcut alert'ler
    YOUR_NEW_ALERT_TYPE = "YOUR_NEW_ALERT_TYPE"
```

2. **Yeni Tespit Metodu:**
```python
# RuleBasedIDS class'ına ekle
def check_your_scenario(self, ...) -> Optional[Alert]:
    """
    Senaryo #XX için tespit metodu
    """
    # Tespit mantığı
    if condition:
        return Alert(
            alert_type=AlertType.YOUR_NEW_ALERT_TYPE,
            severity=Severity.HIGH,
            description="...",
            timestamp=time.time()
        )
    return None
```

3. **TrafficStats Güncellemesi:**
```python
# Gerekirse TrafficStats class'ına yeni tracking değişkenleri ekle
self.your_scenario_tracking: deque = deque(maxlen=1000)
```

**Örnek Referans:** Senaryo #2 ve #3'ün IDS entegrasyonları

---

### 3️⃣ Attack Simulator Fonksiyonu Ekle

**Dosya:** `attack_simulator.py`

**Eklenmesi Gerekenler:**

```python
# AttackSimulator class'ına ekle
def your_scenario_attack(self, ...):
    """
    Senaryo #XX saldırı simülasyonu
    """
    logger.warning(f"🚨 SALDIRI: [Senaryo Adı] başlatılıyor...")
    # Saldırı simülasyonu
    # ...
    logger.warning(f"✓ [Senaryo Adı] tamamlandı")
```

**CLI Argümanları:**
```python
# main() fonksiyonunda argparse'a ekle
parser.add_argument(
    "--your-scenario-param",
    type=...,
    default=...,
    help="Senaryo #XX parametresi"
)

# main() içinde handler ekle
elif args.attack == "your_scenario":
    simulator.your_scenario_attack(...)
```

**Örnek Referans:** `attack_simulator.py` içindeki `ocpp_message_flooding()` ve `sampling_manipulation()` fonksiyonları

---

### 4️⃣ ML-IDS Features Ekle (Opsiyonel)

**Dosya:** `utils/ml_ids.py`

**Eklenmesi Gerekenler:**

```python
# FeatureExtractor class'ına ekle
def extract_your_scenario_features(self, ...) -> np.ndarray:
    """
    Senaryo #XX için feature extraction
    """
    features = []
    # Feature hesaplamaları
    return np.array(features)
```

**Örnek Referans:** Senaryo #2 ve #3'ün ML feature'ları

---

### 5️⃣ Kullanım Kılavuzu Oluştur

**Dosya:** `SCENARIO_XX_GUIDE.md`

**Template:**

```markdown
# 🔴 Senaryo #XX: [Senaryo Adı]

## 📋 Senaryo Özeti

**Saldırı Tipi:** [Tip]
**Hedef:** [Hedef]
**Severity:** [Severity]
**Tespit Yöntemi:** [Yöntem]

## 🎯 Saldırı Akışı

[Adım adım saldırı akışı]

## 🔬 Tespit Kuralları

### Kural 1: [Kural Adı]
[Kural açıklaması]

## 🧪 Test Senaryoları

### Test 1: [Test Adı]

```bash
python attack_simulator.py --attack your_scenario --param value
```

**Beklenen Sonuç:**
- ✅ IDS alert: [Alert Tipi]
- ✅ Severity: [Severity]
- ✅ Dashboard'da görünür

## 📊 Beklenen Sonuçlar

[Sonuçlar]

## 🛡️ Azaltma Stratejileri

1. [Strateji 1]
2. [Strateji 2]
```

**Örnek Referans:** `SCENARIO_01_GUIDE.md`, `SCENARIO_02_GUIDE.md`, `SCENARIO_03_GUIDE.md`

---

### 6️⃣ README Oluştur

**Dosya:** `README_SCENARIO_XX.md`

**Template:**

```markdown
# ✅ SENARYO #XX ENTEGRASYON ÖZETİ

## 📋 SENARYO DETAYLARI

**ID:** SCENARIO-XX
**İsim:** [Senaryo Adı]
**Kategori:** [Kategori]
**Severity:** [Severity]
**Durum:** ✅ ENTEGRE EDİLDİ

## 🎯 NE EKLENDİ?

### 1️⃣ IDS Kuralları
[Eklenen IDS kuralları]

### 2️⃣ Attack Simulator
[Eklenen attack simulator fonksiyonu]

### 3️⃣ ML-IDS Features (Opsiyonel)
[Eklenen ML features]

## 🧪 TEST SENARYOLARI

[Test senaryoları tablosu]

## 🚀 NASIL TEST EDİLİR?

[Test adımları]
```

**Örnek Referans:** `README_SCENARIO_01.md`, `README_SCENARIO_02.md`, `README_SCENARIO_03.md`

---

### 7️⃣ Ana README'yi Güncelle

**Dosya:** `README.md`

**Eklenmesi Gerekenler:**

1. Senaryo listesine ekle
2. Test komutlarına ekle
3. Dokümantasyon linklerine ekle

---

## 🔄 Git Workflow

### Branch'e Geçiş

```bash
# Remote repository'yi clone et (ilk kez)
git clone https://github.com/sennaates/elektrikli-arac-sarj-istasyon-guvenligi-g10.git
cd elektrikli-arac-sarj-istasyon-guvenligi-g10

# güncelsimülasyonumuz branch'ine geç
git checkout güncelsimülasyonumuz

# Veya yeni branch oluştur (eğer yoksa)
git checkout -b güncelsimülasyonumuz
```

### Senaryo Ekleme Süreci

```bash
# 1. Güncel kodu çek
git pull origin güncelsimülasyonumuz

# 2. Senaryo dosyalarını oluştur
# - tests/scenario_XX_*.py
# - SCENARIO_XX_GUIDE.md
# - README_SCENARIO_XX.md

# 3. Kod değişikliklerini yap
# - utils/ids.py
# - attack_simulator.py
# - utils/ml_ids.py (opsiyonel)

# 4. Değişiklikleri stage et
git add tests/scenario_XX_*.py
git add SCENARIO_XX_GUIDE.md
git add README_SCENARIO_XX.md
git add utils/ids.py
git add attack_simulator.py

# 5. Commit et
git commit -m "feat: Senaryo #XX eklendi - [Senaryo Adı]"

# 6. Push et
git push origin güncelsimülasyonumuz
```

---

## ✅ Kontrol Listesi

Senaryo eklemeden önce:

- [ ] Senaryo tanım dosyası oluşturuldu (`tests/scenario_XX_*.py`)
- [ ] IDS kuralları eklendi (`utils/ids.py`)
- [ ] Attack simulator fonksiyonu eklendi (`attack_simulator.py`)
- [ ] ML-IDS features eklendi (opsiyonel, `utils/ml_ids.py`)
- [ ] Kullanım kılavuzu oluşturuldu (`SCENARIO_XX_GUIDE.md`)
- [ ] README oluşturuldu (`README_SCENARIO_XX.md`)
- [ ] Ana README güncellendi (`README.md`)
- [ ] Test edildi ve çalıştığı doğrulandı
- [ ] Git commit ve push yapıldı

---

## 📚 Örnek Senaryo Referansları

### Senaryo #1: MitM OCPP Manipulation
- **Dosya:** `tests/scenario_01_mitm_ocpp_manipulation.py`
- **IDS:** `utils/ids.py` - `check_ocpp_message()` içinde K1, K2, K3 kuralları
- **Attack:** `attack_simulator.py` - `mitm_ocpp_manipulation()`
- **Guide:** `SCENARIO_01_GUIDE.md`

### Senaryo #2: OCPP Message Flooding
- **Dosya:** `tests/scenario_02_ocpp_dos_flooding.py`
- **IDS:** `utils/ids.py` - `check_ocpp_message()` içinde rate limiting
- **Attack:** `attack_simulator.py` - `ocpp_message_flooding()`
- **ML:** `utils/ml_ids.py` - `extract_ocpp_features()`
- **Guide:** `SCENARIO_02_GUIDE.md`

### Senaryo #3: Sampling Manipulation
- **Dosya:** `tests/scenario_03_sampling_manipulation.py`
- **IDS:** `utils/ids.py` - `check_meter_values()` metodu
- **Attack:** `attack_simulator.py` - `sampling_manipulation()`
- **ML:** `utils/ml_ids.py` - `extract_sampling_features()`
- **Guide:** `SCENARIO_03_GUIDE.md`

---

## 🆘 Yardım ve Destek

### Sorun Giderme

**Problem:** IDS alert'i oluşmuyor
- ✅ `check_*` metodunun doğru çağrıldığından emin ol
- ✅ Alert tipinin `AlertType` enum'ında tanımlı olduğundan emin ol
- ✅ Threshold değerlerinin doğru olduğundan emin ol

**Problem:** Attack simulator çalışmıyor
- ✅ CLI argümanlarının doğru tanımlandığından emin ol
- ✅ Fonksiyonun `AttackSimulator` class'ı içinde olduğundan emin ol
- ✅ Gerekli bağımlılıkların kurulu olduğundan emin ol

**Problem:** Git push hatası
- ✅ Branch'in doğru olduğundan emin ol (`güncelsimülasyonumuz`)
- ✅ Remote repository'nin doğru olduğundan emin ol
- ✅ Güncel kodu çektiğinden emin ol (`git pull`)

### İletişim

Sorularınız için:
- GitHub Issues kullanın
- Ekip içi iletişim kanallarını kullanın

---

## 📝 Notlar

- Her senaryo, mevcut 3 senaryo ile aynı yapıda olmalı
- Kod standartlarına uygun olmalı (PEP 8)
- Dokümantasyon eksiksiz olmalı
- Test edilmiş ve çalışır durumda olmalı
- Git commit mesajları açıklayıcı olmalı

---

**Son Güncelleme:** 2025-11-23
**Versiyon:** 1.0

