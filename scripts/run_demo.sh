#!/bin/bash
# Demo senaryosunu çalıştır

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Virtual environment'ı aktif et
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  Virtual environment bulunamadı! 'venv/bin/activate' dosyasını kontrol edin."
fi

echo "🚀 OCPP-CAN Bridge Demo Başlatılıyor..."
echo ""

# Sanal CAN arayüzünü kur (eğer yoksa)
if ! ip link show vcan0 &>/dev/null; then
    echo "📡 Sanal CAN arayüzü kuruluyor..."
    sudo bash scripts/setup_vcan.sh
fi

# Sertifikaları oluştur (eğer yoksa)
if [ ! -f "certs/weak/server.crt" ] || [ ! -f "certs/strong/server.crt" ]; then
    echo "🔐 Sertifikalar oluşturuluyor..."
    bash scripts/generate_certs.sh
fi

# Senaryoyu seç
SCENARIO=${1:-plain_ws}

echo "📋 Senaryo: $SCENARIO"
echo ""

# Temizle (birden fazla başlatma önlemek için)
pkill -f "csms\|charge_point" || true
sleep 1

# Terminal'leri açar (eğer xterm veya gnome-terminal varsa)
if command -v xterm &> /dev/null; then
    # CSMS
    xterm -T "CSMS ($SCENARIO)" -e bash -c "
        cd $PROJECT_DIR;
        source venv/bin/activate;
        echo '🌐 CSMS Başlatılıyor: $SCENARIO';
        python -m src.ocpp.central_system.simulator --scenario $SCENARIO --port 9000;
        sleep 5
    " &
    
    sleep 2
    
    # CP
    xterm -T "Charge Point ($SCENARIO)" -e bash -c "
        cd $PROJECT_DIR;
        source venv/bin/activate;
        echo '🔌 CP Başlatılıyor: $SCENARIO';
        python -m src.ocpp.charge_point.simulator --scenario $SCENARIO --cp-id CP001;
        sleep 30
    " &
    
    # CAN trafiği
    xterm -T "CAN Traffic (vcan0)" -e bash -c "
        echo '📊 CAN trafiği izleniyor...';
        candump vcan0;
        sleep 30
    " &
    
    echo ""
    echo "✅ Demo başlatıldı! Terminal pencerelerini kontrol edin."
    echo "⚠️  Pencereleri kapatarak durdurabilirsiniz."
    
elif command -v gnome-terminal &> /dev/null; then
    # Gnome Terminal kullan
    gnome-terminal --tab --title="CSMS ($SCENARIO)" -- bash -c "
        cd $PROJECT_DIR;
        source venv/bin/activate;
        python -m src.ocpp.central_system.simulator --scenario $SCENARIO --port 9000; sleep 5
    " &
    
    sleep 2
    
    gnome-terminal --tab --title="Charge Point ($SCENARIO)" -- bash -c "
        cd $PROJECT_DIR;
        source venv/bin/activate;
        python -m src.ocpp.charge_point.simulator --scenario $SCENARIO --cp-id CP001; sleep 30
    " &
    
    gnome-terminal --tab --title="CAN Traffic" -- bash -c "
        candump vcan0; sleep 30
    " &
    
    echo "✅ Demo başlatıldı!"
    
else
    # Terminal yoksa arka planda çalıştır
    echo "⚠️  Terminal bulunamadı, arka planda çalıştırılıyor..."
    
    python -m src.ocpp.central_system.simulator --scenario $SCENARIO --port 9000 > csms.log 2>&1 &
    CSMS_PID=$!
    
    sleep 2
    
    python -m src.ocpp.charge_point.simulator --scenario $SCENARIO --cp-id CP001 > cp.log 2>&1 &
    CP_PID=$!
    
    echo ""
    echo "✅ Demo başlatıldı! (PID: CSMS=$CSMS_PID, CP=$CP_PID)"
    echo ""
    echo "📊 Logları izlemek için:"
    echo "   tail -f csms.log"
    echo "   tail -f cp.log"
    echo "   candump vcan0"
    echo ""
    echo "⏹️  Durdurmak için:"
    echo "   kill $CSMS_PID $CP_PID"
    
    echo $CSMS_PID > /tmp/bsg_csms.pid
    echo $CP_PID > /tmp/bsg_cp.pid
fi

