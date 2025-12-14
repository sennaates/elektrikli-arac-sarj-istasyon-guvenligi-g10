# Dockerfile for OCPP-CAN Bridge with CAN bus support
FROM ubuntu:22.04

# Non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    can-utils \
    iproute2 \
    net-tools \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies (cache'lenir)
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create vcan0 interface script (Linux'ta çalışır)
RUN echo '#!/bin/bash\n\
set -e\n\
echo "🔧 CAN modülleri yükleniyor..."\n\
modprobe can || { echo "❌ can modülü yüklenemedi"; exit 1; }\n\
modprobe can_raw || { echo "❌ can_raw modülü yüklenemedi"; exit 1; }\n\
modprobe vcan || { echo "❌ vcan modülü yüklenemedi"; exit 1; }\n\
echo "✅ CAN modülleri yüklendi"\n\
echo "📡 vcan0 oluşturuluyor..."\n\
ip link delete vcan0 2>/dev/null || true\n\
ip link add dev vcan0 type vcan || { echo "❌ vcan0 oluşturulamadı"; exit 1; }\n\
ip link set up vcan0 || { echo "❌ vcan0 aktif edilemedi"; exit 1; }\n\
ip link show vcan0\n\
echo "✅ vcan0 hazır!"\n\
' > /usr/local/bin/setup_vcan.sh && chmod +x /usr/local/bin/setup_vcan.sh

# Default command
CMD ["/bin/bash"]

