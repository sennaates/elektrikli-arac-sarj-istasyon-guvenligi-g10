#!/bin/bash
# Basit başlatma script'i - Hata mesajlarını gösterir

cd "$(dirname "$0")"

echo "🔐 Secure OCPP-CAN Bridge Başlatılıyor..."
echo ""

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment bulunamadı!"
    echo "Önce: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Virtual environment'ı aktif et
source venv/bin/activate

# Logs dizini
mkdir -p logs

echo "📡 Terminal 1: API Server başlatılıyor..."
echo "   Komut: python api_server.py"
echo "   URL: http://localhost:8000"
echo ""
echo "📊 Terminal 2: Dashboard başlatılacak..."
echo "   Komut: streamlit run dashboard.py"
echo "   URL: http://localhost:8501"
echo ""
echo "════════════════════════════════════════════════════════"
echo ""
echo "İki terminal açın:"
echo ""
echo "TERMINAL 1 (API Server):"
echo "  cd $(pwd)"
echo "  source venv/bin/activate"
echo "  python api_server.py"
echo ""
echo "TERMINAL 2 (Dashboard):"
echo "  cd $(pwd)"
echo "  source venv/bin/activate"
echo "  streamlit run dashboard.py"
echo ""
echo "════════════════════════════════════════════════════════"
echo ""
read -p "API Server'ı bu terminalde başlatmak ister misiniz? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 API Server başlatılıyor..."
    echo "   Log: logs/api_server.log"
    echo ""
    python api_server.py 2>&1 | tee logs/api_server.log
else
    echo "Manuel başlatma için yukarıdaki komutları kullanın."
fi

