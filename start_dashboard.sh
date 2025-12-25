#!/bin/bash
# Dashboard ve API Server'ı başlatma script'i

set -e

# Renkler
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔐 Secure OCPP-CAN Bridge Dashboard Başlatılıyor...${NC}"
echo ""

# Proje dizinine git
cd "$(dirname "$0")"

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment bulunamadı!${NC}"
    echo "Önce virtual environment oluşturun:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Virtual environment'ı aktif et
source venv/bin/activate

# Port kontrolü
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port kullanımda
    else
        return 1  # Port boş
    fi
}

# API Server kontrolü
if check_port 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 zaten kullanımda (API Server çalışıyor olabilir)${NC}"
    echo "Mevcut API server'ı kontrol ediliyor..."
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API Server zaten çalışıyor${NC}"
        API_RUNNING=true
    else
        echo -e "${RED}❌ Port 8000 kullanımda ama API yanıt vermiyor${NC}"
        echo "Port'u kullanan process'i durdurun veya farklı bir port kullanın"
        exit 1
    fi
else
    echo -e "${GREEN}📡 API Server başlatılıyor...${NC}"
    API_RUNNING=false
fi

# Dashboard port kontrolü
if check_port 8501; then
    echo -e "${YELLOW}⚠️  Port 8501 zaten kullanımda${NC}"
    echo "Dashboard zaten çalışıyor olabilir: http://localhost:8501"
    read -p "Devam etmek istiyor musunuz? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# API Server'ı arka planda başlat
if [ "$API_RUNNING" = false ]; then
    echo -e "${GREEN}🚀 API Server başlatılıyor (arka planda)...${NC}"
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
            echo -e "${RED}❌ API Server başlatılamadı (30 saniye timeout)${NC}"
            kill $API_PID 2>/dev/null || true
            exit 1
        fi
        sleep 1
        echo -n "."
    done
    echo ""
fi

# Dashboard'u başlat
echo -e "${GREEN}📊 Dashboard başlatılıyor...${NC}"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Dashboard: http://localhost:8501${NC}"
echo -e "${GREEN}  API Server: http://localhost:8000${NC}"
echo -e "${GREEN}  API Docs: http://localhost:8000/docs${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}⚠️  Dashboard'u durdurmak için: Ctrl+C${NC}"
echo ""

# Dashboard'u başlat (foreground)
streamlit run dashboard.py --server.port 8501 --server.address localhost

# Cleanup: API Server'ı durdur (eğer biz başlattıysak)
if [ "$API_RUNNING" = false ] && [ ! -z "$API_PID" ]; then
    echo ""
    echo -e "${YELLOW}API Server durduruluyor...${NC}"
    kill $API_PID 2>/dev/null || true
fi

