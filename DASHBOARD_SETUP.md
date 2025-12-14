# 🚀 Dashboard Kurulum Rehberi

## Sorun: Python 3.13 Uyumluluk Sorunu

Python 3.13 çok yeni olduğu için bazı kütüphaneler (özellikle pydantic-core) henüz tam uyumlu değil.

## ✅ Çözüm Adımları

### Yöntem 1: Mevcut venv Kullanma (Önerilen)

```bash
# 1. Proje dizinine git
cd "/Users/enes/Desktop/Projects/elektrikli-arac-sarj-istasyon-guvenligi-g10"

# 2. Mevcut venv'i aktifleştir
source venv/bin/activate

# 3. Pip'i güncelle
pip install --upgrade pip

# 4. Dashboard kütüphanelerini yükle
pip install streamlit==1.28.0 plotly==5.15.0 pandas==2.0.0 requests python-dotenv

# 5. Dashboard'ı başlat
streamlit run dashboard.py
```

### Yöntem 2: Conda Kullanma (Alternatif)

```bash
# 1. Conda environment oluştur
conda create -n dashboard python=3.11

# 2. Environment'ı aktifleştir
conda activate dashboard

# 3. Kütüphaneleri yükle
conda install streamlit plotly pandas requests python-dotenv

# 4. Dashboard'ı başlat
streamlit run dashboard.py
```

### Yöntem 3: Docker Kullanma (Gelişmiş)

```bash
# Dockerfile oluştur ve çalıştır
docker build -t dashboard .
docker run -p 8501:8501 dashboard
```

## 🎯 Hızlı Test

Dashboard çalışıyor mu test et:

```bash
python3 -c "import streamlit; print('✅ Streamlit:', streamlit.__version__)"
python3 -c "import plotly; print('✅ Plotly:', plotly.__version__)"
python3 -c "import pandas; print('✅ Pandas:', pandas.__version__)"
```

## 🌐 Erişim

Dashboard başladığında:
- **URL:** http://localhost:8501
- **Otomatik açılır:** Tarayıcı otomatik açılacak

## 🆘 Sorun Giderme

### "streamlit: command not found"
```bash
# venv'i aktifleştirdiğinizden emin olun
source venv/bin/activate
which streamlit  # Streamlit'in yolunu kontrol et
```

### "pydantic-core build failed"
```bash
# Daha eski Python sürümü kullanın (3.11)
# veya pre-compiled wheel'ler kullanın
pip install --only-binary=all streamlit plotly pandas
```

### SSL Certificate Error
```bash
# Güvenilir host ekle
pip install --trusted-host pypi.org --trusted-host pypi.python.org streamlit
```

## 📋 Minimal Requirements

Sadece dashboard için:
```
streamlit>=1.28.0
plotly>=5.15.0  
pandas>=2.0.0
requests>=2.28.0
python-dotenv>=1.0.0
```

## 🎉 Başarı!

Dashboard çalıştığında şunları göreceksiniz:
- 🔐 Elektrikli Araç Şarj İstasyonu Güvenlik Sistemi
- 🚨 Real-Time Alerts
- ⛓️ Blockchain Durumu  
- 📊 Trafik Analizi
- 🤖 ML-IDS
- 🔋 BSG Proje Çıktıları