```markdown
# 🔴 Senaryo #4: Fuzzing ile OCPP Protokol Zafiyet Tespiti

## 📋 Senaryo Özeti

**Saldırı Tipi:** Fuzzing (Protocol Anomaly) / Input Validation Attacks  
**Hedef:** CSMS (Central System) Uygulama Katmanı ve Mesaj İşleme Mantığı  
**Severity:** HIGH (Potansiyel CRITICAL - DoS durumunda)  
**Tespit Yöntemi:** Rule-based IDS (Payload Boyutu, Veri Tipi ve Format Kontrolü)

Bu senaryo, OCPP protokolüne kasıtlı olarak hatalı (bozuk tip, aşırı uzunluk, geçersiz format) mesajlar göndererek hedef sistemin (CSMS) sağlamlığını test eder.

---

## 🎯 Saldırı Akışı

```

[SALDIRGAN (Fuzzer)] → [CSMS Hedef Sistem]

1.  Fuzzer, hedef CSMS'e WebSocket üzerinden bağlanır.
2.  Geçerli bir OCPP mesaj şablonu seçilir (örn. StartTransaction).
3.  Şablon üzerinde rastgele bir mutasyon uygulanır:
    a. Tip Mutasyonu (Int yerine String)
    b. Uzunluk Mutasyonu (Aşırı uzun veri - Buffer Overflow denemesi)
    c. Format Mutasyonu (Bozuk JSON yapısı)
4.  Bozulmuş mesaj (Malicious Payload) hedefe gönderilir.
5.  Hedef sistemin tepkisi izlenir (Çökme, Hata, Kaynak Tüketimi).

<!-- end list -->

````

---

## 🔬 Tespit Kuralları

### F1: Hedef Çökmesi (System Crash)
**Kural:** Beklenmedik payload sonrası sistemin kapanması veya kritik hata vermesi.  
**Severity:** CRITICAL  
**Mantık:**
```python
# Log analizi veya bağlantı kopması ile tespit edilir
if connection_dropped_unexpectedly or "Segmentation Fault" in logs:
    → ALERT: SYSTEM_CRASH_RISK
````

### F2: Yanıt Vermeme (Hang/DoS)

**Kural:** Fuzzing mesajına 10 saniye boyunca yanıt gelmemesi.  
**Severity:** HIGH  
**Mantık:**

```python
if (current_time - message_sent_time) > 10.0 and no_response:
    → ALERT: SYSTEM_UNRESPONSIVE
```

### F3: Payload Size Anomaly

**Kural:** Mesaj boyutunun normal sınırların (örn. 10KB) üzerinde olması.  
**Severity:** HIGH  
**Mantık:**

```python
# utils/ids.py içindeki check_ocpp_fuzzing metodu
if payload_size > 10000:
    → ALERT: PAYLOAD_SIZE_ANOMALY
```

### F4: Protocol Type Error

**Kural:** Mesaj alanlarında veri tipi uyuşmazlığı (String yerine Int gelmesi vb.).  
**Severity:** MEDIUM  
**Mantık:**

```python
# utils/ids.py içindeki check_ocpp_fuzzing metodu
if "connectorId" in message and not isinstance(message["connectorId"], int):
    → ALERT: OCPP_PROTOCOL_ERROR
```

-----

## 🧪 Test Senaryoları

### Test 1: Tip Mutasyonu (Type Mutation)

```bash
# Terminal 1: Simülasyonu/IDS'i çalıştır (veya logları izle)
# ...

# Terminal 2: Fuzzing saldırısını başlat
python attack_simulator.py --attack fuzzing --fuzz-intensity 5
```

**Beklenen Sonuç:**

  - ✅ Fuzzer, `connectorId` alanına string gönderir.
  - ✅ IDS alert: `OCPP_PROTOCOL_ERROR`
  - ✅ Severity: MEDIUM
  - ✅ Loglarda: "Tip uyuşmazlığı: connectorId integer olmalı"

### Test 2: Uzunluk Mutasyonu (Length Mutation)

```bash
# Fuzzing saldırısı rastgele seçim yaptığı için tekrar çalıştırılabilir veya koda müdahale edilebilir.
# Simülasyon gereği attack_simulator.py içinde bu senaryo rastgele seçilir.
python attack_simulator.py --attack fuzzing --fuzz-intensity 10
```

**Beklenen Sonuç:**

  - ✅ Fuzzer, `chargePointVendor` alanına 20KB veri gönderir.
  - ✅ IDS alert: `PAYLOAD_SIZE_ANOMALY`
  - ✅ Severity: HIGH
  - ✅ Loglarda: "Anormal payload boyutu tespit edildi"

### Test 3: Format Mutasyonu (Format Mutation)

**Beklenen Sonuç:**

  - ✅ Fuzzer, bozuk JSON (eksik parantez vb.) gönderir.
  - ✅ IDS alert: `JSON_PARSE_ERROR`
  - ✅ Severity: LOW
  - ✅ Hedef sistemin hata mesajı (veya IDS uyarısı)

-----

## 📊 Test Sonuçları (Örnek)

```
🚨 SALDIRI: [OCPP Protocol Fuzzing] başlatılıyor... Hedef: ws://localhost:9000
   Fuzzing [1/10]: Tip Mutasyonu gönderiliyor...
   ⚠️ ALERT [SCENARIO-4]: Tip uyuşmazlığı: connectorId integer olmalı. Gelen: <class 'str'>
   
   Fuzzing [2/10]: Uzunluk Mutasyonu (Buffer Overflow) gönderiliyor...
   🚨 ALERT [SCENARIO-4]: Anormal payload boyutu tespit edildi: 20050 bytes. Olası Fuzzing/Buffer Overflow denemesi.
   
   Fuzzing [3/10]: Format Mutasyonu gönderiliyor...
   ⚠️ ALERT [SCENARIO-4]: Bozuk JSON formatı algılandı.

