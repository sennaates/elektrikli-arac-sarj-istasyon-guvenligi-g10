#!/usr/bin/env python3
"""
API Server'ı test et ve başlat
"""
import sys
import os

# Proje root'unu path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api_server import app
    import uvicorn
    
    print("✅ API Server modülleri yüklendi")
    print(f"✅ FastAPI app: {app}")
    
    # Test başlatma
    print("\n🚀 API Server başlatılıyor...")
    print("   Port: 8000")
    print("   URL: http://localhost:8000")
    print("\n⚠️  Ctrl+C ile durdurun\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ Import hatası: {e}")
    print("\nBağımlılıkları kontrol edin:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

