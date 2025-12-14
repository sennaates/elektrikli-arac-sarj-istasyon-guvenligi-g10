#!/bin/bash

# Elektrikli Araç Şarj İstasyonu Güvenlik Sistemi - Tam Başlatma Scripti
# Bu script projeyi tamamen ayaklandırır: API Server + Dashboard + CSMS (opsiyonel)

set -e  # Hata durumunda dur

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${PURPLE}================================================================${NC}"
echo -e "${CYAN}🔐 Elektrikli Araç Şarj İstasyonu Güvenlik Sistemi${NC}"
echo -e "${CYAN}   Blockchain-Secured OCPP-to-CAN Bridge${NC}"
echo -e "${PURPLE}================================================================${NC}"
echo ""

# Proje dizinine git
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)

echo -e "${BLUE}📂 Proje Dizini: ${PROJECT_DIR}${NC}"
echo ""

# Parametreler
START_API=true
START_DASHBOARD=true
START_CSMS=false
INSTALL_DEPS=true

# Komut satırı parametrelerini kontrol et
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-api)
            START_API=false
            shift
            ;;
        --no-dashboard)
            START_DASHBOARD=false
            shift
            ;;
        --with-csms)
            START_CSMS=true
            shift
            ;;
        --no-install)
            INSTALL_DEPS=false
            shift
            ;;
        --help|-h)
            echo "Kullanım: ./start.sh [SEÇENEKLER]"
            echo ""
            echo "Seçenekler:"
            echo "  --no-api        API Server'ı başlatma"
            echo "  --no-dashboard  Dashboard'ı başlatma"
            echo "  --with-csms     CSMS simülatörünü de başlat"
            echo "  --no-install    Kütüphane kurulumunu atla"
            echo "  --help, -h      Bu yardım mesajını göster"
            echo ""
            echo "Örnekler:"
            echo "  ./start.sh                    # API + Dashboard başlat"
            echo "  ./start.sh --with-csms       # API + Dashboard + CSMS başlat"
            echo "  ./start.sh --no-api          # Sadece Dashboard başlat"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Bilinmeyen parametre: $1${NC}"
            echo "Yardım için: ./start.sh --help"
            exit 1
            ;;
    esac
done

# Fonksiyonlar
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $1 mevcut${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 bulunamadı${NC}"
        return 1
    fi
}

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $1 zaten kullanımda${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Port $1 müsait${NC}"
        return 0
    fi
}

kill_process_on_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}🔄 Port $port'taki process (PID: $pid) sonlandırılıyor...${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Sistem kontrolleri
echo -e "${BLUE}🔍 Sistem Kontrolleri${NC}"
echo "==================="

# Python kontrolü
if ! check_command python3; then
    echo -e "${RED}❌ Python 3 gerekli. Lütfen Python 3'ü yükleyin.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo -e "${GREEN}🐍 Python versiyonu: $PYTHON_VERSION${NC}"

# pip kontrolü
if ! check_command pip3; then
    echo -e "${RED}❌ pip3 gerekli. Lütfen pip'i yükleyin.${NC}"
    exit 1
fi

echo ""

# Virtual Environment Kontrolü ve Kurulumu
echo -e "${BLUE}📦 Virtual Environment Kontrolü${NC}"
echo "================================"

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Virtual environment bulunamadı, oluşturuluyor...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment oluşturuldu${NC}"
else
    echo -e "${GREEN}✅ Virtual environment mevcut${NC}"
fi

# venv'i aktifleştir
echo -e "${BLUE}🔄 Virtual environment aktifleştiriliyor...${NC}"
source venv/bin/activate

echo -e "${GREEN}✅ Virtual environment aktif${NC}"
echo ""

