#!/bin/bash

echo "🔐 Elektrikli Araç Şarj İstasyonu Güvenlik Sistemi Dashboard"
echo "=========================================================="

# Proje dizinine git
cd "$(dirname "$0")"

echo "📦 Kütüphaneleri kontrol ediliyor..."

# Gerekli kütüphaneleri yükle
pip3 install -r requirements.txt

echo ""
echo "🚀 Dashboard başlatılıyor..."
echo "   📊 Dashboard URL: http://localhost:8501"
echo "   🛑 Durdurmak için: Ctrl+C"
echo ""

# Dashboard'ı başlat
streamlit run dashboard.py