# Docker ile CAN Bus Desteği

macOS'ta CAN bus desteği olmadığı için Docker container içinde Linux kullanarak testleri çalıştırabilirsiniz.

## 🚀 Hızlı Başlangıç

### İlk Kez (Image Build)

```bash
cd /Users/earth/Downloads/bsg
./docker/build_image.sh
```

Bu komut:
- Ubuntu 22.04 image'ını indirir
- Tüm paketleri yükler (can-utils, python3, pip, vb.)
- Python bağımlılıklarını yükler
- `bsg-test` adında bir image oluşturur

**Süre**: ~5-10 dakika (sadece bir kez)

### Sonraki Çalıştırmalar (Hızlı)

```bash
cd /Users/earth/Downloads/bsg
./docker/run_test.sh
```

Bu komut:
- Build edilmiş image'ı kullanır
- Sadece testi çalıştırır
- **Çok hızlı!** (~10-30 saniye)

## 📋 Komutlar

| Komut | Açıklama | Süre |
|-------|----------|------|
| `./docker/build_image.sh` | Image'ı build et (ilk kez) | ~5-10 dk |
| `./docker/run_test.sh` | Testi çalıştır (cache'den) | ~10-30 sn |

## 🔄 Image'ı Yeniden Build Etme

Eğer `requirements.txt` veya sistem paketlerinde değişiklik yaptıysanız:

```bash
./docker/build_image.sh
```

## 🗑️ Image'ı Silme

```bash
docker rmi bsg-test
```

## 📊 Image Boyutu

- Base Ubuntu: ~100MB
- Paketler: ~300MB
- Python bağımlılıkları: ~200MB
- **Toplam**: ~600MB

## 🐛 Sorun Giderme

### "bsg-test image bulunamadı"

```bash
./docker/build_image.sh
```

### "Permission denied"

```bash
chmod +x docker/*.sh
```

### Image'ı temizlemek istiyorum

```bash
docker rmi bsg-test
docker system prune -a  # Tüm kullanılmayan image'ları sil
```

---

**Not**: İlk build'den sonra her test çalıştırması çok hızlı olacak! 🚀
