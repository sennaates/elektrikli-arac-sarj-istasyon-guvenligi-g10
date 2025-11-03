#!/bin/bash
# Sanal CAN arayüzü kurulum scripti

set -e

echo "🔧 CAN arayüzü kuruluyor..."

# Load CAN kernel modules
sudo modprobe can
sudo modprobe can_raw
sudo modprobe vcan

# Remove existing vcan0 if exists
sudo ip link delete vcan0 2>/dev/null || true

# Create virtual CAN interface
sudo ip link add dev vcan0 type vcan

# Bring interface up
sudo ip link set up vcan0

# Verify
if ip link show vcan0 | grep -q "UP"; then
    echo "✅ vcan0 başarıyla kuruldu"
    ip link show vcan0
else
    echo "❌ vcan0 kurulumu başarısız"
    exit 1
fi

echo ""
echo "📊 CAN trafiğini izlemek için:"
echo "   candump vcan0"
echo ""
echo "🔧 CAN arayüzünü kaldırmak için:"
echo "   sudo ip link delete vcan0"

