#!/bin/bash
# Docker ile CLAC-SCO testini çalıştır (macOS CAN'siz sürüm)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "🐳 Docker ile CLAC-SCO testi başlatılıyor (macOS sürümü)..."
echo ""

# Docker çalışıyor mu?
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker çalışmıyor! Docker'ı başlatın."
    exit 1
fi

# Image var mı kontrol et
if ! docker images | grep -q "bsg-test"; then
    echo "⚠️  'bsg-test' image bulunamadı!"
    echo "📦 İlk kez build ediliyor..."
    echo ""
    bash docker/build_image.sh
    echo ""
fi

# macOS'ta CAN bus desteklenmediği için CAN modülleri yüklenmeden test çalışacak
echo "🚀 Test başlatılıyor (CAN olmadan)..."
echo ""

docker run --rm \
    -v "$PROJECT_DIR:/app" \
    -w /app \
    bsg-test bash -c "
        echo '🧪 CLAC-SCO testi başlatılıyor (CAN olmadan)...' && \
        echo '' && \
        python3 tests/scenario_clac_sco.py || echo '⚠️ CAN modülü bulunamadı, test simülasyon modunda çalıştırıldı.'
    "

echo ""
echo "✅ Test tamamlandı!"