# Kütüphane kurulumu
if [ "$INSTALL_DEPS" = true ]; then
    echo -e "${BLUE}📚 Kütüphane Kurulumu${NC}"
    echo "===================="
    
    echo -e "${YELLOW}📦 pip güncelleniyor...${NC}"
    pip install --upgrade pip --quiet
    
    echo -e "${YELLOW}📦 Temel kütüphaneler yükleniyor...${NC}"
    
    # Temel kütüphaneler
    pip install --quiet \
        requests \
        python-dotenv \
        pandas \
        numpy
    
    if [ "$START_API" = true ]; then
        echo -e "${YELLOW}📦 API Server kütüphaneleri yükleniyor...${NC}"
        pip install --quiet \
            fastapi \
            uvicorn \
            pydantic \
            loguru
    fi
    
    if [ "$START_DASHBOARD" = true ]; then
        echo -e "${YELLOW}📦 Dashboard kütüphaneleri yükleniyor...${NC}"
        pip install --quiet \
            streamlit \
            plotly
    fi
    
    if [ "$START_CSMS" = true ]; then
        echo -e "${YELLOW}📦 CSMS kütüphaneleri yükleniyor...${NC}"
        pip install --quiet \
            websockets \
            ocpp
    fi
    
    echo -e "${GREEN}✅ Kütüphaneler yüklendi${NC}"
    echo ""
fi

# Port kontrolleri
echo -e "${BLUE}🔌 Port Kontrolleri${NC}"
echo "=================="

if [ "$START_API" = true ]; then
    if ! check_port 8000; then
        read -p "Port 8000'deki process'i sonlandırmak istiyor musunuz? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill_process_on_port 8000
        else
            echo -e "${RED}❌ API Server başlatılamaz (Port 8000 meşgul)${NC}"
            START_API=false
        fi
    fi
fi

if [ "$START_DASHBOARD" = true ]; then
    if ! check_port 8501; then
        read -p "Port 8501'deki process'i sonlandırmak istiyor musunuz? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill_process_on_port 8501
        else
            echo -e "${RED}❌ Dashboard başlatılamaz (Port 8501 meşgul)${NC}"
            START_DASHBOARD=false
        fi
    fi
fi

if [ "$START_CSMS" = true ]; then
    if ! check_port 9000; then
        read -p "Port 9000'deki process'i sonlandırmak istiyor musunuz? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill_process_on_port 9000
        else
            echo -e "${RED}❌ CSMS başlatılamaz (Port 9000 meşgul)${NC}"
            START_CSMS=false
        fi
    fi
fi

echo ""

# .env dosyası kontrolü
echo -e "${BLUE}⚙️  Konfigürasyon Kontrolü${NC}"
echo "========================="

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}📄 .env dosyası bulunamadı, .env.example'dan oluşturuluyor...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✅ .env dosyası oluşturuldu${NC}"
    else
        echo -e "${YELLOW}📄 .env dosyası oluşturuluyor...${NC}"
        cat > .env << EOF
# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Dashboard Configuration
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8501

# CSMS Configuration
CSMS_HOST=0.0.0.0
CSMS_PORT=9000
EOF
        echo -e "${GREEN}✅ .env dosyası oluşturuldu${NC}"
    fi
else
    echo -e "${GREEN}✅ .env dosyası mevcut${NC}"
fi

echo ""

# Servisleri başlat
echo -e "${BLUE}🚀 Servisler Başlatılıyor${NC}"
echo "========================"

# PID dosyaları için dizin oluştur
mkdir -p .pids

# API Server başlat
if [ "$START_API" = true ]; then
    echo -e "${CYAN}🌐 API Server başlatılıyor...${NC}"
    nohup python3 api_server.py > logs/api_server.log 2>&1 &
    API_PID=$!
    echo $API_PID > .pids/api_server.pid
    
    # API'nin başlamasını bekle
    echo -e "${YELLOW}⏳ API Server'ın başlaması bekleniyor...${NC}"
    for i in {1..10}; do
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ API Server başlatıldı (PID: $API_PID)${NC}"
            echo -e "${GREEN}   📍 URL: http://localhost:8000${NC}"
            echo -e "${GREEN}   📖 Docs: http://localhost:8000/docs${NC}"
            break
        fi
        sleep 2
        echo -n "."
    done
    echo ""
fi

