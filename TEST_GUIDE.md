# 🛡️ Güvenlik Testi ve Anomali Tespiti Kullanım Kılavuzu

Bu doküman, Elektrikli Araç Şarj İstasyonları (EVSE) için geliştirdiğimiz **Saldırı Tespit Sistemini (IDS)** ve **Saldırı Simülatörünü** nasıl çalıştıracağınızı anlatır.

Sistem iki ana parçadan oluşur:
1. **Dedektif (`simple_test.py`):** Ağı dinler, ML modeli ve kuralları kullanarak saldırıları yakalar.
2. **Saldırgan (`attack_simulator.py`):** Ağa sahte saldırı verileri gönderir.

---

## 🚀 Kurulum

Projeyi indirdikten sonra gerekli kütüphaneleri yükleyin:

```bash
pip install -r requirements.txt
```

---

## 🧪 Test Nasıl Yapılır?

Testi gerçekleştirmek için **iki ayrı terminal** penceresi açmanız gerekmektedir.

### Adım 1: Modeli Eğitme (Sadece İlk Seferde)
Eğer `models/isolation_forest.pkl` dosyası yoksa veya modeli sıfırlamak istiyorsanız önce eğitimi çalıştırın:

```bash
python training/train_ml_model.py
```
*✅ Çıktı: "Model başarıyla eğitildi ve kaydedildi" mesajını görmelisiniz.*

### Adım 2: Dedektifi Başlatma (Terminal 1)
Bu terminal **savunma** tarafıdır. Sürekli açık kalmalı ve ağı dinlemelidir.

```bash
python simple_test.py
```
*📡 Çıktı: "Hat dinleniyor..." mesajını göreceksiniz. Saldırı gelene kadar bekleyecektir.*

### Adım 3: Saldırı Yapma (Terminal 2)
Bu terminal **saldırı** tarafıdır. Buradan komut gönderdiğinizde, diğer terminalde (Dedektif) alarmların çaldığını görmelisiniz.

#### 🌟 Tüm Senaryoları Sırayla Test Et (Önerilen)
En kapsamlı test budur. Tüm saldırıları sırayla yapar:
```bash
python attack_simulator.py --attack all
```

#### 🎯 Özel Senaryoları Test Et
Sadece belirli bir senaryoyu denemek isterseniz:

**1. Ransomware (Fidye Yazılımı) Saldırısı (Senaryo #5)**
Sahte firmware güncellemesi ve şifreleme aktivitesi simüle eder.
```bash
python attack_simulator.py --attack ransomware
```

**2. Sensor Data Poisoning (Veri Zehirleme) (Senaryo #7)**
Sensör verilerini yavaşça manipüle ederek yapay zekayı yanıltmaya çalışır.
```bash
python attack_simulator.py --attack poisoning
```

**3. Latency Exploit (Gecikme Zafiyeti) (Senaryo #4)**
Sistemin kör noktalarından faydalanarak voltaj manipülasyonu yapar.
```bash
python attack_simulator.py --attack latency
```

---

## 📊 Beklenen Sonuçlar (Dedektif Terminali)

Saldırı başladığında `simple_test.py` çalışan terminalde şunları görmelisiniz:

* **🚨 [YAPAY ZEKA] ANOMALİ TESPİT ETTİ!**
  * ML modeli, normal trafikten sapan verileri (örn. Poisoning, Latency) yakaladığında çıkar.
  
* **⚠️ [KURAL] İHLAL TESPİT ETTİ**
  * Bilinen imzalar (örn. Ransomware ID'si 0x777) yakalandığında çıkar.

* **CRITICAL ALERT [RANSOMWARE]**
  * Fidye yazılımı tespit edildiğinde çıkan özel kritik alarm.

---

## 🛠 Sorun Giderme

* **Hata:** `ModuleNotFoundError: No module named ...`
  * **Çözüm:** `pip install -r requirements.txt` komutunu çalıştırın.
  
* **Hata:** `Model bulunamadı`
  * **Çözüm:** `python training/train_ml_model.py` komutunu çalıştırın.

* **Not:** Mac kullanıcıları için sistem otomatik olarak UDP modunda, Linux kullanıcıları için vcan0 modunda çalışır. Ekstra ayar yapmanıza gerek yoktur.
