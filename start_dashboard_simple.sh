#!/bin/bash

echo "🔐 Elektrikli Araç Şarj İstasyonu Güvenlik Sistemi Dashboard"
echo "=========================================================="

# Proje dizinine git
cd "$(dirname "$0")"

echo "📦 Dashboard kütüphaneleri yükleniyor..."

# Sadece dashboard için gerekli kütüphaneleri yükle
pip3 install --user --break-system-packages streamlit plotly pandas requests python-dotenv numpy

echo ""
echo "🚀 Dashboard başlatılıyor..."
echo "   📊 Dashboard URL: http://localhost:8501"
echo "   🛑 Durdurmak için: Ctrl+C"
echo ""

# Dashboard'ı başlat
python3 -m streamlit run dashboard.py