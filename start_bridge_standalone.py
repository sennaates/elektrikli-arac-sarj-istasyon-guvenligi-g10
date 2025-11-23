#!/usr/bin/env python3
"""
Bridge'i standalone modda başlat (CSMS olmadan)
Sadece CAN-Bus dinleme ve IDS çalışır.
"""
import asyncio
import sys
import os
from loguru import logger

# Proje root'unu path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from secure_bridge import SecureBridgeService

async def main():
    """Standalone modda bridge başlat"""
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | <level>{message}</level>"
    )
    
    # Bridge'i başlat
    bridge = SecureBridgeService()
    
    # CSMS URL'ini None yap (standalone mod)
    bridge.csms_url = None
    
    try:
        # Standalone modda başlat
        logger.info("="*60)
        logger.info("BRIDGE STANDALONE MODDA BAŞLATILIYOR")
        logger.info("="*60)
        logger.info("CSMS bağlantısı atlanıyor, sadece CAN dinleme aktif")
        logger.info("")
        
        # CAN handler'ı bağla
        if not bridge.can_handler.connect():
            logger.error("CAN Bus'a bağlanılamadı!")
            return
        
        logger.info(f"✓ CAN Bus'a bağlanıldı: {bridge.can_handler.interface}")
        logger.info("")
        
        # Standalone CAN modunu direkt çağır
        await bridge._standalone_can_mode()
        
    except KeyboardInterrupt:
        logger.info("\n⚠ Ctrl+C algılandı")
    finally:
        bridge.shutdown()

if __name__ == "__main__":
    asyncio.run(main())

