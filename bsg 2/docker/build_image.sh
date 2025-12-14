#!/bin/bash
# Docker image'ı build et (sadece bir kez)

cd "$(dirname "$0")/.."

echo "🔨 Docker image build ediliyor..."
echo "   (Bu sadece bir kez yapılır, sonra hızlı çalışır)"
echo ""

docker build -t bsg-test -f docker/Dockerfile .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Image başarıyla build edildi: bsg-test"
    echo "   Artık testleri hızlı çalıştırabilirsiniz!"
else
    echo "❌ Build başarısız!"
    exit 1
fi

