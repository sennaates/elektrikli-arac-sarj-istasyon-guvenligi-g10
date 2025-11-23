# 🔴 Senaryo #1: Man-in-the-Middle OCPP Manipulation

## 📋 Senaryo Özeti

**Saldırı Tipi:** Man-in-the-Middle (MitM) + Message Tampering  
**Hedef:** OCPP mesajlarını manipüle ederek CAN-Bus'a yanlış komutlar gönderme  
**Severity:** CRITICAL (CVSS 8.5)  
**Tespit Yöntemi:** Hybrid (Rule-based + Statistical)

---

## 🎯 Saldırı Akışı

```
CSMS → [SALDIRGAN] → CP → CAN-Bus → Araç

1. RemoteStartTransaction gönderilir
2. Saldırgan mesajı yakalar
3. RemoteStopTransaction'a çevirir
4. CP manipüle edilmiş mesajı alır
5. CAN ID 0x201 (Stop) gönderir (0x200 yerine)
6. Şarj beklenmedik şekilde durur
```

---

## 🔬 Tespit Kuralları

### K1: Timing Mismatch
**Kural:** RemoteStart sonrası 2 saniye içinde RemoteStop  
**Severity:** HIGH  
**Mantık:**
```python
if action == "RemoteStopTransaction":
    for prev_action in last_actions:
        if prev_action == "RemoteStartTransaction":
            if (timestamp_diff < 2.0):
                → ALERT: TIMING_MISMATCH_K1
```

### K2: Session Fingerprint Change
**Kural:** Aynı idTag için 3+ farklı IP adresi  
**Severity:** CRITICAL  
**Mantık:**
```python
if len(session_fingerprints[idTag]) > 2:
    → ALERT: SESSION_FINGERPRINT_CHANGE_K2
```

### K3: OCPP-CAN Mapping Mismatch
**Kural:** OCPP action ile CAN ID uyuşmazlığı  
**Severity:** CRITICAL  
**Mantık:**
```python
expected_can_id = mapping["RemoteStartTransaction"]  # 0x200
if actual_can_id != expected_can_id:  # 0x201 geldi
    → ALERT: OCPP_CAN_MISMATCH_K3
```

---

## 🧪 Test Senaryoları

### Test 1: Start → Stop Manipulation

```bash
# Terminal 1: Bridge çalıştır
python secure_bridge.py

# Terminal 2: Saldırıyı simüle et
python attack_simulator.py --attack mitm --mitm-scenario start_to_stop
```

**Beklenen Sonuç:**
- ✅ IDS alert: `OCPP_CAN_MISMATCH_K3`
- ✅ Severity: CRITICAL
- ✅ Dashboard'da kırmızı alarm
- ✅ Blockchain'e ALERT bloğu

### Test 2: Stop → Start Manipulation

```bash
python attack_simulator.py --attack mitm --mitm-scenario stop_to_start
```

### Test 3: Timing Anomaly

```bash
python attack_simulator.py --attack mitm --mitm-scenario timing_anomaly
```

**Beklenen Sonuç:**
- ✅ IDS alert: `TIMING_MISMATCH_K1`
- ✅ Start frame gönderilir
- ✅ 1 saniye sonra Stop frame
- ✅ Anomali tespit edilir

---

## 📊 Test Sonuçları (Örnek)

```
🚨 SALDIRI: MitM OCPP Manipulation başlatılıyor...
   Senaryo: start_to_stop
   [Simülasyon] RemoteStartTransaction komutu yakalandı
   [Manipülasyon] Start → Stop dönüştürülüyor
   [CP Action] RemoteStopTransaction olarak işleniyor
   ⚠️  OCPP-CAN Mismatch: Start bekleniyor ama Stop frame gönderildi!
   [IDS] K3 kuralı tetiklenmeli: OCPP_CAN_MISMATCH

✓ MitM OCPP Manipulation tamamlandı

Beklenen IDS Alerts:
  - OCPP_CAN_MISMATCH (K3)
  - TIMING_ANOMALY (K1)
  - Severity: CRITICAL
  - Dashboard: Kırmızı alarm görünmeli
```

---

## 🛡️ Azaltma Stratejileri

### 1. Mutual TLS (Priority: CRITICAL)

**Uygulama:**
```python
# secure_bridge.py konfigürasyonu
OCPP_SECURITY_PROFILE = 3  # Mutual TLS
CLIENT_CERT = "/path/to/cp_cert.pem"
CLIENT_KEY = "/path/to/cp_key.pem"
CA_CERT = "/path/to/csms_ca.pem"
```

**Etkinlik:** MitM saldırılarını %95+ engeller

### 2. Payload Signing (Priority: HIGH)

**Uygulama:**
```python
import hmac
import hashlib

def sign_payload(payload: dict, secret: str) -> str:
    data = json.dumps(payload, sort_keys=True).encode()
    return hmac.new(secret.encode(), data, hashlib.sha256).hexdigest()

def verify_payload(payload: dict, signature: str, secret: str) -> bool:
    expected_sig = sign_payload(payload, secret)
    return hmac.compare_digest(signature, expected_sig)
```