# Dashboard başlat
if [ "$START_DASHBOARD" = true ]; then
    echo -e "${CYAN}📊 Dashboard başlatılıyor...${NC}"
    nohup streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0 > logs/dashboard.log 2>&1 &
    DASHBOARD_PID=$!
    echo $DASHBOARD_PID > .pids/dashboard.pid
    
    # Dashboard'ın başlamasını bekle
    echo -e "${YELLOW}⏳ Dashboard'ın başlaması bekleniyor...${NC}"
    for i in {1..15}; do
        if curl -s http://localhost:8501 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Dashboard başlatıldı (PID: $DASHBOARD_PID)${NC}"
            echo -e "${GREEN}   📍 URL: http://localhost:8501${NC}"
            break
        fi
        sleep 2
        echo -n "."
    done
    echo ""
fi

# CSMS başlat (opsiyonel)
if [ "$START_CSMS" = true ]; then
    echo -e "${CYAN}⚡ CSMS Simülatörü başlatılıyor...${NC}"
    nohup python3 csms_simulator.py --port 9000 > logs/csms.log 2>&1 &
    CSMS_PID=$!
    echo $CSMS_PID > .pids/csms.pid
    
    echo -e "${GREEN}✅ CSMS başlatıldı (PID: $CSMS_PID)${NC}"
    echo -e "${GREEN}   📍 URL: ws://localhost:9000${NC}"
    echo ""
fi

# Log dizini oluştur
mkdir -p logs

# Başarı mesajı
echo -e "${PURPLE}================================================================${NC}"
echo -e "${GREEN}🎉 Sistem Başarıyla Başlatıldı!${NC}"
echo -e "${PURPLE}================================================================${NC}"
echo ""

echo -e "${CYAN}📋 Çalışan Servisler:${NC}"
if [ "$START_API" = true ]; then
    echo -e "${GREEN}   🌐 API Server:    http://localhost:8000${NC}"
    echo -e "${GREEN}   📖 API Docs:      http://localhost:8000/docs${NC}"
fi
if [ "$START_DASHBOARD" = true ]; then
    echo -e "${GREEN}   📊 Dashboard:     http://localhost:8501${NC}"
fi
if [ "$START_CSMS" = true ]; then
    echo -e "${GREEN}   ⚡ CSMS:          ws://localhost:9000${NC}"
fi

echo ""
echo -e "${CYAN}📂 Log Dosyaları:${NC}"
if [ "$START_API" = true ]; then
    echo -e "${YELLOW}   📄 API Server:    logs/api_server.log${NC}"
fi
if [ "$START_DASHBOARD" = true ]; then
    echo -e "${YELLOW}   📄 Dashboard:     logs/dashboard.log${NC}"
fi
if [ "$START_CSMS" = true ]; then
    echo -e "${YELLOW}   📄 CSMS:          logs/csms.log${NC}"
fi

echo ""
echo -e "${CYAN}🛑 Durdurmak için:${NC}"
echo -e "${YELLOW}   ./stop.sh         # Tüm servisleri durdur${NC}"
echo -e "${YELLOW}   Ctrl+C            # Bu terminali kapat (servisler çalışmaya devam eder)${NC}"

echo ""
echo -e "${BLUE}📊 Sistem Durumunu İzlemek için:${NC}"
echo -e "${YELLOW}   tail -f logs/api_server.log    # API Server logları${NC}"
echo -e "${YELLOW}   tail -f logs/dashboard.log     # Dashboard logları${NC}"
if [ "$START_CSMS" = true ]; then
    echo -e "${YELLOW}   tail -f logs/csms.log          # CSMS logları${NC}"
fi

echo ""
echo -e "${GREEN}✨ Sistem hazır! Tarayıcınızda http://localhost:8501 adresini açın.${NC}"
echo ""

# Kullanıcı müdahalesi için bekle
echo -e "${BLUE}Servisleri arka planda çalıştırmak için Enter'a basın, durdurmak için Ctrl+C...${NC}"
read -r

echo -e "${GREEN}🚀 Servisler arka planda çalışıyor. İyi kullanımlar!${NC}"