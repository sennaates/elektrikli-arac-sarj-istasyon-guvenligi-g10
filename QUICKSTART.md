# ⚡ Hızlı Başlangıç

## 5 Dakikada Başlangıç

### 1️⃣ Kurulum (2 dakika)

```bash
# Sanal ortam kur
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# CAN arayüzü ve sertifikaları hazırla
sudo bash scripts/setup_vcan.sh
bash scripts/generate_certs.sh
```

### 2️⃣ İlk Demo Çalıştır (1 dakika)

```bash
# Senaryo 1: Plain WebSocket demo
bash scripts/run_demo.sh plain_ws
```

### 3️⃣ Terminal Açıp İzle (2 dakika)

**3 farklı terminal açın:**

```bash
# Terminal 1: CSMS
python -m src.ocpp.central_system.simulator --scenario plain_ws --port 9000

# Terminal 2: CP
python -m src.ocpp.charge_point.simulator --scenario plain_ws --cp-id CP001

# Terminal 3: CAN trafiği
candump vcan0
```

**Artık CAN mesajlarını görebilirsiniz! 🎉**

## 📚 Sonraki Adımlar

### Okuma
1. [README.md](README.md) - Genel bakış
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Teknik detaylar
3. [USAGE.md](USAGE.md) - Kullanım örnekleri

### Deneme
1. Test senaryoları: `pytest tests/ -v`
2. MitM saldırısı: `python -m src.attacks.mitm_proxy`
3. CAN IDS: `python -m src.detection.can_ids`

### Geliştirme
1. Yeni CAN mapping ekleyin: `src/bridge/mapper.py`
2. Saldırı senaryosu yazın: `src/attacks/`
3. Test ekleyin: `tests/`

## 🎯 Senaryolar

| Senaryo | Komut | Açıklama |
|---------|-------|----------|
| Plain WS | `bash scripts/run_demo.sh plain_ws` | MitM'e açık |
| Weak TLS | `bash scripts/run_demo.sh weak_tls` | Zayıf şifreleme |
| Strong TLS | `bash scripts/run_demo.sh strong_tls` | Güvenli |

## 🐛 Sorun mu var?

```bash
# Tüm modüller yüklü mü?
python -c "import can, websockets, cryptography; print('✅ OK')"

# CAN arayüzü çalışıyor mu?
ip link show vcan0

# Port kullanımda mı?
sudo netstat -tulpn | grep 9000
```

## 📞 Yardım

- [INSTALL.md](INSTALL.md) - Detaylı kurulum
- [USAGE.md](USAGE.md) - Kullanım kılavuzu
- GitHub Issues - Soru/Problem bildirimi

---

**Hazırsanız, başlayalım! 🚀**

