#!/bin/bash

echo "🔐 Elektrikli Araç Şarj İstasyonu Güvenlik Sistemi Dashboard"
echo "=========================================================="

# Proje dizinine git
cd "$(dirname "$0")"

# Mevcut venv'i kullan
if [ -d "venv" ]; then
    echo "📦 Mevcut venv aktifleştiriliyor..."
    source venv/bin/activate
    
    echo "📦 Sadece gerekli kütüphaneleri yükleniyor..."
    
    # Sadece dashboard için gerekli olanları yükle
    pip install streamlit==1.28.0 --no-deps --quiet 2>/dev/null || echo "Streamlit zaten yüklü"
    pip install plotly==5.15.0 --no-deps --quiet 2>/dev/null || echo "Plotly zaten yüklü" 
    pip install pandas==2.0.0 --no-deps --quiet 2>/dev/null || echo "Pandas zaten yüklü"
    pip install requests --quiet 2>/dev/null || echo "Requests zaten yüklü"
    pip install python-dotenv --quiet 2>/dev/null || echo "Python-dotenv zaten yüklü"
    
    echo ""
    echo "🚀 Dashboard başlatılıyor..."
    echo "   📊 Dashboard URL: http://localhost:8501"
    echo "   🛑 Durdurmak için: Ctrl+C"
    echo ""
    
    # Dashboard'ı başlat
    streamlit run dashboard.py
else
    echo "❌ venv bulunamadı. Önce virtual environment oluşturun:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install streamlit plotly pandas requests python-dotenv"
fi