### 3. Gateway Whitelist (Priority: HIGH)

**Uygulama:**
```python
# utils/can_handler.py
ALLOWED_MAPPINGS = {
    "RemoteStartTransaction": 0x200,
    "RemoteStopTransaction": 0x201,
    "SetChargingProfile": 0x210,
    # ...
}

def validate_mapping(ocpp_action: str, can_id: int) -> bool:
    expected_id = ALLOWED_MAPPINGS.get(ocpp_action)
    return expected_id == can_id
```

### 4. SIEM Correlation (Priority: MEDIUM)

**Kural:**
```
IF (K2: Session Fingerprint Change) AND (K3: OCPP-CAN Mismatch):
    → CRITICAL ALARM: "MitM Attack Detected"
    → AUTO-RESPONSE: Block source IP
    → NOTIFY: Security team
```

---

## 📈 Dashboard Görünümü

### Alert Panel
```
┌─────────────────────────────────────────┐
│ 🚨 CRITICAL ALERTS                      │
├─────────────────────────────────────────┤
│ 🔴 OCPP_CAN_MISMATCH_K3                 │
│    RemoteStart için 0x200 bekleniyor    │
│    Ancak 0x201 geldi                    │
│    Time: 14:35:22                       │
│    Severity: CRITICAL                   │
├─────────────────────────────────────────┤
│ 🟠 TIMING_MISMATCH_K1                   │
│    Start sonrası 1.2s'de Stop           │
│    Threshold: 2.0s                      │
│    Time: 14:35:23                       │
│    Severity: HIGH                       │
└─────────────────────────────────────────┘
```

### Traffic Analysis
```
OCPP → CAN Mapping Success Rate
Time Window: Last 5 minutes

Normal Baseline: 95%
Current: 72% ⚠️

┌──────────────────────┐
│ ████████░░░░░░░░░░  │ 72%
└──────────────────────┘
```

---

## 🔍 Log Analizi

### Blockchain Logs
```json
{
  "index": 42,
  "type": "ALERT",
  "data": {
    "alert_type": "OCPP_CAN_MISMATCH_K3",
    "severity": "CRITICAL",
    "ocpp_action": "RemoteStartTransaction",
    "expected_can_id": "0x200",
    "actual_can_id": "0x201"
  },
  "hash": "a3f5b2...7e9c",
  "signature": "3045...a92f"
}
```

### IDS Statistics
```json
{
  "total_alerts": 2,
  "alert_breakdown": {
    "CRITICAL": 1,
    "HIGH": 1
  },
  "can_id_frequency": {
    "0x200": 45,
    "0x201": 48  // Anormal artış
  },
  "ocpp_action_frequency": {
    "RemoteStartTransaction": 50,
    "RemoteStopTransaction": 2  // Çok az (manipülasyon göstergesi)
  }
}
```

---

## 🎓 Eğitim Senaryosu

### Adım 1: Normal Trafik
```bash
# 100 normal işlem gerçekleştir
for i in {1..100}; do
    # Normal OCPP → CAN akışı
done
```

### Adım 2: Saldırı
```bash
python attack_simulator.py --attack mitm --mitm-scenario start_to_stop
```

### Adım 3: Gözlem
- Dashboard'u izle
- Alert'leri kontrol et
- Blockchain'i doğrula
- Log analizi yap

### Adım 4: Azaltma
- mTLS aktif et
- Payload signing uygula
- Gateway whitelist ekle

### Adım 5: Tekrar Test
```bash
# Saldırı tekrarlanmalı ama başarısız olmalı
python attack_simulator.py --attack mitm --mitm-scenario start_to_stop
# Beklenen: Connection refused veya Invalid signature
```

---

## 📚 Referanslar

- **OCPP v2.0.1 Spec:** Part 2, Section 15.3 (Security)
- **STRIDE Model:** Microsoft Threat Modeling
- **ISO 15118-20:** V2G Communication Security
- **CVE-2021-31800:** EV Charging MitM
- **CVE-2020-8858:** OCPP Authentication Bypass

---

## 🔗 İlgili Dosyalar

- Senaryo Detayları: `tests/scenario_01_mitm_ocpp_manipulation.py`
- Saldırı Kodu: `attack_simulator.py` (mitm_ocpp_manipulation)
- IDS Kuralları: `utils/ids.py` (K1, K2, K3)
- Test Script: Bu dosyanın test komutları

---

## ✅ Başarı Kriterleri

- [x] K1, K2, K3 kuralları implement edildi
- [x] Attack simulator'a MitM fonksiyonu eklendi
- [x] IDS alert'leri doğru severity ile üretiliyor
- [x] Blockchain'e ALERT blokları kaydediliyor
- [x] Dashboard'da görselleştirme çalışıyor
- [x] Test senaryoları çalıştırılabilir durumda

---

**Son Güncelleme:** 2024-11-23  
**Senaryo Versiyonu:** 1.0  
**Test Durumu:** ✅ HAZIR

