# 🔧 Ubuntu VM'de SSH Kurulumu

## Ubuntu VM'de (Terminal):

```bash
# 1. SSH servisini kur
sudo apt-get update
sudo apt-get install -y openssh-server

# 2. SSH servisini başlat
sudo systemctl start ssh
sudo systemctl enable ssh

# 3. Firewall kontrolü (eğer aktifse)
sudo ufw allow ssh
sudo ufw allow 22

# 4. SSH servisinin çalıştığını kontrol et
sudo systemctl status ssh

# 5. IP adresini tekrar kontrol et
hostname -I
```

## Alternatif: UTM Shared Folder'ı Düzgün Çalıştırma

UTM'de shared folder bazen otomatik mount edilmez. Manuel mount edebiliriz:

```bash
# Ubuntu VM'de
# 1. SPICE guest tools kur
sudo apt-get install -y spice-vdagent spice-webdavd

# 2. VM'i yeniden başlat
sudo reboot

# 3. Yeniden başladıktan sonra kontrol et
ls -la /media/
ls -la /run/user/$(id -u)/gvfs/
```

## En Kolay Alternatif: USB veya Drag & Drop

UTM'de dosya aktarımı için:
1. macOS'ta projeyi zip'le: `zip -r bsg.zip /Users/earth/Downloads/bsg`
2. UTM'de VM penceresine sürükle-bırak yap
3. Ubuntu'da Downloads klasöründe görünecek

