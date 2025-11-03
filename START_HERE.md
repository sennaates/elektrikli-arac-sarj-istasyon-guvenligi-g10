# 🚀 START HERE - İlk Adım Rehberi

Merhaba! Bu projede kendi anomali senaryonuzu yazabilirsiniz.

## ✅ İzlenecek Sıra

### 1️⃣ Hızlı Tur (5 dakika)

**OKU:**
- [README.md](README.md) - Genel bakış
- [QUICKSTART.md](QUICKSTART.md) - Hızlı başlangıç

**DENE:**
```bash
bash scripts/run_demo.sh plain_ws
```

**SONUÇ:** 3 terminal penceresi açılmalı ve çalışmalı.

---

### 2️⃣ İlk Testinizi Çalıştırın (2 dakika)

```bash
pytest tests/my_scenario.py -v -s
```

**BEKLENEN:** "✅ TEST BAŞARILI!" mesajı

---

### 3️⃣ Senaryonuzu Yazın (15-30 dakika)

**OKU:**
- [HOW_TO_SUBMIT_SCENARIO.md](HOW_TO_SUBMIT_SCENARIO.md) - Format kuralları ve şablon
- tests/my_scenario.py - Şablon dosya

**YAPIN:**
```bash
# Şablon kopyala
cp tests/my_scenario.py tests/my_unique_test.py

# Düzenle
nano tests/my_unique_test.py

# Test et
pytest tests/my_unique_test.py -v -s
```

---

### 4️⃣ Senaryonuzu Gönderin! (10 dakika)

**OKU:**
- [HOW_TO_SUBMIT_SCENARIO.md](HOW_TO_SUBMIT_SCENARIO.md) - 📤 Nasıl gönderirim?

**YAPIN:**
```bash
# Git ile gönderin veya
git add tests/my_unique_test.py
git commit -m "Add scenario: my_scenario by YourName"
git push

# Ya da dosyayı direkt paylaşın
```
Hazırladığınız senaryo projeye eklenecek ve sizin adınızla kredilendirilecek! 🎉

---

## 📚 Tüm Dokümantasyon

| Dosya | İçerik | Zaman |
|-------|--------|-------|
| START_HERE.md | Bu dosya (okuyorsunuz) | - |
| README.md | Genel bakış ve kurulum | 5 dk |
| QUICKSTART.md | Hızlı başlangıç kılavuzu | 3 dk |
| **HOW_TO_SUBMIT_SCENARIO.md** | 📤 **Senaryo gönderme rehberi** | 10 dk |
| USAGE.md | Kullanım örnekleri | 10 dk |
| INSTALL.md | Detaylı kurulum | 10 dk |
| PROJECT_SUMMARY.md | Teknik mimari | 15 dk |

---

## 🐛 Sorun mu Yaşıyorsunuz?

### "bash: python: command not found"

```bash
# Virtual environment'ı aktif et
source venv/bin/activate
which python
```

### "Port already in use"

```bash
# Eski process'leri temizle
pkill -f "csms\|charge_point"
sleep 1
```

### "CAN bus error"

```bash
# CAN interface kontrol et
ip link show vcan0

# Yoksa oluştur
sudo bash scripts/setup_vcan.sh
```

### "Import error"

```bash
# Bağımlılıkları yükle
source venv/bin/activate
pip install -r requirements.txt
```

---

## ✅ Başarı Kriterleri

Senaryonuz başarılı sayılır eğer:

- [ ] pytest tests/your_file.py -v geçiyor
- [ ] En az 1 assertion var
- [ ] Setup ve cleanup düzgün yapılıyor
- [ ] Loglar anlamlı mesajlar içeriyor
- [ ] Kod yorumlanmış ve anlaşılır

---

## 📞 Yardım

- **Sorular:** Dokümantasyonu tekrar okuyun
- **Buglar:** GitHub Issues
- **Fikirler:** Tartışmak için GitHub Discussions

---

## 🎉 Hazırsınız!

Şimdi bir sonraki adıma geçin:

→ **README.md** okumaya başlayın!

```bash
cat README.md
```

Başarılar! 🚀
