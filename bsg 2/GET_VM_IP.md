# 📡 Ubuntu VM IP Adresini Öğrenme

## Ubuntu VM'de (Terminal):

```bash
# Yöntem 1: hostname komutu (Linux)
hostname -I

# Yöntem 2: ip komutu
ip addr show | grep "inet " | grep -v 127.0.0.1

# Yöntem 3: ifconfig (eski yöntem)
ifconfig | grep "inet " | grep -v 127.0.0.1

# Yöntem 4: Sadece IP adresini al
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}'
```

## macOS'tan VM IP'sini Öğrenme (Alternatif):

UTM NAT network kullanıyorsa, genellikle `192.168.64.x` aralığında olur.

```bash
# macOS terminal'inde
arp -a | grep -i utm
# veya
ping -c 1 ubuntu.local 2>/dev/null | head -1
```

## En Kolay Yöntem:

Ubuntu VM'de terminal açın ve şunu çalıştırın:
```bash
hostname -I
```

Çıktıyı bana gönderin, SCP komutunu hazırlayayım!

