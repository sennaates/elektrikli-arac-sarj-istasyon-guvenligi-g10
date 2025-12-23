# 🚀 Hızlı Başlangıç Rehberi

## 📋 Tek Komutla Başlatma

```bash
# Projeyi tamamen başlat (API + Dashboard)
./start.sh

# CSMS simülatörü ile birlikte başlat
./start.sh --with-csms

# Sadece Dashboard başlat
./start.sh --no-api

# Kütüphane kurulumunu atla (zaten yüklüyse)
./start.sh --no-install
```

## 🛑 Durdurma

```bash
# Tüm servisleri durdur
./stop.sh
```

## 🌐 Erişim URL'leri

| Servis | URL | Açıklama |
|--------|-----|----------|
| **Dashboard** | http://localhost:8501 | Ana arayüz |
| **API Server** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **CSMS** | ws://localhost:9000 | WebSocket (opsiyonel) |

## 📊 Özellikler

### Dashboard Bölümleri:
- 🚨 **Real-Time Alerts** - Güvenlik uyarıları
- ⛓️ **Blockchain Durumu** - Blockchain istatistikleri  
- 📊 **Trafik Analizi** - CAN ve OCPP trafiği
- 🤖 **ML-IDS** - Makine öğrenmesi durumu
- 🔋 **BSG Proje Çıktıları** - Şarj istasyonu verileri

### API Endpoints:
- `/api/health` - Sistem durumu
- `/api/stats` - Genel istatistikler
- `/api/alerts` - Güvenlik uyarıları
- `/api/bsg/transactions` - Transaction listesi
- `/api/bsg/chargepoints` - Şarj istasyonları
- `/api/blockchain/stats` - Blockchain verileri

## 🔧 Sorun Giderme

### Port Zaten Kullanımda
```bash
# Çalışan process'leri kontrol et
lsof -i :8000  # API Server
lsof -i :8501  # Dashboard
lsof -i :9000  # CSMS

# Script otomatik olarak sorar ve durdurur
./start.sh
```

### Kütüphane Hataları
```bash
# Manuel kütüphane yükleme
source venv/bin/activate
pip install -r requirements.txt

# Veya minimal yükleme
pip install streamlit plotly pandas requests python-dotenv fastapi uvicorn
```

### Python Versiyonu
- **Minimum:** Python 3.8
- **Önerilen:** Python 3.11
- **Desteklenen:** Python 3.8 - 3.12

## 📄 Log Dosyaları

```bash
# Logları takip et
tail -f logs/api_server.log    # API Server
tail -f logs/dashboard.log     # Dashboard  
tail -f logs/csms.log          # CSMS

# Tüm logları göster
ls -la logs/
```

## ⚙️ Konfigürasyon

`.env` dosyasını düzenleyerek portları değiştirebilirsiniz:

```env
# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Dashboard  
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8501

# CSMS
CSMS_HOST=0.0.0.0
CSMS_PORT=9000
```

## 🎯 Kullanım Senaryoları

### 1. Geliştirme Modu
```bash
# Sadece Dashboard
./start.sh --no-api

# API + Dashboard
./start.sh
```

### 2. Demo Modu
```bash
# Tüm servisler
./start.sh --with-csms
```

### 3. Production Modu
```bash
# Kütüphaneler zaten yüklü
./start.sh --no-install
```

## 🔄 Güncellemeler

```bash
# Servisleri durdur
./stop.sh

# Kodu güncelle (git pull vb.)
git pull

# Yeniden başlat
./start.sh
```

## 📱 Mobil Erişim

Dashboard mobil uyumludur:
- **Yerel Ağ:** http://[IP_ADRESINIZ]:8501
- **IP Bulma:** `ifconfig | grep inet`

## 🎉 İlk Kullanım

1. **Başlat:** `./start.sh`
2. **Aç:** http://localhost:8501
3. **Keşfet:** Dashboard bölümlerini incele
4. **Test Et:** API endpoints'leri dene
5. **İzle:** Real-time verileri gözlemle

---

**🔐 Elektrikli Araç Şarj İstasyonu Güvenlik Sistemi**  
*Blockchain-Secured OCPP-to-CAN Bridge*