✓ [OCPP Protocol Fuzzing] tamamlandı

Beklenen IDS Alerts:
  - PAYLOAD_SIZE_ANOMALY (High)
  - OCPP_PROTOCOL_ERROR (Medium)
  - JSON_PARSE_ERROR (Low)
```

-----

## 🛡️ Azaltma Stratejileri

### 1\. Kapsamlı Girdi Doğrulama (Priority: CRITICAL)

**Uygulama:**

```python
# JSON Schema Validation Kullanımı
from jsonschema import validate

schema = {
    "type": "object",
    "properties": {
        "connectorId": {"type": "integer", "minimum": 0},
        # ...
    }
}

def on_message(msg):
    try:
        validate(instance=msg, schema=schema)
    except ValidationError:
        return "ProtocolError"
```

**Etkinlik:** Tip ve format hatalarını %100'e yakın engeller.

### 2\. Payload Boyut Sınırı (Priority: HIGH)

**Uygulama:**

```python
# Ağ katmanında veya uygulama girişinde
MAX_PAYLOAD_SIZE = 4096 # 4KB

def receive_message(raw_data):
    if len(raw_data) > MAX_PAYLOAD_SIZE:
        drop_connection()
        log_security_event("Payload too large")
```

**Etkinlik:** Buffer overflow ve kaynak tüketimi saldırılarını engeller.

### 3\. Sağlam Hata Yönetimi (Priority: MEDIUM)

**Uygulama:**

```python
try:
    process_message(msg)
except Exception as e:
    logger.error(f"Beklenmeyen hata: {e}")
    # Asla stack trace'i istemciye dönme!
    return "InternalError" 
```

**Etkinlik:** Sistemin çökmesini engeller ve saldırgana bilgi sızmasını önler.

-----

## 📈 Dashboard Görünümü

### Alert Panel

```
┌─────────────────────────────────────────┐
│ 🚨 SECURITY ALERTS                      │
├─────────────────────────────────────────┤
│ 🟠 PAYLOAD_SIZE_ANOMALY                 │
│    Size: 20050 bytes                    │
│    Threshold: 10000 bytes               │
│    Time: 14:35:22                       │
│    Severity: HIGH                       │
├─────────────────────────────────────────┤
│ 🟡 OCPP_PROTOCOL_ERROR                  │
│    Field: connectorId                   │
│    Expected: Int, Got: String           │
│    Time: 14:35:23                       │
│    Severity: MEDIUM                     │
└─────────────────────────────────────────┘
```

-----

## 🔍 Log Analizi

### Fuzzer Logs

```json
{
  "timestamp": "2025-11-09T14:35:22Z",
  "source": "Fuzzer-01",
  "fuzzed_message_type": "StartTransaction",
  "mutation_type": "TYPE_MUTATION",
  "payload_preview": "{\"connectorId\": \"BU_BIR_STRING_DEGIL_INT_OLMALI\", ...}",
  "ids_detection": "OCPP_PROTOCOL_ERROR"
}
```

### IDS Statistics

```json
{
  "total_alerts": 3,
  "alert_breakdown": {
    "HIGH": 1,
    "MEDIUM": 1,
    "LOW": 1
  }
}
```

-----

## 🎓 Eğitim Senaryosu

### Adım 1: Normal Akış

Sistemin normal mesajlara (StartTransaction, StopTransaction) doğru yanıt verdiğini doğrula.

### Adım 2: Fuzzing Saldırısı

```bash
python attack_simulator.py --attack fuzzing --fuzz-intensity 10
```

### Adım 3: Gözlem

  - Terminal çıktısında IDS alarmlarını izle.
  - Hangi mutasyon tipinin hangi alarmı tetiklediğini not et.

### Adım 4: Analiz

  - "Neden bu mesaj sistemi zorladı?" sorusunu sor.
  - Girdi doğrulamanın önemini tartış.

-----

## 📚 Referanslar

  - **OCPPStorm:** A Comprehensive Fuzzing Tool for OCPP Implementations (M. Coppoletta et al.)
  - **OWASP:** Input Validation Cheat Sheet
  - **Fuzzing 101:** Protocol Fuzzing Basics

-----

## 🔗 İlgili Dosyalar

  - Senaryo Detayları: `tests/scenario_04_ocpp_fuzzing.py`
  - Saldırı Kodu: `attack_simulator.py` (ocpp\_fuzzing\_attack)
  - IDS Kuralları: `utils/ids.py` (check\_ocpp\_fuzzing)
  - Test Script: `attack_simulator.py` CLI komutları

-----

## ✅ Başarı Kriterleri

  - [x] F1, F2, F3 kuralları IDS'e eklendi
  - [x] Attack simulator Fuzzing fonksiyonu çalışıyor
  - [x] IDS alarmları dashboard'a düşüyor
  - [x] Test senaryoları belgelendi

-----

**Son Güncelleme:** 2024-11-24  
**Senaryo Versiyonu:** 1.0  
**Test Durumu:** ✅ HAZIR

```
```