FROM ubuntu:22.04

# Sistem paketlerini kur
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    can-utils \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# Proje dosyalarını kopyala
COPY . /app/

# Virtual environment oluştur ve paketleri kur
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# vcan0 kurulum scripti
RUN chmod +x setup_vcan.sh quick_start.sh

# Varsayılan komut
CMD ["/bin/bash"]
