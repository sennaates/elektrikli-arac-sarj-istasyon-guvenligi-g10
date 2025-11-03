# Proje Özeti: OCPP-CAN Bridge Güvenlik Simülasyonu

## 📋 Proje Tanımı

Bu proje, **OCPP (Open Charge Point Protocol)** ve **CAN-Bus** protokolleri arasındaki güvenlik köprüsünü simüle ederek, şarj istasyonu sistemlerindeki zafiyetleri test eder ve blokzincir tabanlı bir güvenlik katmanı önerisi sunar.

## 🎯 Temel Hedefler

1. **OCPP-CAN Köprü Güvenliği**: Şarj istasyonu (CP) ve merkezi yönetim (CSMS) arasındaki iletişimdeki güvenlik açıklarını simüle et
2. **Güvenlik Senaryoları**: Üç farklı güvenlik konfigürasyonu ile karşılaştırmalı analiz
3. **MitM Saldırıları**: Plain WebSocket üzerinde ortadaki adam saldırılarını göster
4. **CAN Anomali Tespiti**: CAN Intrusion Detection System ile saldırı tespiti
5. **Blokzincir Entegrasyonu**: Gelecekte blokzincir tabanlı güvenlik katmanı ekleme altyapısı

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                     CSMS (Central System)                    │
│                   ┌───────────────────┐                     │
│                   │  OCPP Simulator   │                     │
│                   │  (WebSocket/TLS)  │                     │
│                   └─────────┬─────────┘                     │
└─────────────────────────────┼───────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   MitM Proxy      │ ← Plain WS için saldırı
                    │   (9090)          │
                    └─────────┬─────────┘
                              │
                              │ OCPP Messages
                              │
┌─────────────────────────────▼───────────────────────────────┐
│               Charge Point (CP) Simulator                   │
│         ┌───────────────────────────────────────┐           │
│         │  OCPP Agent   │    Gateway Layer      │           │
│         └───────┬───────┴───────────┬───────────┘           │
└─────────────────┼───────────────────┼───────────────────────┘
                  │                   │
        ┌─────────▼─────────┐  ┌──────▼─────────────┐
        │   OCPP-CAN        │  │   CAN IDS          │
        │   Mapper          │  │   (Anomaly Det.)   │
        └─────────┬─────────┘  └────────────────────┘
                  │
                  │ CAN Frames
                  ▼
        ┌─────────────────────┐
        │  vcan0 (Virtual)    │
        │  or physical CAN    │
        └─────────────────────┘
                  │
                  ▼
        Charger Control Modules
        (Motor, Relay, Meter)
```

## 🔒 Güvenlik Senaryoları

### Senaryo 1: Plain WebSocket ⚠️
- **Güvenlik**: ❌ YOK
- **Risk**: 🔴 ÇOK YÜKSEK
- **Özellikler**:
  - Şifreleme yok
  - MitM saldırılarına açık
  - Mesaj manipülasyonu mümkün
- **Kullanım**: Saldırı demonstrasyonu

### Senaryo 2: Weak TLS ⚠️
- **Güvenlik**: ⚠️  ZAYIF
- **Risk**: 🟠 YÜKSEK
- **Özellikler**:
  - TLS 1.0 (eski protokol)
  - Self-signed sertifikalar (512 bit)
  - Certificate verification kapalı
  - Zayıf cipher suites
- **Kullanım**: Zayıf konfigürasyon etkisi gösterme

### Senaryo 3: Strong TLS ✅
- **Güvenlik**: ✅ GÜÇLÜ
- **Risk**: 🟢 DÜŞÜK
- **Özellikler**:
  - TLS 1.2+ (modern protokol)
  - Güçlü sertifikalar (4096 bit)
  - Certificate verification açık
  - Strong cipher suites
  - Mutual TLS desteği
- **Kullanım**: Önerilen güvenli konfigürasyon

## 📊 CAN Mesaj Mapping

| OCPP Action | CAN ID | Payload Format | Yön |
|-------------|--------|----------------|-----|
| RemoteStartTransaction | 0x200 | `[cp_id, connector_id]` | CSMS→CP→CAN |
| RemoteStopTransaction | 0x201 | `[tx_id(4B), stop_cmd]` | CSMS→CP→CAN |
| SetChargingProfile | 0x210 | `[profile_id(2B), connector_id, max_current]` | CSMS→CP→CAN |
| MeterValues | 0x300 | `[connector_id, energy(2B), voltage(2B), current(2B)]` | CAN→CP→CSMS |
| ChargeStatus | 0x301 | `[connector_id, status]` | CAN→CP→CSMS |

## 🛡️ Güvenlik Özellikleri

### 1. Zero Trust Architecture
- Her mesaj doğrulanır
- Kaynak kimlik doğrulaması zorunlu
- İzin verilmeyen işlemler reddedilir

### 2. Defense in Depth
- Birden fazla koruma katmanı:
  - Transport layer (TLS)
  - Application layer (OCPP validation)
  - Network layer (CAN filtering)

### 3. Intrusion Detection
- **CAN IDS**: Anomali tespiti
  - Frekans analizi
  - Beklenmeyen CAN ID tespiti
  - Burst attack tespiti
  - Temporal pattern analizi

### 4. Tamper-Evident Logging
- Tüm mesajlar kaydedilir
- Zaman damgalı loglar
- Değiştirilemez kayıtlar (gelecekte blokzincir)

## 🧪 Test Senaryoları

### Normal Akış Testi
```bash
# 1. CSMS başlat
python -m src.ocpp.central_system.simulator --scenario plain_ws

