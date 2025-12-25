# Dashboard Sorun Giderme Kılavuzu

## ❌ Dashboard Açılmıyor - Çözümler

### 1. API Server Çalışmıyor

**Sorun**: Dashboard açılıyor ama "API'ye bağlanılamıyor" hatası veriyor.

**Çözüm**:

```bash
# Terminal 1: API Server'ı başlat
cd /home/semih/elektrikli-arac-sarj-istasyon-guvenligi-g10
source venv/bin/activate
python api_server.py
```

API Server'ın çalıştığını kontrol edin:
```bash
curl http://localhost:8000/api/health
```

Beklenen yanıt:
```json
{"status": "healthy"}
```

### 2. Port 8000 Kullanımda

**Sorun**: "Address already in use" hatası.

**Çözüm**:

```bash
# Port'u kullanan process'i bul
lsof -i :8000

# Process'i durdur
kill -9 <PID>
```

Veya farklı bir port kullanın:
```bash
export API_PORT=8001
python api_server.py
```

Dashboard'da API URL'yi güncelleyin:
```python
# dashboard.py içinde
API_URL = "http://127.0.0.1:8001"
```

### 3. Port 8501 Kullanımda

**Sorun**: Streamlit "Port 8501 is already in use" hatası.

**Çözüm**:

```bash
# Port'u kullanan process'i bul
lsof -i :8501

# Process'i durdur
kill -9 <PID>
```

Veya farklı bir port kullanın:
```bash
streamlit run dashboard.py --server.port 8502
```

### 4. Virtual Environment Aktif Değil

**Sorun**: "ModuleNotFoundError" veya import hataları.

**Çözüm**:

```bash
# Virtual environment'ı aktif et
source venv/bin/activate

# Bağımlılıkları kontrol et
pip install -r requirements.txt
```

### 5. Bağımlılıklar Eksik

**Sorun**: Modül bulunamıyor hataları.

**Çözüm**:

```bash
# Tüm bağımlılıkları yükle
pip install -r requirements.txt

# Özellikle şunları kontrol et:
pip install streamlit
pip install fastapi
pip install uvicorn
pip install requests
pip install plotly
pip install pandas
```

### 6. API Server Başlamıyor

**Sorun**: API server başlatılamıyor veya hata veriyor.

**Kontrol Listesi**:

```bash
# 1. Python versiyonu kontrol et (3.9+ gerekli)
python3 --version

# 2. Virtual environment aktif mi?
which python  # venv/bin/python göstermeli

# 3. API server'ı manuel başlat ve hataları gör
python api_server.py

# 4. Log dosyasını kontrol et
tail -f logs/api_server.log
```

### 7. Dashboard Boş Görünüyor

**Sorun**: Dashboard açılıyor ama veri yok.

**Çözüm**:

1. **Bridge çalışıyor mu?**
   ```bash
   python secure_bridge.py
   ```

2. **API'den veri geliyor mu?**
   ```bash
   curl http://localhost:8000/api/stats
   ```

3. **Bridge state API'ye enjekte edilmiş mi?**
   Bridge çalışırken API server'a state enjekte edilir. Bridge'i başlatın.

### 8. CORS Hatası

**Sorun**: Browser console'da CORS hatası.

**Çözüm**: API server'da CORS zaten aktif. Eğer hala sorun varsa:

```python
# api_server.py içinde zaten var:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 9. Hızlı Başlatma Script'i

**En Kolay Yol**:

```bash
# Otomatik başlatma script'ini kullan
./start_dashboard.sh
```

Bu script:
- ✅ Virtual environment'ı kontrol eder
- ✅ Port'ları kontrol eder
- ✅ API Server'ı otomatik başlatır
- ✅ Dashboard'u başlatır

### 10. Manuel Başlatma (Adım Adım)

**Terminal 1: API Server**
```bash
cd /home/semih/elektrikli-arac-sarj-istasyon-guvenligi-g10
source venv/bin/activate
python api_server.py
```

**Terminal 2: Dashboard**
```bash
cd /home/semih/elektrikli-arac-sarj-istasyon-guvenligi-g10
source venv/bin/activate
streamlit run dashboard.py
```

**Terminal 3: Bridge (Opsiyonel - veri için)**
```bash
cd /home/semih/elektrikli-arac-sarj-istasyon-guvenligi-g10
source venv/bin/activate
python secure_bridge.py
```

## 🔍 Debug Komutları

### API Server Durumu
```bash
# Health check
curl http://localhost:8000/api/health

# Stats
curl http://localhost:8000/api/stats

# Alerts
curl http://localhost:8000/api/alerts

# Blockchain
curl http://localhost:8000/api/blockchain/stats
```

### Port Kontrolü
```bash
# Tüm portları kontrol et
lsof -i :8000  # API
lsof -i :8501  # Dashboard
lsof -i :9000  # CSMS
```

### Process Kontrolü
```bash
# Python process'lerini gör
ps aux | grep python

# Belirli bir process'i durdur
kill -9 <PID>
```

## 📝 Log Dosyaları

```bash
# API Server logları
tail -f logs/api_server.log

# Bridge logları
tail -f logs/bridge.log
```

## ✅ Başarı Kontrolü

Dashboard başarıyla çalışıyorsa:

1. ✅ Browser'da `http://localhost:8501` açılmalı
2. ✅ Sidebar'da "✅ Sistem Aktif" görünmeli
3. ✅ KPI kartlarında sayılar görünmeli (0 olsa bile)
4. ✅ Alert bölümü görünmeli
5. ✅ Blockchain bölümü görünmeli

## 🆘 Hala Çalışmıyorsa

1. **Tüm process'leri durdurun:**
   ```bash
   pkill -f "api_server.py"
   pkill -f "dashboard.py"
   pkill -f "streamlit"
   ```

2. **Port'ları temizleyin:**
   ```bash
   lsof -ti:8000 | xargs kill -9
   lsof -ti:8501 | xargs kill -9
   ```

3. **Yeniden başlatın:**
   ```bash
   ./start_dashboard.sh
   ```

4. **Hata mesajlarını kontrol edin:**
   - Browser console (F12)
   - Terminal output
   - Log dosyaları

## 📞 Yardım

Sorun devam ederse:
- Log dosyalarını kontrol edin
- Browser console'daki hataları kontrol edin
- API server'ın çalıştığını doğrulayın (`curl http://localhost:8000/api/health`)

