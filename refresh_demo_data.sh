#!/bin/bash

# Demo verilerini yenile ve dashboard'ı güncelle

echo "🎭 Demo Verileri Yenileniyor..."
echo "=============================="

cd "$(dirname "$0")"

# venv'i aktifleştir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Demo verilerini oluştur
python3 demo_data.py

echo ""
echo "✨ Demo verileri yenilendi!"
echo "📊 Dashboard otomatik olarak güncellenecek: http://localhost:8501"