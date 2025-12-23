#!/bin/bash
# Virtual CAN (vcan0) kurulum scripti

echo "========================================"
echo "Virtual CAN (vcan0) Kurulumu"
echo "========================================"

# vcan modülünü yükle
echo "[1/3] vcan kernel modülü yükleniyor..."
sudo modprobe vcan

if [ $? -eq 0 ]; then
    echo "✓ vcan modülü yüklendi"
else
    echo "✗ vcan modülü yüklenemedi!"
    exit 1
fi

# vcan0 interface oluştur
echo "[2/3] vcan0 interface oluşturuluyor..."
sudo ip link add dev vcan0 type vcan

# vcan0'ı aktif et
echo "[3/3] vcan0 aktif ediliyor..."
sudo ip link set up vcan0

if [ $? -eq 0 ]; then
    echo "✓ vcan0 başarıyla kuruldu"
else
    echo "✗ vcan0 aktif edilemedi!"
    exit 1
fi

# Doğrula
echo ""
echo "========================================"
echo "Kurulum Tamamlandı!"
echo "========================================"
ip link show vcan0

echo ""
echo "Test etmek için:"
echo "  cansend vcan0 123#DEADBEEF"
echo "  candump vcan0"

