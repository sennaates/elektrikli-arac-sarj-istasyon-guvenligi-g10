#!/bin/bash
# Docker ile CLAC-SCO testini çalıştır (build edilmiş image kullanır)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "🐳 Docker ile CLAC-SCO testi başlatılıyor..."
echo ""

# Docker'ın çalıştığını kontrol et
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker çalışmıyor! Docker'ı başlatın."
    exit 1
fi

# Image var mı kontrol et
if ! docker images | grep -q "bsg-test"; then
    echo "⚠️  'bsg-test' image bulunamadı!"
    echo "📦 İlk kez build ediliyor (bu biraz zaman alabilir)..."
    echo ""
    bash docker/build_image.sh
    echo ""
fi

# Build edilmiş image ile testi çalıştır
echo "🚀 Test çalıştırılıyor (CAN bus ile)..."
echo "⚠️  NOT: macOS'ta CAN bus desteği sınırlı olabilir"
echo ""

docker run --rm \
    --network host \
    --privileged \
    --cap-add=NET_ADMIN \
    --cap-add=SYS_MODULE \
    --cap-add=SYS_ADMIN \
    -v /lib/modules:/lib/modules:ro \
    -v "$PROJECT_DIR:/app" \
    -w /app \
    bsg-test bash -c "
        echo '🔧 CAN modülleri yükleniyor...' && \
        if modprobe can 2>&1 && modprobe can_raw 2>&1 && modprobe vcan 2>&1; then \
            echo '✅ CAN modülleri yüklendi'; \
        else \
            echo '❌ CAN modülleri yüklenemedi!'; \
            echo '⚠️  macOS Sınırlaması: Docker container içinde CAN modülleri yüklenemez'; \
            echo '📖 Çözüm: Linux VM veya Linux host kullanın'; \
            echo '📖 Detaylar: docker/README_CAN_BUS.md'; \
            exit 1; \
        fi && \
        echo '' && \
        echo '📡 vcan0 oluşturuluyor...' && \
        (ip link delete vcan0 2>/dev/null || true) && \
        ip link add dev vcan0 type vcan && \
        ip link set up vcan0 && \
        ip link show vcan0 && \
        echo '✅ vcan0 hazır ve aktif!' && \
        echo '' && \
        echo '🧪 Test başlatılıyor (CAN bus ile)...' && \
        echo '' && \
        python3 tests/scenario_clac_sco.py
    "

echo ""
echo "✅ Test tamamlandı!"

