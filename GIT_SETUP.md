# 🔧 Git Kurulumu ve İlk Push

## 1. Git Yapılandırması

İlk kez kullanıyorsan, Git'i yapılandır:

```bash
# Git kullanıcı adı ve email ayarla
git config --global user.name "Senin Adın"
git config --global user.email "senin@email.com"

# Veya sadece bu repository için:
git config user.name "Senin Adın"
git config user.email "senin@email.com"
```

## 2. Mevcut Durum

✅ Git repository başlatıldı
✅ Remote repository eklendi: https://github.com/sennaates/elektrikli-arac-sarj-istasyon-guvenligi-g10.git
✅ Branch oluşturuldu: `güncelsimülasyonumuz`
✅ Rehber dosyaları hazırlandı

## 3. İlk Push

Git yapılandırmasından sonra:

```bash
# Tüm dosyaları ekle (venv hariç - .gitignore'da)
git add .

# İlk commit
git commit -m "feat: Secure OCPP-to-CAN Bridge projesi eklendi

- 3 anomali senaryosu entegre edildi (Senaryo #1, #2, #3)
- Blockchain tabanlı güvenlik sistemi
- Real-time dashboard
- IDS (Rule-based + ML-based)
- Attack simulator
- Ekip arkadaşları için senaryo ekleme rehberleri"

# Branch'i push et
git push -u origin güncelsimülasyonumuz
```

## 4. Ekip Arkadaşları İçin

Ekip arkadaşları şu adımları izlemeli:

```bash
# 1. Repository'yi clone et
git clone https://github.com/sennaates/elektrikli-arac-sarj-istasyon-guvenligi-g10.git
cd elektrikli-arac-sarj-istasyon-guvenligi-g10

# 2. Branch'e geç
git checkout güncelsimülasyonumuz

# 3. Rehberleri oku
cat SCENARIO_ADDITION_GUIDE.md
cat QUICK_START_FOR_TEAM.md

# 4. Senaryo ekleme işlemlerini yap
# (Detaylar için SCENARIO_ADDITION_GUIDE.md'ye bak)
```

## 5. Senaryo Ekleme Sonrası

```bash
# Değişiklikleri ekle
git add tests/scenario_XX_*.py
git add SCENARIO_XX_GUIDE.md
git add README_SCENARIO_XX.md
git add utils/ids.py
git add attack_simulator.py

# Commit et
git commit -m "feat: Senaryo #XX eklendi - [Senaryo Adı]"

# Push et
git push origin güncelsimülasyonumuz
```

---

**Not:** İlk push'tan önce Git yapılandırmasını yapmayı unutma!

