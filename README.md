📘 Kapsamlı Proje Dokümantasyonu

🔐 Secure OCPP-to-CAN Bridge

Blockchain Destekli Otomotiv Ağ Geçidi ve ML Tabanlı Saldırı Tespit Sistemi

📋 İÇİNDEKİLER

Proje Kimliği

Yönetici Özeti (Asansör Konuşması)

Genel Bakış

Teknik Gereksinimler

İşlevsellik ve Senaryolar

Sistem Mimarisi ve Tasarım

Risk Analizi

Yazılım Mühendisliği Yaklaşımı

Arayüzler ve Servisler

Proje Durumu ve İlerleyiş

Sürüm Kontrol ve Depo

1. PROJE KİMLİĞİ

Kategori

Detay

Proje Adı

Secure OCPP-to-CAN Bridge

Proje Türü

Akademik Araştırma - EVSE Siber Güvenliği

Dönem

2024-2025 Akademik Yılı

Liderler

Sude Demir, Sudem Cücemen

👥 Proje Ekibi

Ad Soyad

Rol / Görev Alanı

Sude Demir

Proje Lideri & Backend

Sudem Cücemen

Proje Lideri & Dokümantasyon

Sena Ateş

Geliştirici

Enes Malik

Geliştirici

Uğur Berktaş

Geliştirici

İbrahim Kerem Güven

Geliştirici

Semih Tepe

Geliştirici

Özgün Deniz Sevilmiş

Geliştirici

Şerif Bayram

Geliştirici

Oğuzhan Erdoğan

Geliştirici

Selanur Ayaz

Geliştirici

2. YÖNETİCİ ÖZETİ (ASANSÖR KONUŞMASI)

"Elektrikli araç şarj istasyonlarında, OCPP protokolü ile araç içi CAN-Bus arasındaki kritik köprüyü güvenli hale getiriyoruz. Blockchain teknolojisi ile her mesajı değiştirilemez şekilde kaydediyor, makine öğrenmesi destekli hibrit bir saldırı tespit sistemi (IDS) ile gerçek zamanlı tehditleri yakalıyoruz. Sistemimiz, saldırganların şarj işlemlerini manipüle etmesini, enerji ölçümlerini çalmasını ve araç kontrol sistemlerine yetkisiz erişim sağlamasını engelliyor. Modern otomotiv siber güvenliği için endüstri standardı, izlenebilir bir çözüm sunuyoruz."

3. GENEL BAKIŞ

3.1 Proje Amacı

Bu proje, Elektrikli Araç Şarj İstasyonları (EVCS) yönetiminde kullanılan OCPP (Open Charge Point Protocol) ile araç içi iletişim standardı olan CAN-Bus arasındaki veri akışını güvence altına almayı hedefler. Sistem üç temel savunma katmanı üzerine inşa edilmiştir:

🛡️ Güvenlik Katmanı: Blockchain tabanlı değiştirilemez (immutable) kayıt defteri.

🔍 Tespit Katmanı: Kural tabanlı ve Makine Öğrenmesi (ML) destekli Hibrit IDS.

📊 İzleme Katmanı: Gerçek zamanlı sistem görünürlüğü sağlayan Web Dashboard.

3.2 Kapsam ve Hedefler

Protokol Dönüşümü: OCPP 1.6 komutlarının CAN frame'lerine güvenli çevirimi.

Veri Bütünlüğü: SHA-256 ve ECDSA imzaları ile verinin inkar edilemezliği.

Anomali Tespiti: 10 farklı saldırı vektörüne karşı koruma.

Standartlara Uyum: ISO/SAE 21434 ve UN R155 prensiplerine uygunluk.

4. TEKNİK GEREKSİNİMLER

4.1 Fonksiyonel Gereksinimler (FR)

FR1 - Protokol Köprüsü: Sistem, RemoteStartTransaction gibi OCPP komutlarını ilgili CAN ID'lerine (örn: 0x200) hatasız dönüştürmelidir.

FR2 - Blockchain Kaydı: Her işlem bir blok oluşturmalı, SHA-256 ile hash'lenmeli ve dijital olarak imzalanmalıdır.

FR3 - Hibrit IDS: Sistem hem bilinen imza tabanlı saldırıları (Rule-based) hem de bilinmeyen anomalileri (Isolation Forest) tespit etmelidir.

FR4 - Canlı İzleme: Web arayüzü, blok zinciri durumunu ve alarmları <3 saniye gecikmeyle yansıtmalıdır.

FR5 - Simülasyon: Test amaçlı entegre bir saldırı simülatörü (Injection, Flooding vb.) barındırmalıdır.

4.2 Fonksiyonel Olmayan Gereksinimler (NFR)

Performans: Alert tespit süresi <100ms, Blockchain yazma süresi <50ms.

Güvenilirlik: Hata durumunda otomatik kurtarma (Self-recovery).

Taşınabilirlik: Linux (Tam destek) ve Windows (Sanal arayüz desteği) uyumluluğu.

Teknoloji Yığını: Python 3.9+, Streamlit, FastAPI, python-can.

5. İŞLEVSELLİK VE SENARYOLAR

5.1 Temel Akışlar (Use Cases)

UC1: Güvenli Şarj Başlatma

CSMS: Şarj başlat komutu gönderir.

