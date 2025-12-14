"""
BSG Proje Çıktılarını API Server'a Senkronize Etme Yardımcı Modülü
"""
import requests
import time
from typing import Optional, Dict, List
from loguru import logger


class BSGAPISync:
    """BSG proje çıktılarını API server'a senkronize eder"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:8000"):
        self.api_url = api_url
        self.last_sync_time = 0
        self.sync_interval = 5  # 5 saniyede bir senkronize et
    
    def sync_csms_data(self, csms_instance) -> bool:
        """
        CSMS instance'ından verileri alıp API'ye gönder
        
        Args:
            csms_instance: CSMSimulator instance
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            # CSMS'den verileri al
            transactions = []
            charge_points = []
            statistics = {}
            
            if hasattr(csms_instance, 'active_transactions'):
                transactions = csms_instance.active_transactions.copy()
            
            if hasattr(csms_instance, 'connected_charge_points'):
                for cp_id, cp_handler in csms_instance.connected_charge_points.items():
                    charge_points.append({
                        "charge_point_id": cp_id,
                        "connected": True,
                        "is_connected": getattr(cp_handler, 'is_connected', True) if hasattr(cp_handler, 'is_connected') else True
                    })
            
            if hasattr(csms_instance, 'get_statistics'):
                statistics = csms_instance.get_statistics()
            else:
                statistics = {
                    "connected_charge_points": len(csms_instance.connected_charge_points) if hasattr(csms_instance, 'connected_charge_points') else 0,
                    "total_transactions": len(csms_instance.active_transactions) if hasattr(csms_instance, 'active_transactions') else 0,
                    "active_transactions": len([tx for tx in csms_instance.active_transactions if tx.get("active", False)]) if hasattr(csms_instance, 'active_transactions') else 0,
                    "inactive_transactions": 0
                }
                if hasattr(csms_instance, 'active_transactions'):
                    statistics["inactive_transactions"] = statistics["total_transactions"] - statistics["active_transactions"]
            
            # API'ye gönder
            bsg_data = {
                "transactions": transactions,
                "charge_points": charge_points,
                "statistics": statistics
            }
            
            response = requests.post(
                f"{self.api_url}/api/bsg/register",
                json=bsg_data,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.debug(f"✓ BSG verileri API'ye kaydedildi: {len(transactions)} transaction, {len(charge_points)} charge point")
                return True
            else:
                logger.warning(f"BSG verileri kaydedilemedi: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"BSG verileri senkronize edilirken hata: {e}")
            return False
    
    def auto_sync(self, csms_instance, interval: Optional[float] = None):
        """
        Belirli aralıklarla otomatik senkronize et
        
        Args:
            csms_instance: CSMSimulator instance
            interval: Senkronizasyon aralığı (saniye), None ise self.sync_interval kullanılır
        """
        current_time = time.time()
        sync_interval = interval or self.sync_interval
        
        if current_time - self.last_sync_time >= sync_interval:
            self.sync_csms_data(csms_instance)
            self.last_sync_time = current_time


def register_csms_to_api(csms_instance, api_url: str = "http://127.0.0.1:8000"):
    """
    CSMS instance'ını API server'a kaydet (global state'e ekle)
    
    Args:
        csms_instance: CSMSimulator instance
        api_url: API server URL'i
    """
    try:
        # API server'a CSMS instance'ını kaydetmek için bir endpoint çağır
        # Not: Bu endpoint'i api_server.py'ye eklememiz gerekebilir
        # Şimdilik sadece verileri senkronize ediyoruz
        sync = BSGAPISync(api_url)
        sync.sync_csms_data(csms_instance)
        logger.info("CSMS instance API'ye kaydedildi")
    except Exception as e:
        logger.error(f"CSMS instance kaydedilirken hata: {e}")
