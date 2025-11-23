# 📤 GitHub Push Talimatları

## ✅ Mevcut Durum

- ✅ Git repository başlatıldı
- ✅ Branch oluşturuldu: `güncelsimülasyonumuz`
- ✅ Remote repository eklendi
- ✅ Dosyalar commit edildi
- ⏳ Push için authentication gerekiyor

## 🔐 Push Yapmak İçin

### Seçenek 1: HTTPS ile (Önerilen - İlk Kullanım)

```bash
# Push yap (GitHub kullanıcı adı ve token/şifre isteyecek)
git push -u origin güncelsimülasyonumuz
```

**Not:** GitHub artık şifre yerine **Personal Access Token (PAT)** kullanıyor.

**Token Oluşturma:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" → "repo" yetkisi ver
3. Token'ı kopyala ve push sırasında şifre yerine kullan

### Seçenek 2: SSH ile (Daha Güvenli)

```bash
# SSH key oluştur (eğer yoksa)
ssh-keygen -t ed25519 -C "senin@email.com"

# Public key'i GitHub'a ekle
cat ~/.ssh/id_ed25519.pub
# Bu çıktıyı GitHub → Settings → SSH and GPG keys → New SSH key

# Remote URL'i SSH'a çevir
git remote set-url origin git@github.com:sennaates/elektrikli-arac-sarj-istasyon-guvenligi-g10.git

# Push yap
git push -u origin güncelsimülasyonumuz
```

### Seçenek 3: GitHub CLI ile

```bash
# GitHub CLI kur (eğer yoksa)
# Ubuntu/Debian:
sudo apt install gh

# Login ol
gh auth login

# Push yap
git push -u origin güncelsimülasyonumuz
```

## 📋 Mevcut Commit'ler

```bash
# Commit geçmişini gör
git log --oneline -5
```

## 🔍 Durum Kontrolü

```bash
# Hangi branch'te olduğunu gör
git branch

# Remote repository durumu
git remote -v

# Push edilmemiş commit'ler var mı?
git log origin/güncelsimülasyonumuz..HEAD --oneline
```

## ✅ Push Sonrası

Push başarılı olduktan sonra:

1. GitHub'da repository'yi kontrol et:
   https://github.com/sennaates/elektrikli-arac-sarj-istasyon-guvenligi-g10

2. Branch'i kontrol et:
   - `güncelsimülasyonumuz` branch'i görünmeli
   - Tüm dosyalar yüklenmiş olmalı

3. Ekip arkadaşlarına bildir:
   - Repository URL'i
   - Branch adı: `güncelsimülasyonumuz`
   - Rehber dosyaları: `SCENARIO_ADDITION_GUIDE.md`, `QUICK_START_FOR_TEAM.md`

---

**Not:** İlk push'tan sonra, ekip arkadaşları `git clone` ve `git checkout güncelsimülasyonumuz` ile projeyi alabilir.

