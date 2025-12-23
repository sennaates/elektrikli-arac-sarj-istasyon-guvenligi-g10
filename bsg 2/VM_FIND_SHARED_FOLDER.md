# 🔍 Shared Folder'ı Bulma

Ubuntu VM'de şu komutları çalıştırın:

```bash
# 1. Farklı yerlerde ara
ls -la /media/
ls -la /run/user/
find /media -name "bsg" 2>/dev/null
find /mnt -name "bsg" 2>/dev/null

# 2. Tüm mount edilmiş dosya sistemlerini kontrol et
mount | grep -i bsg
df -h | grep -i bsg

# 3. SPICE shared folder kontrolü
ls -la /run/user/$(id -u)/gvfs/
```

Eğer hiçbir yerde bulamazsanız, SCP ile kopyalama yöntemini kullanın.

