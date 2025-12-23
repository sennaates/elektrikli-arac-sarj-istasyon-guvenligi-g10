# 📤 Senaryonuzu Nasıl Eklersiniz?

## 🎯 Senaryo Gönderme Rehberi

Bu belge, arkadaşlarınızın hazırladığı anomali senaryolarını projeye nasıl ekleyeceklerini açıklar.

---

## ✅ Senaryo Gereksinimleri

### **Format Kuralları**

1. **Dosya Adı**: `tests/scenario_<isim>.py`
   - Örnek: `tests/scenario_energy_manipulation.py`
   - Örnek: `tests/scenario_timing_attack.py`

2. **Test Fonksiyonu**: `test_` ile başlamalı
   ```python
   @pytest.mark.asyncio
   async def test_energy_manipulation():
       """Enerji manipülasyonu saldırısı"""
       # ...
   ```

3. **Port Yönetimi**: Her senaryo farklı port kullanmalı
   ```python
   # Senaryo 1: port=9020
   # Senaryo 2: port=9021
   # Senaryo 3: port=9022
   # ...
   ```

### **Zorunlu Özellikler**

✅ **Setup**: CSMS ve CP doğru başlatılmalı  
✅ **Cleanup**: `await cp.stop()` ve `await csms.stop()` çağrılmalı  
✅ **Assertions**: En az 1 assertion olmalı  
✅ **Açıklayıcı Loglar**: Senaryo ne yapıyor anlaşılmalı  
✅ **Yorumlar**: Kod anlaşılır şekilde yorumlanmalı  
✅ **Senaryo Adı**: Açıklayıcı bir isim  

---

## 📝 Senaryo Şablonu

```python
"""
<ARKADAŞINIZIN ADI>: <SENARYO ADI>

<SENARYO AÇIKLAMASI: Saldırının ne yaptığı, nasıl tespit edileceği, vs.>

Örnek:
Saldırgan MitM ile enerji değerlerini manipüle ederek faturalamayı 
düşürüyor. IDS bu anormal değerleri tespit etmeli.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ocpp.central_system.simulator import CSMSimulator
from src.ocpp.charge_point.simulator import ChargePointSimulator
from src.detection.can_ids import CANIntrusionDetector
from src.can_bus.can_simulator import CANMessage

@pytest.mark.asyncio
async def test_<isim>():

@pytest.mark.asyncio
async def test_<senaryo_adı>():
    """
    <SENARYO AÇIKLAMASI>
    
    Beklenen Sonuç:
    - ...
    - ...
    """
    print("\n" + "="*80)
    print("<BÜYÜK HARF SENARYO ADI>")
    print("="*80)
    
    # ==========================================
    # ADIM 1: SETUP
    # ==========================================
    
    csms = CSMSimulator(host='localhost', port=90XX, scenario='plain_ws')
    csms_task = asyncio.create_task(csms.start())
    await asyncio.sleep(2)
    
    try:
        cp = ChargePointSimulator(
            cp_id='CP_<UNIQUE_ID>',
            scenario='plain_ws',
            csms_url='ws://localhost:90XX/charge_point/cp_<unique_id>'
        )
        cp_task = asyncio.create_task(cp.start())
        await asyncio.sleep(3)
        
        # IDS veya diğer bileşenler
        ids = CANIntrusionDetector()
        
        # ==========================================
        # ADIM 2: SENARYO
        # ==========================================
        
        # Buraya arkadaşınızın senaryosunu yazın
        # Örn:
        # await csms.send_remote_start('cp_<id>', connector_id=1)
        # ...
        # Saldırı kodu
        # ...
        
        # ==========================================
        # ADIM 3: DOĞRULAMA
        # ==========================================
        
        stats = csms.get_stats()
        print(f"📊 Stats: {stats}")
        
        # Assertions
        assert stats['gateway_stats']['ocpp_to_can'] >= 1
        # Daha fazla assertion...
        
        print("✅ Senaryo başarılı!")
        
    finally:
        # ==========================================
        # ADIM 4: CLEANUP
        # ==========================================
        
        await cp.stop()
        await csms.stop()
        await asyncio.sleep(0.5)
```