# 2. CP başlat
python -m src.ocpp.charge_point.simulator --scenario plain_ws

# 3. CAN trafiğini izle
candump vcan0
```

### MitM Saldırı Testi
```bash
# 1-2. Normal akışı başlat
# 3. MitM proxy ekle
python -m src.attacks.mitm_proxy

# 4. CP'yi proxy üzerinden bağla
python -m src.ocpp.charge_point.simulator --csms-url ws://localhost:9090/...
```

### Anomali Tespit Testi
```bash
python -m src.detection.can_ids
```

## 📈 Performans Metrikleri

### Ölçülecek Parametreler

1. **Gecikme (Latency)**
   - OCPP mesajı → CAN frame dönüşüm süresi
   - Hedef: < 10ms

2. **İletim Başarı Oranı**
   - Başarılı mesaj iletimi yüzdesi
   - Hedef: > 99%

3. **Tespit Oranı**
   - CAN IDS tarafından yakalanan anomali oranı
   - Hedef: > 95%

4. **Sistem Kaynakları**
   - CPU kullanımı
   - Bellek kullanımı
   - Ağ bant genişliği

## 🔮 Gelecek Geliştirmeler

### Kısa Vadeli
- [ ] Blokzincir entegrasyonu (hash tabanlı kayıt)
- [ ] Detaylı performans analizi
- [ ] Grafana/Prometheus monitoring
- [ ] Otomatik test suite

### Orta Vadeli
- [ ] Machine learning tabanlı anomali tespiti
- [ ] Gerçek donanım entegrasyonu
- [ ] V2X protokol desteği
- [ ] ISO 15118 uyumluluğu

### Uzun Vadeli
- [ ] End-to-end blokzincir güvenlik katmanı
- [ ] Federated learning ile IoT güvenliği
- [ ] Quantum-safe encryption
- [ ] Autonomous vehicle network

## 📚 Teknolojiler

### Backend
- **Python 3.9+**
- **asyncio**: Asenkron işlemler
- **websockets**: WebSocket protokolü
- **python-can**: CAN bus işlemleri

### Güvenlik
- **cryptography**: Şifreleme
- **OpenSSL**: TLS desteği
- **TLS 1.2/1.3**: Modern şifreleme

### Test & Analiz
- **pytest**: Unit testler
- **can-utils**: CAN trafik analizi
- **scikit-learn**: ML tabanlı tespit

### Simülasyon
- **vcan**: Virtual CAN bus
- **socketcan**: Linux CAN altyapısı

## 🎓 Akademik Bağlam

Bu proje, şu araştırma alanlarını kapsar:

1. **Otomotiv Siber Güvenliği**
   - ISO/SAE 21434 uyumluluğu
   - UN R155 standardı

2. **IoT/IoE Güvenliği**
   - V2X iletişim güvenliği
   - Akıllı şehir entegrasyonu

3. **Blockchain & DLT**
   - Decentralized security
   - Tamper-evident logging

4. **Intrusion Detection**
   - Behavioral analysis
   - Anomaly detection

## 👥 Kullanım Senaryoları

### Eğitim
- Otomotiv siber güvenliği dersleri
- CAN protokolü anlatımı
- Saldırı ve savunma demonstrasyonu

### Araştırma
- OCPP protokolü analizi
- Güvenlik katmanı geliştirme
- Performans optimizasyonu

### Endüstri
- Şarj istasyonu güvenliği testi
- Ürün validasyonu
- Compliance testleri

## ⚠️ Güvenlik ve Etik Uyarıları

- ⛔ Tüm testler **yalnızca izole laboratuvar ortamında** yapılmalı
- ⛔ Canlı altyapılara erişim **kesinlikle yasak**
- ⛔ Gerçek araç veya şarj istasyonlarında test yapılmamalı
- ✅ Sorumlu disclosure prensipleri uygulanmalı
- ✅ Tüm veriler anonimleştirilmeli
- ✅ Test sonuçları paylaşımında gizlilik korunmalı

## 📄 Lisans

Bu proje akademik araştırma amaçlıdır ve eğitim kullanımı içindir.

## 📞 İletişim

Proje hakkında sorular için issue tracker kullanın.

---

**Not**: Bu proje, blockchain tabanlı güvenlik çerçevesinin ilk adımı olarak tasarlanmıştır. Gelecek iterasyonlarda blokzincir altyapısı eklenecektir.

