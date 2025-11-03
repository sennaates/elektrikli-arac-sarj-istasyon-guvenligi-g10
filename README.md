Async10
# 🚗Elektrikli Araç Şarj Sistemlerinde Güvenlik Modeli

## 🔍 Proje Tanımı
Bu proje, **elektrikli araç şarj altyapılarında (EVCS)** kullanılan **OCPP (Open Charge Point Protocol)** iletişimini ve **araç içi CAN veri yolu** etkileşimini simüle ederek, **siber güvenlik açısından anomali tespiti ve analizini** amaçlamaktadır.  

Her ekip üyesi, belirli bir **anomali senaryosu** geliştirip sanal ortamda test edecek, sonuçlarını **SWOT analizi** ve **literatür incelemesi** ile destekleyecektir.  

Proje, akademik amaçlı yürütülmekte olup **gerçek sistemler üzerinde herhangi bir test yapılmamaktadır**. Tüm deneyler, güvenli sanal ağlarda (`vcan0`, `localhost`, Python tabanlı simülasyon ortamı) gerçekleştirilir.

---

## ⚙️ Öne Çıkan İşlevler
- **OCPP iletişim simülasyonu:** CSMS ↔ CP ↔ EMS arasındaki veri akışının modellenmesi  
- **CAN veri yolu trafiği oluşturma:** `python-can` ve `vcan0` ile sanal araç verisi üretimi  
- **Anomali senaryoları geliştirme:** Her ekip üyesi tarafından özgün saldırı veya bozulma senaryosu hazırlanması  
- **Loglama ve analiz:** Deney verilerinin toplanması, temizlenmesi ve istatistiksel anomali tespiti  
- **SWOT analizi:** Her senaryonun güçlü ve zayıf yönlerinin, fırsat ve tehditlerinin değerlendirilmesi  
- **Literatür taraması:** Güncel akademik çalışmaların incelenmesi ve projeye entegre edilmesi  

---

## 🧰 Kullanılan Diller, Frameworkler ve Araçlar

| Katman | Teknolojiler |
|--------|---------------|
| **Programlama Dili** | Python 3.10+ |
| **Simülasyon & Haberleşme** | `websockets`, `ocpp`, `python-can`, `socket`, `asyncio` |
| **Veri Analizi & Görselleştirme** | `pandas`, `numpy`, `matplotlib`, `jupyter` |
| **Ortam & Test** | `vcan0` (Virtual CAN Interface), `pytest` |
| **Sürüm Kontrol** | Git & GitHub |
| **Dokümantasyon** | Markdown (`README.md`), PDF (rapor çıktıları) |

---

## 👥 Ekip Arkadaşları

- Sude Demir  
- Sudem Cücemen  
- Sena Ateş  
- Enes Malik  
- Uğur Berktaş  
- İbrahim Kerem Güven  
- Semih Tepe  
- Özgün Deniz Sevilmiş  
- Şerif Bayram  
- Oğuzhan Erdoğan  
- Selanur Ayaz  

---

## 📘 Proje Amacı
Bu çalışma, **araç içi ağ güvenliğini artırmak**, **blokzincir tabanlı doğrulama mekanizmalarını araştırmak** ve **akıllı ulaşım sistemleri** için güvenli bir veri iletişim altyapısı tasarlamak amacıyla yürütülmektedir.  

Her öğrencinin geliştireceği anomali senaryosu, gelecekteki otonom ve bağlantılı araç güvenliği çözümlerine katkı sağlamayı hedeflemektedir.

