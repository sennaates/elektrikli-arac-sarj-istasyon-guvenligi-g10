#!/bin/bash
# Test TLS sertifikaları oluşturma scripti

set -e

CERT_DIR="certs"
WEAK_DIR="$CERT_DIR/weak"
STRONG_DIR="$CERT_DIR/strong"

echo "🔐 Test sertifikaları oluşturuluyor..."

# Create directories
mkdir -p "$WEAK_DIR" "$STRONG_DIR"

# Generate ZAYIF sertifikalar (kısa süreli, düşük anahtar uzunluğu)
echo "Zayıf sertifikalar oluşturuluyor..."
openssl req -x509 -newkey rsa:512 -keyout "$WEAK_DIR/server.key" \
    -out "$WEAK_DIR/server.crt" -days 30 -nodes \
    -subj "/CN=weak-csms.example.com" 2>/dev/null

openssl req -x509 -newkey rsa:512 -keyout "$WEAK_DIR/client.key" \
    -out "$WEAK_DIR/client.crt" -days 30 -nodes \
    -subj "/CN=weak-cp.example.com" 2>/dev/null

# Generate GÜÇLÜ sertifikalar (uzun süreli, yüksek anahtar uzunluğu)
echo "Güçlü sertifikalar oluşturuluyor..."
openssl req -x509 -newkey rsa:4096 -keyout "$STRONG_DIR/server.key" \
    -out "$STRONG_DIR/server.crt" -days 365 -nodes \
    -subj "/CN=secure-csms.example.com" 2>/dev/null

openssl req -x509 -newkey rsa:4096 -keyout "$STRONG_DIR/client.key" \
    -out "$STRONG_DIR/client.crt" -days 365 -nodes \
    -subj "/CN=secure-cp.example.com" 2>/dev/null

echo "✅ Sertifikalar hazır!"
echo ""
echo "📁 Konum:"
echo "   Zayıf: $WEAK_DIR/"
echo "   Güçlü: $STRONG_DIR/"

