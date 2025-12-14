# 📊 Dashboard Kullanım Rehberi

## 🎯 Dashboard'a Erişim

Dashboard başlatıldıktan sonra: **http://localhost:8501**

## 🎭 Demo Verileri

Dashboard'da veri görmek için:

### Yöntem 1: Otomatik (Dashboard içinden)
1. Dashboard'ı açın
2. "🎭 Demo Verileri Oluştur" butonuna tıklayın
3. Sayfa otomatik yenilenecek

### Yöntem 2: Manuel (Terminal'den)
```bash
# Demo verileri oluştur
python3 demo_data.py

# Veya script ile
./refresh_demo_data.sh
```

## 📋 Dashboard Bölümleri

### 1. 🔝 Ana Metrikler
- **📦 Toplam Blok:** Blockchain'deki blok sayısı
- **🚨 Toplam Alert:** Güvenlik uyarıları
- **📡 CAN Frame:** CAN-Bus mesaj sayısı
- **🤖 ML-IDS:** Makine öğrenmesi durumu

### 2. 🚨 Real-Time Alerts
- **Severity Dağılımı:** CRITICAL, HIGH, MEDIUM, LOW
- **Son Alert'ler:** Zaman sıralı güvenlik uyarıları
- **Alert Tipleri:**
  - `UNAUTHORIZED_CAN_FRAME` - Yetkisiz CAN mesajı
  - `OCPP_FLOODING` - OCPP mesaj bombardımanı
  - `TIMING_ANOMALY` - Zamanlama anomalisi
  - `BLOCKCHAIN_VALIDATION_FAILED` - Blockchain doğrulama hatası
  - `ML_ANOMALY_DETECTED` - ML anomali tespiti

### 3. ⛓️ Blockchain Durumu
- **Doğrulama Durumu:** Blockchain geçerliliği
- **Genesis Hash:** İlk blok hash'i
- **En Son Hash:** Son blok hash'i
- **Dijital İmza:** İmza durumu
- **Blok Tipi Dağılımı:** Pie chart

### 4. 📊 Trafik Analizi
- **CAN ID Frekansı:** CAN mesaj dağılımı
- **OCPP Action Frekansı:** OCPP komut dağılımı

### 5. 🤖 Makine Öğrenmesi
- **Model Durumu:** Eğitilmiş/Eğitilmemiş
- **Eğitim Verisi:** Örnek sayısı
- **Anomali Oranı:** Tespit oranı
- **🎓 Modeli Eğit:** Manuel eğitim butonu

### 6. 🔋 BSG Proje Çıktıları
- **Şarj İstasyonu Metrikleri:**
  - Bağlı şarj istasyonu sayısı
  - Toplam transaction sayısı
  - Aktif transaction'lar
  - Tamamlanan transaction'lar

- **Şarj İstasyonu Listesi:** Bağlı cihazlar
- **Transaction Geçmişi:** İşlem kayıtları
- **Grafikler:**
  - Transaction durumu (Pie chart)
  - Charge Point dağılımı (Bar chart)

## ⚙️ Kontrol Paneli (Sidebar)

### Otomatik Yenileme
- **🔄 Otomatik Yenileme:** Açık/Kapalı
- **⏱️ Yenileme Süresi:** 1-10 saniye arası

### Filtreler
- **🚨 Alert'ler:** Alert bölümünü göster/gizle
- **⛓️ Blockchain:** Blockchain bölümünü göster/gizle
- **📡 Trafik:** Trafik analizi göster/gizle
- **🤖 ML-IDS:** ML bölümünü göster/gizle
- **🔋 BSG Proje Çıktıları:** BSG bölümünü göster/gizle

### Sistem Durumu
- **✅ Sistem Aktif:** API bağlantısı OK
- **❌ Sistem Erişilemez:** API bağlantı sorunu

## 🎨 Görsel Özellikler

### Renkler
- **🔴 CRITICAL:** Kırmızı (Kritik)
- **🟠 HIGH:** Turuncu (Yüksek)
- **🟡 MEDIUM:** Sarı (Orta)
- **🟢 LOW:** Yeşil (Düşük)

### Animasyonlar
- **Hover Efektleri:** Kartlar üzerine gelince büyür
- **Gradient Arka Plan:** Modern glassmorphism
- **Smooth Transitions:** Yumuşak geçişler

## 🔧 Sorun Giderme

### Veri Görünmüyor
1. API Server çalışıyor mu? → `curl http://localhost:8000/api/health`
2. Demo verileri oluşturuldu mu? → `python3 demo_data.py`
3. Dashboard yenilendi mi? → F5 veya otomatik yenileme

### Yavaş Yüklenme
1. Yenileme süresini artırın (5-10 saniye)
2. Gereksiz bölümleri kapatın (filtreler)
3. Tarayıcı cache'ini temizleyin

### API Bağlantı Hatası
1. API Server'ı yeniden başlatın: `./start.sh`
2. Port'u kontrol edin: `lsof -i :8000`
3. Log'ları kontrol edin: `tail -f logs/api_server.log`

## 📱 Mobil Uyumluluk

Dashboard mobil cihazlarda da çalışır:
- **Responsive Design:** Ekran boyutuna uyum
- **Touch Friendly:** Dokunma dostu arayüz
- **Optimized Charts:** Mobil için optimize grafikler

## 🚀 Performans İpuçları

1. **Otomatik yenileme süresini optimize edin** (3-5 saniye ideal)
2. **Gereksiz bölümleri kapatın** (filtreler ile)
3. **Tarayıcı cache'ini düzenli temizleyin**
4. **Stable internet bağlantısı kullanın**

---

**🎉 Dashboard'ınızı keşfetmeye başlayın!**