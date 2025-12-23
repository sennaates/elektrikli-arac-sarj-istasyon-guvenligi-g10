#!/bin/bash
# Hızlı başlangıç scripti - Tüm servisleri başlatır

echo "========================================"
echo "Secure OCPP-CAN Bridge"
echo "Quick Start Script"
echo "========================================"

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Python virtual environment kontrol
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment bulunamadı. Oluşturuluyor...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# vcan0 kontrol
if ! ip link show vcan0 &> /dev/null; then
    echo -e "${YELLOW}vcan0 bulunamadı. Kuruluyor...${NC}"
    bash setup_vcan.sh
fi

# .env kontrol
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}.env dosyası bulunamadı. .env.example'dan kopyalanıyor...${NC}"
    cp .env.example .env
fi

# Logs dizini
mkdir -p logs

# Models dizini
mkdir -p models

echo ""
echo -e "${GREEN}✓ Hazırlık tamamlandı${NC}"
echo ""
echo "Başlatılacak servisler:"
echo "  1. Secure Bridge (secure_bridge.py)"
echo "  2. API Server (api_server.py)"
echo "  3. Dashboard (dashboard.py)"
echo ""
echo "Not: CSMS sunucusu ayrıca başlatılmalı (veya simüle edilmeli)"
echo ""

read -p "Devam edilsin mi? (y/n) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "İptal edildi."
    exit 0
fi

echo ""
echo "========================================"
echo "Servisler Başlatılıyor..."
echo "========================================"

# Terminal multiplexer kontrol (tmux veya screen)
if command -v tmux &> /dev/null; then
    echo "tmux kullanılarak başlatılıyor..."
    
    # Yeni tmux session
    tmux new-session -d -s ocpp_bridge
    
    # Window 1: Secure Bridge
    tmux rename-window -t ocpp_bridge:0 'Bridge'
    tmux send-keys -t ocpp_bridge:0 'source venv/bin/activate && python secure_bridge.py' C-m
    
    # Window 2: API Server
    tmux new-window -t ocpp_bridge:1 -n 'API'
    tmux send-keys -t ocpp_bridge:1 'source venv/bin/activate && python api_server.py' C-m
    
    # Window 3: Dashboard
    tmux new-window -t ocpp_bridge:2 -n 'Dashboard'
    tmux send-keys -t ocpp_bridge:2 'source venv/bin/activate && streamlit run dashboard.py' C-m
    
    echo -e "${GREEN}✓ Servisler tmux'ta başlatıldı${NC}"
    echo ""
    echo "Terminallere erişmek için:"
    echo "  tmux attach -t ocpp_bridge"
    echo ""
    echo "Window'lar arası geçiş:"
    echo "  Ctrl+B, sonra 0/1/2"
    echo ""
    echo "tmux'tan çıkmak için:"
    echo "  Ctrl+B, sonra D (detach)"
    echo ""
    echo "Tüm servisleri durdurmak için:"
    echo "  tmux kill-session -t ocpp_bridge"
    echo ""
    echo -e "${GREEN}Dashboard: http://localhost:8501${NC}"
    echo -e "${GREEN}API: http://localhost:8000${NC}"
    
else
    echo -e "${YELLOW}tmux bulunamadı. Manuel başlatma gerekiyor.${NC}"
    echo ""
    echo "Terminal 1: python secure_bridge.py"
    echo "Terminal 2: python api_server.py"
    echo "Terminal 3: streamlit run dashboard.py"
fi

