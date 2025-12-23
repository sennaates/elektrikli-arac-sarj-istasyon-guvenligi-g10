#!/bin/bash

# Elektrikli Araç Şarj İstasyonu Güvenlik Sistemi - Durdurma Scripti

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}================================================================${NC}"
echo -e "${CYAN}🛑 Elektrikli Araç Şarj İstasyonu Güvenlik Sistemi${NC}"
echo -e "${CYAN}   Servisler Durduruluyor...${NC}"
echo -e "${PURPLE}================================================================${NC}"
echo ""

# Proje dizinine git
cd "$(dirname "$0")"

# PID dosyalarından process'leri durdur
if [ -d ".pids" ]; then
    for pidfile in .pids/*.pid; do
        if [ -f "$pidfile" ]; then
            service_name=$(basename "$pidfile" .pid)
            pid=$(cat "$pidfile")
            
            if ps -p "$pid" > /dev/null 2>&1; then
                echo -e "${YELLOW}🔄 $service_name durduruluyor (PID: $pid)...${NC}"
                kill -TERM "$pid" 2>/dev/null
                
                # Process'in durmasını bekle
                for i in {1..10}; do
                    if ! ps -p "$pid" > /dev/null 2>&1; then
                        echo -e "${GREEN}✅ $service_name durduruldu${NC}"
                        break
                    fi
                    sleep 1
                done
                
                # Hala çalışıyorsa zorla durdur
                if ps -p "$pid" > /dev/null 2>&1; then
                    echo -e "${RED}⚠️  $service_name zorla durduruluyor...${NC}"
                    kill -KILL "$pid" 2>/dev/null
                    echo -e "${GREEN}✅ $service_name zorla durduruldu${NC}"
                fi
            else
                echo -e "${YELLOW}⚠️  $service_name zaten durdurulmuş${NC}"
            fi
            
            rm -f "$pidfile"
        fi
    done
    
    rmdir .pids 2>/dev/null || true
else
    echo -e "${YELLOW}⚠️  PID dosyaları bulunamadı, port'lara göre durdurma deneniyor...${NC}"
fi

# Port'lara göre process'leri durdur
ports=(8000 8501 9000)
port_names=("API Server" "Dashboard" "CSMS")

for i in "${!ports[@]}"; do
    port=${ports[$i]}
    name=${port_names[$i]}
    
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}🔄 $name (Port $port) durduruluyor (PID: $pid)...${NC}"
        kill -TERM $pid 2>/dev/null
        sleep 2
        
        # Hala çalışıyorsa zorla durdur
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -KILL $pid 2>/dev/null
            echo -e "${GREEN}✅ $name zorla durduruldu${NC}"
        else
            echo -e "${GREEN}✅ $name durduruldu${NC}"
        fi
    fi
done

echo ""
echo -e "${GREEN}🎉 Tüm servisler durduruldu!${NC}"
echo ""

# Log dosyalarını temizleme seçeneği
if [ -d "logs" ] && [ "$(ls -A logs)" ]; then
    echo -e "${BLUE}📄 Log dosyaları mevcut:${NC}"
    ls -la logs/
    echo ""
    
    read -p "Log dosyalarını temizlemek istiyor musunuz? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f logs/*.log
        echo -e "${GREEN}✅ Log dosyaları temizlendi${NC}"
    else
        echo -e "${YELLOW}📄 Log dosyaları korundu${NC}"
    fi
fi

echo ""
echo -e "${CYAN}🚀 Sistemi tekrar başlatmak için: ./start.sh${NC}"
echo ""