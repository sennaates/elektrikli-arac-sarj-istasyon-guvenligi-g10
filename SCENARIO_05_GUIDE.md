# 🔴 Senaryo #5: Sahte Firmware ve Ransomware Saldırısı

## 📋 Senaryo Özeti

**Saldırı Tipi:** Firmware Manipulation / Ransomware Injection / DoS
**Hedef:** Şarj İstasyonu (EVSE) İşletim Sistemi ve Kontrol Ünitesi
**Severity:** CRITICAL
**Tespit Yöntemi:** IDS (Firmware Integrity Check & Network Anomaly)

Bu senaryo, OCPP protokolündeki **"Güvensiz Firmware Güncelleme (L02)"** zafiyetini istismar eder. Saldırgan, kendini CSMS gibi tanıtarak istasyona imzasız/zararlı bir güncelleme paketi gönderir. Paket yüklendiğinde istasyon kilitlenir ve Dashboard üzerinde fidye uyarısı görüntülenir.

---

## 🎯 Saldırı Akışı

```
[SALDIRGAN (Hacker)] → [İSTASYON (Hedef)]
```

* Saldırgan ağa sızar ve CSMS kimliğine bürünür (Spoofing).
* İstasyona **UpdateFirmware (CAN ID: 0x230)** komutu gönderir.
* Payload: **"Evil.bin"** firmware dosyasının indirilmesi.
* İstasyon doğrulama yapmadığı için yüklemeyi kabul eder.
* Saldırgan, yüksek entropili zararlı veri paketlerini ağa basar.
* Güncelleme tamamlanınca sistem **kilitlenir (Lockdown)**.
* Dashboard API'sine sinyal gönderilir: **"RANSOMWARE DETECTED"**.

---

## 🔬 Tespit Kuralları

### **R1: Firmware Integrity Failure**

**Kural:** Onaylanmamış veya dijital imzası bulunmayan güncelleme isteği.
**Severity:** CRITICAL

```python
if action == "UpdateFirmware" and signature_valid is False:
    → ALERT: FIRMWARE_INTEGRITY_FAILURE
```

---

### **R2: Malicious Payload Injection**

**Kural:** Bilinmeyen CAN ID'lerden gelen yüksek entropili veri akışı.
**Severity:** HIGH

```python
if unknown_can_id and data_entropy > threshold:
    → ALERT: MALICIOUS_PAYLOAD
```

---

## 🧪 Test Senaryoları

### **Test 1: Ransomware Simülasyonu**

```bash
# Terminal 1: Sistemi Başlat (Dashboard & API)
./quick_start.sh

# Terminal 2: Saldırıyı Başlat
python tests/scenario_05_ransomware.py
```

### Beklenen Sonuç:

* **Terminal:** "Yükleniyor... %100" ve **"SİSTEM KİLİTLENİYOR"** mesajları.
* **Dashboard:**

```
Alert Tipi: Firmware Integrity Failure
Mesaj: RANSOMWARE DETECTED: System locked. Unauthorized firmware update.
Severity: CRITICAL
```

---

## 📊 Dashboard Görünümü

```
┌─────────────────────────────────────────┐
│ 🚨 REAL-TIME ALERTS                     │
├─────────────────────────────────────────┤
│ 🔴 CRITICAL                             │
│    Firmware Integrity Failure           │
│    RANSOMWARE DETECTED: System locked.  │
│    Time: 14:35:22                       │
│    Source: IDS_FIRMWARE_CHECK           │
└─────────────────────────────────────────┘
```

---

## 🛡️ Azaltma Stratejileri

### **1. Güvenli Firmware Güncelleme (Priority: CRITICAL)**

Firmware paketleri mutlaka **dijital imza** içermeli ve istasyon tarafından doğrulanmalıdır.

### **2. TLS Şifreleme (Priority: HIGH)**

Tüm CSMS ↔ İstasyon trafiği **TLS 1.2 / 1.3** ile korunmalıdır.

### **3. Ağ İzolasyonu (Priority: MEDIUM)**

Şarj istasyonları **ayrı VLAN** üzerinde çalışmalıdır.

---

## 🔗 İlgili Dosyalar

* **Senaryo Kodu:** `tests/scenario_05_ransomware.py`
* **Kılavuz:** `SCENARIO_05_GUIDE.md`
* **Sistem Düzeltmesi:** `utils/can_handler.py` (WSL Virtual Mode Support)
* **API Düzeltmesi:** `api_server.py` (Indentation Bug Fix)

**Son Güncelleme:** 2025-12-08
**Versiyon:** 1.0
**Status:** ✅ PRODUCTION READY
