#!/bin/bash
# Linux'ta CAN bus kurulum scripti

set -e

echo "🔧 CAN Bus Kurulumu (Linux)"
echo ""

# Root kontrolü
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Bu script root olarak çalıştırılmalı (sudo)"
    exit 1
fi

# CAN modüllerini yükle
echo "📦 CAN kernel modülleri yükleniyor..."
modprobe can || (echo "❌ 'can' modülü yüklenemedi" && exit 1)
modprobe can_raw || (echo "❌ 'can_raw' modülü yüklenemedi" && exit 1)
modprobe vcan || (echo "❌ 'vcan' modülü yüklenemedi" && exit 1)

echo "✅ CAN modülleri yüklendi"
echo ""

# vcan0 oluştur
echo "📡 vcan0 interface'i oluşturuluyor..."

# Eğer varsa sil
ip link delete vcan0 2>/dev/null || true

# Yeni oluştur
ip link add dev vcan0 type vcan || (echo "❌ vcan0 oluşturulamadı" && exit 1)

# Aktif et
ip link set up vcan0 || (echo "❌ vcan0 aktif edilemedi" && exit 1)

echo "✅ vcan0 oluşturuldu ve aktif"
echo ""

# Kontrol et
echo "📊 vcan0 durumu:"
ip link show vcan0

echo ""
echo "✅ CAN bus hazır!"
echo ""
echo "Test etmek için:"
echo "  Terminal 1: candump vcan0"
echo "  Terminal 2: cansend vcan0 200#1234ABCDEF"
echo ""

