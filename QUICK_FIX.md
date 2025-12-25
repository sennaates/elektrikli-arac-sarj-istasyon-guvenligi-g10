# 🚀 Dashboard Hızlı Çözüm

## Sorun: Dashboard açılmıyor

### ✅ Çözüm 1: İki Terminal Açın

**Terminal 1 - API Server:**
```bash
cd /home/semih/elektrikli-arac-sarj-istasyon-guvenligi-g10
source venv/bin/activate
python api_server.py
```

Beklenen çıktı:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Dashboard:**
```bash
cd /home/semih/elektrikli-arac-sarj-istasyon-guvenligi-g10
source venv/bin/activate
streamlit run dashboard.py
```

Beklenen çıktı:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### ✅ Çözüm 2: Tek Komutla Test

```bash
cd /home/semih/elektrikli-arac-sarj-istasyon-guvenligi-g10
source venv/bin/activate
python test_api.py
```

Bu komut API server'ı başlatır ve hataları gösterir.

### ✅ Çözüm 3: Basit Script

```bash
./start_simple.sh
```

## 🔍 Hata Kontrolü

### API Server başlamıyorsa:

1. **Import hatası:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Port kullanımda:**
   ```bash
   lsof -i :8000
   kill -9 <PID>
   ```

3. **Python hatası:**
   ```bash
   python --version  # 3.9+ olmalı
   which python     # venv/bin/python olmalı
   ```

### Dashboard başlamıyorsa:

1. **Streamlit yüklü değil:**
   ```bash
   pip install streamlit
   ```

2. **Port kullanımda:**
   ```bash
   lsof -i :8501
   kill -9 <PID>
   ```

3. **API bağlantı hatası:**
   - Önce API server'ın çalıştığını kontrol edin:
   ```bash
   curl http://localhost:8000/api/health
   ```

## 📝 Adım Adım Kontrol

```bash
# 1. Dizin kontrolü
cd /home/semih/elektrikli-arac-sarj-istasyon-guvenligi-g10
pwd

# 2. Virtual environment
source venv/bin/activate
which python

# 3. Bağımlılıklar
python -c "import fastapi, streamlit, uvicorn; print('OK')"

# 4. API Server test
python test_api.py

# 5. Dashboard test
streamlit run dashboard.py --server.headless true
```

## 🆘 Hala Çalışmıyorsa

1. **Log dosyalarını kontrol edin:**
   ```bash
   cat logs/api_server.log
   ```

2. **Hata mesajını paylaşın:**
   - Terminal çıktısı
   - Browser console (F12)
   - Log dosyaları

3. **Manuel test:**
   ```bash
   # API test
   python -c "from api_server import app; print('API OK')"
   
   # Dashboard test
   python -c "import streamlit; print('Streamlit OK')"
   ```

## ✅ Başarı Kriterleri

- ✅ API Server: http://localhost:8000/api/health → `{"status": "healthy"}`
- ✅ Dashboard: http://localhost:8501 → Sayfa açılıyor
- ✅ Sidebar'da "✅ Sistem Aktif" görünüyor

