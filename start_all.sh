#!/bin/bash
# Tüm servisleri başlatma script'i (API + Dashboard)

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd "$(dirname "$0")"

echo -e "${GREEN}🔐 Secure OCPP-CAN Bridge - Tüm Servisler Başlatılıyor...${NC}"
echo ""

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment bulunamadı!${NC}"
    exit 1
fi

source venv/bin/activate

# Logs dizini
mkdir -p logs

# API Server'ı arka planda başlat
echo -e "${GREEN}📡 API Server başlatılıyor...${NC}"
python api_server.py > logs/api_server.log 2>&1 &
API_PID=$!
echo "API Server PID: $API_PID"

# API Server'ın hazır olmasını bekle
echo "API Server'ın hazır olması bekleniyor..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API Server hazır!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ API Server başlatılamadı${NC}"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""

# Dashboard'u başlat
echo -e "${GREEN}📊 Dashboard başlatılıyor...${NC}"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Dashboard: http://localhost:8501${NC}"
echo -e "${GREEN}  ✅ API Server: http://localhost:8000${NC}"
echo -e "${GREEN}  ✅ API Docs: http://localhost:8000/docs${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}⚠️  Durdurmak için: Ctrl+C${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Servisler durduruluyor...${NC}"
    kill $API_PID 2>/dev/null || true
    pkill -f "streamlit" 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Dashboard'u başlat
streamlit run dashboard.py --server.port 8501 --server.address localhost