---

## 🔍 Senaryo Kontrol Listesi

Senaryonuzu göndermeden önce kontrol edin:

- [ ] Dosya adı `scenario_<isim>.py` formatında
- [ ] Test fonksiyonu `test_` ile başlıyor
- [ ] Port numarası başka senaryolarla çakışmıyor
- [ ] `await cp.stop()` ve `await csms.stop()` çağrılıyor
- [ ] En az 1 assertion var
- [ ] Loglar anlamlı
- [ ] Kodu yorumlandı
- [ ] `pytest tests/scenario_<isim>.py -v` geçiyor
- [ ] Dosya başında ad ve açıklama var

---

## 📤 Senaryoyu Nasıl Gönderirsiniz?

### **Yöntem 1: Pull Request (Önerilen)**

```bash
# 1. Fork edin veya branch oluşturun
git checkout -b feature/add-scenario-<isim>

# 2. Senaryonuzu ekleyin
cp <hazırladığınız_dosya.py> tests/scenario_<isim>.py

# 3. Commit edin
git add tests/scenario_<isim>.py
git commit -m "Add scenario: <isim> by <ad>"

# 4. Push edin
git push origin feature/add-scenario-<isim>

# 5. Pull Request açın
```

### **Yöntem 2: Manuel Ekleme**

```bash
# 1. Senaryonuzu proje klasörüne kopyalayın
cp <hazırladığınız_dosya.py> tests/scenario_<isim>.py

# 2. Test edin
pytest tests/scenario_<isim>.py -v -s

# 3. Git'e ekleyin
git add tests/scenario_<isim>.py
git commit -m "Add scenario: <isim>"
git push
```

### **Yöntem 3: Direct Upload**

Eğer Git bilmiyorsanız, senaryo dosyanızı:
1. WhatsApp/Discord/Email ile gönderin
2. Proje sahibi ekleyecek
3. Tüm ekleme kredisi sizin olacak

---

## ✅ Senaryo Onay Süreci

1. **Otomatik Test**: `pytest tests/scenario_<isim>.py` geçmeli
2. **Lint Kontrolü**: Kod kalitesi kontrol edilir
3. **İçerik Kontrolü**: Senaryo anlamlı ve öğretici olmalı
4. **Dokümantasyon**: Yorumlar açıklayıcı olmalı

**Onaylanan senaryolar:**
- `tests/` klasörüne eklenir
- Test suite'e eklenir
- Dokümantasyonda bahsedilir
- **Yazar adı korunur** 🎉

---

## 🏆 Ödüller & Tanınma

En iyi senaryolar:

- ⭐ **En Yaratıcı Senaryo**: En yenilikçi yaklaşım
- ⭐ **En İyi Dokümante**: En iyi yorumlanan kod
- ⭐ **En Eğitici**: Öğrenme değeri en yüksek
- ⭐ **Community Award**: En popüler senaryo

**Senaryolar otomatik olarak README'de listelenir:**

```markdown
## 🤝 Community Scenarios

- `scenario_energy_manipulation.py` - by @AliYilmaz - Enerji manipülasyonu
- `scenario_timing_attack.py` - by @AyseDemir - Zamanlama saldırısı
- ...
```

---

## 📞 Sorularınız mı Var?

- **Teknik sorular**: GitHub Issues
- **Senaryo fikirleri**: GitHub Discussions
- **Görüşler**: Proje sahibine ulaşın

---

## 🎉 Başarılar!

Senaryonuzu yazarken:

- ✅ Öğrenmeye odaklanın
- ✅ Eğlenceli olsun
- ✅ Paylaşın!
- ✅ Geri bildirim isteyin

**Her katkı değerlidir!** 🚀

---

**Son Güncelleme**: 2025-11-03

