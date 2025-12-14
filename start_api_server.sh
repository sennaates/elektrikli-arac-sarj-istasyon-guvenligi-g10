#!/bin/bash

echo "🚀 API Server Başlatılıyor"
echo "=========================="

# Proje dizinine git
cd "$(dirname "$0")"

# Mevcut venv'i kullan
if [ -d "venv" ]; then
    echo "📦 venv aktifleştiriliyor..."
    source venv/bin/activate
    
    echo "📦 API kütüphaneleri kontrol ediliyor..."
    
    # API için gerekli kütüphaneleri yükle
    pip install fastapi uvicorn pydantic loguru python-dotenv --quiet 2>/dev/null || echo "Kütüphaneler zaten yüklü"
    
    echo ""
    echo "🚀 API Server başlatılıyor..."
    echo "   🌐 API URL: http://localhost:8000"
    echo "   📖 Docs: http://localhost:8000/docs"
    echo "   🛑 Durdurmak için: Ctrl+C"
    echo ""
    
    # API server'ı başlat
    python3 api_server.py
else
    echo "❌ venv bulunamadı. Önce virtual environment oluşturun:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install fastapi uvicorn pydantic loguru python-dotenv"
fi