Bridge: Komutu alır, doğrular ve Blockchain'e "PENDING" olarak yazar.

IDS: Komutta anomali tarar.

Bridge: Komutu CAN Frame'e (0x200) çevirip araca iletir.

Blockchain: İşlemi "COMPLETED" olarak mühürler.

UC2: Saldırı Tespiti (Intrusion Detection)

Saldırgan: Yetkisiz bir CAN mesajı (Injection) gönderir.

IDS: Mesajın imzasını veya frekansını analiz eder.

Karar: Anomali tespit edilir (HIGH Severity).

Eylem: Mesaj engellenir, Blockchain'e "ALERT" bloğu eklenir.

Dashboard: Operatöre görsel ve sesli uyarı verilir.

5.2 Bileşen Detayları

Web Dashboard: Real-time monitoring, Blockchain explorer, Traffic analysis.

İşlem Yönetimi: Blok üretimi, Hash hesaplama, İmza doğrulama.

Veri Tabanı: In-memory Blockchain yapısı (Simülasyon amaçlı), JSON export yeteneği.

6. SİSTEM MİMARİSİ VE TASARIM

6.1 Yüksek Seviye Mimari

Sistem, dış dünya (CSMS) ile araç (CAN-Bus) arasında bir güvenlik duvarı gibi çalışır.

      [BULUT / YÖNETİM]                  [GÜVENLİ AĞ GEÇİDİ]                 [ARAÇ AĞI]
┌──────────────────────────┐      ┌───────────────────────────────┐      ┌───────────────┐
│                          │      │                               │      │               │
│   CSMS (OCPP Server)     │◄────►│  SECURE BRIDGE (Orchestrator) │◄────►│    vcan0      │
│                          │      │                               │      │   (CAN Bus)   │
└──────────────────────────┘      └──────────────┬────────────────┘      └───────────────┘
                                                 │
                                       ┌─────────┴──────────┐
                                       │                    │
                              ┌────────▼───────┐    ┌───────▼───────┐
                              │   BLOCKCHAIN   │    │      IDS      │
                              │ (Immutable DB) │    │  (AI + Rule)  │
                              └────────┬───────┘    └───────┬───────┘
                                       │                    │
                                       ▼                    ▼
                              ┌─────────────────────────────────────┐
                              │             API SERVER              │
                              │       (FastAPI + WebSocket)         │
                              └──────────────────┬──────────────────┘
                                                 │
                                                 ▼
                                      ┌──────────────────────┐
                                      │    WEB DASHBOARD     │
                                      │     (Streamlit)      │
                                      └──────────────────────┘


6.2 Veri Akış Mimarisi

Normal Akış: OCPP -> Bridge -> Blockchain -> IDS -> CAN

Saldırı Akışı: Attack -> CAN -> IDS (Tespit) -> Blockchain (Alert Log) -> Dashboard

6.3 Tasarım Desenleri

Singleton: Blockchain ve IDS modülleri sistem genelinde tekil çalışır.

Observer: Dashboard, sistemdeki değişiklikleri anlık izler.

Strategy: IDS, duruma göre "Kural Tabanlı" veya "ML Tabanlı" strateji seçer.

7. RİSK ANALİZİ

Risk

Olasılık

Etki

Önlem / Azaltma Stratejisi

CAN-Bus Gecikmesi

Orta

Yüksek

Rate limiting ve mesaj kuyruk yönetimi.

ML Yanlış Pozitif

Orta

Orta

Hibrit yapı (ML kararlarının kural setiyle doğrulanması).

Platform Sorunu

Yüksek

Düşük

Windows için sanal CAN (virtual channel) desteği.

Senaryo Entegrasyonu

Orta

Orta

Modüler yapı sayesinde senaryoların bağımsız eklenebilmesi.

8. YAZILIM MÜHENDİSLİĞİ YAKLAŞIMI

Proje geliştirilirken aşağıdaki temel prensipler benimsenmiştir:

Separation of Concerns (İlgi Alanlarının Ayrımı): Protokol işleme, güvenlik ve arayüz katmanları birbirinden tamamen izole edilmiştir.

Defense in Depth (Derinlemesine Savunma): Tek bir güvenlik önlemi yerine (sadece IDS), çok katmanlı koruma (IDS + Blockchain + İmza) uygulanmıştır.

Immutability (Değişmezlik): Güvenlik loglarının sonradan değiştirilememesi için Blockchain yapısı kullanılmıştır.

Testability (Test Edilebilirlik): Gerçek donanıma ihtiyaç duymadan geliştirme yapılabilmesi için kapsamlı simülatörler yazılmıştır.

9. ARAYÜZLER VE SERVİSLER

9.1 Web Dashboard (Port: 8501)

Key Metrics: Blok sayısı, Alert durumu, Ağ trafiği.

Blockchain Explorer: Zincirin sağlığı, son blok hash'leri ve dijital imza durumu.

Traffic Analysis: CAN ID dağılım grafikleri.

9.2 Komut Satırı (CLI) Araçları

Sistemi test etmek için geliştirilen simülasyon komutları:

# Injection Saldırısı Başlat
python attack_simulator.py --attack injection

# Flood Saldırısı Başlat
python attack_simulator.py --attack ocpp_flood --ocpp-rate 20

# Bridge Sistemini Başlat
python secure_bridge.py
