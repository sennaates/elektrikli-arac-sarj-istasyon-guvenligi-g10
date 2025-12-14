# 📁 UTM'de Shared Folder Ekleme - Adım Adım Rehber

## 🎯 Yöntem 1: UTM Shared Directory (UTM 4.0+)

### Adım 1: VM'i Durdurun
- UTM'de Ubuntu VM'iniz açık ise, **kapatın** (Shut Down)
- VM çalışırken ayarları değiştiremezsiniz

### Adım 2: VM Ayarlarını Açın
1. UTM ana penceresinde Ubuntu VM'inizi **seçin** (tıklayın)
2. Sağ üstte **"Edit"** (Düzenle) butonuna tıklayın
   - VEYA VM'e sağ tıklayıp **"Edit"** seçin

### Adım 3: Sharing Bölümünü Bulun
1. Sol menüde **"Sharing"** sekmesine tıklayın
   - Eğer "Sharing" yoksa, **"Drives"** veya **"USB"** sekmesine bakın
   - UTM versiyonuna göre farklı olabilir

### Adım 4: Shared Directory Ekleme
1. **"Shared Directory"** bölümünde **"+"** (artı) butonuna tıklayın
2. Açılan pencerede:
   - **"Directory"** yanındaki **"Browse"** veya **"Choose"** butonuna tıklayın
   - Finder açılacak
3. Finder'da şu klasöre gidin:
   ```
   /Users/earth/Downloads/bsg
   ```
   - VEYA Finder'da **Cmd+Shift+G** tuşlarına basın
   - `/Users/earth/Downloads/bsg` yazın ve Enter'a basın
   - `bsg` klasörünü **seçin** (klasörün içine girmeyin, klasörün kendisini seçin)
4. **"Open"** veya **"Choose"** butonuna tıklayın

### Adım 5: Mount Point (Opsiyonel)
- **"Mount Point"** alanına şunu yazın: `/mnt/bsg`
- VEYA boş bırakın (otomatik mount edilir)

### Adım 6: Kaydet
1. Sağ altta **"Save"** butonuna tıklayın
2. VM ayarları kapanacak

### Adım 7: VM'i Başlatın
1. Ubuntu VM'inizi **başlatın**
2. Ubuntu açıldığında, shared folder otomatik olarak mount edilir

### Adım 8: Ubuntu'da Klasörü Bulun
Ubuntu terminal'inde şunları çalıştırın:

```bash
# Shared folder'ı bul
ls -la /mnt/
# veya
ls -la /media/
# veya
ls -la ~/Desktop/

# Eğer görünmüyorsa, mount edin
sudo mkdir -p /mnt/bsg
sudo mount -t 9p -o trans=virtio,version=9p2000.L /mnt/bsg /mnt/bsg

# Projeyi kopyala (home dizinine)
cp -r /mnt/bsg ~/bsg
cd ~/bsg
```

---

## 🚀 Yöntem 2: SCP ile Kopyalama (Daha Kolay!)

Bu yöntem daha kolay ve hızlıdır. UTM shared folder ile uğraşmak istemiyorsanız:

### Adım 1: Ubuntu VM'de IP Adresini Öğrenin
Ubuntu terminal'inde:
```bash
ip addr show | grep "inet "
# veya
hostname -I
```
IP adresini not edin (örn: `192.168.64.5`)

### Adım 2: macOS Terminal'inde Kopyalayın
macOS'ta terminal açın ve:

```bash
# Ubuntu VM'in IP adresini kullanın
scp -r /Users/earth/Downloads/bsg ubuntu@192.168.64.5:/home/ubuntu/

# Şifre soracak (Ubuntu kurulumunda belirlediğiniz şifre)
```

### Adım 3: Ubuntu'da Kontrol Edin
Ubuntu terminal'inde:
```bash
cd ~/bsg
ls -la
# Proje dosyalarını görmelisiniz!
```

---

## 📦 Yöntem 3: Git ile Clone (En Kolay!)

Eğer projeniz GitHub'da ise:

### Ubuntu VM'de:
```bash
# Git kur
sudo apt-get update
sudo apt-get install -y git

# Projeyi klonla (repo URL'inizi kullanın)
git clone https://github.com/kullaniciadi/bsg.git ~/bsg
cd ~/bsg
```

---

## 🎯 Yöntem 4: USB ile Aktarma

1. macOS'ta projeyi USB'ye kopyalayın
2. UTM'de USB'yi VM'e bağlayın
3. Ubuntu'da USB'yi mount edin
4. Dosyaları kopyalayın

---

## ✅ Hangi Yöntemi Seçmeliyim?

| Yöntem | Zorluk | Hız | Öneri |
|--------|--------|-----|-------|
| **SCP** | ⭐ Kolay | ⚡ Hızlı | ✅ **ÖNERİLEN** |
| **Git Clone** | ⭐ Çok Kolay | ⚡ Çok Hızlı | ✅ Eğer repo varsa |
| **Shared Folder** | ⭐⭐ Orta | 🐌 Yavaş | ⚠️ UTM'de bazen sorunlu |
| **USB** | ⭐⭐ Orta | 🐌 Yavaş | ⚠️ Manuel işlem |

---

## 🔧 UTM'de Shared Folder Sorunları

### Sorun: Shared folder görünmüyor
```bash
# Ubuntu'da SPICE guest tools kur
sudo apt-get install -y spice-vdagent spice-webdavd

# VM'i yeniden başlat
```

### Sorun: Mount edilemiyor
```bash
# Manuel mount dene
sudo mkdir -p /mnt/bsg
sudo mount -t 9p -o trans=virtio,version=9p2000.L,msize=104857600 /mnt/bsg /mnt/bsg
```

---

## 💡 Öneri

**En kolay yöntem: SCP ile kopyalama**

1. Ubuntu VM'de IP öğren: `hostname -I`
2. macOS terminal'de: `scp -r /Users/earth/Downloads/bsg ubuntu@<IP>:/home/ubuntu/`
3. Şifre gir
4. Bitti! ✅

---

**Hazırlayan**: Auto (Cursor AI)
**Tarih**: 2025-01-27

