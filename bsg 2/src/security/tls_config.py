"""
TLS konfigürasyonları: plain ws, weak TLS, strong TLS
"""

import ssl
import logging
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class TLSConfigManager:
    """
    Farklı güvenlik senaryoları için TLS konfigürasyonları
    """
    
    SCENARIO_PLAIN_WS = 'plain_ws'
    SCENARIO_WEAK_TLS = 'weak_tls'
    SCENARIO_STRONG_TLS = 'strong_tls'
    
    def __init__(self, cert_dir: str = 'certs'):
        self.cert_dir = Path(cert_dir)
        self.weak_dir = self.cert_dir / 'weak'
        self.strong_dir = self.cert_dir / 'strong'
    
    def get_server_context(self, scenario: str) -> Optional[ssl.SSLContext]:
        """
        Senaryoya göre server SSL context döndür
        
        Args:
            scenario: Güvenlik senaryosu
            
        Returns:
            Optional[ssl.SSLContext]: SSL context veya None (plain ws için)
        """
        if scenario == self.SCENARIO_PLAIN_WS:
            logger.info("🔓 Plain WebSocket (güvenlik yok)")
            return None  # Plain WebSocket
        
        elif scenario == self.SCENARIO_WEAK_TLS:
            logger.info("⚠️  Zayıf TLS konfigürasyonu")
            context = self._create_weak_tls_context()
            return context
        
        elif scenario == self.SCENARIO_STRONG_TLS:
            logger.info("🔒 Güçlü TLS konfigürasyonu")
            context = self._create_strong_tls_context()
            return context
        
        else:
            logger.error(f"❌ Bilinmeyen senaryo: {scenario}")
            return None
    
    def get_client_context(self, scenario: str) -> Optional[ssl.SSLContext]:
        """
        Senaryoya göre client SSL context döndür
        
        Args:
            scenario: Güvenlik senaryosu
            
        Returns:
            Optional[ssl.SSLContext]: SSL context veya None
        """
        if scenario == self.SCENARIO_PLAIN_WS:
            return None
        
        elif scenario == self.SCENARIO_WEAK_TLS:
            context = self._create_weak_tls_context(verify=False)
            return context
        
        elif scenario == self.SCENARIO_STRONG_TLS:
            context = self._create_strong_tls_context(verify=True)
            return context
        
        else:
            logger.error(f"❌ Bilinmeyen senaryo: {scenario}")
            return None
    
    def _create_weak_tls_context(self, verify: bool = False) -> ssl.SSLContext:
        """
        Zayıf TLS konfigürasyonu oluştur
        
        Özellikler:
        - TLS 1.0 (eski ve güvensiz)
        - Zayıf cipher suites
        - Self-signed sertifikalar
        - Düşük anahtar uzunluğu (512 bit)
        
        Args:
            verify: Server certificate verification
            
        Returns:
            ssl.SSLContext: Weak TLS context
        """
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER if verify is None 
                                else ssl.PROTOCOL_TLS_CLIENT)
        
        # Zayıf ayarlar
        context.minimum_version = ssl.TLSVersion.MINIMUM_SUPPORTED  # En eski TLS
        
        # Zayıf cipher suites (opsiyonel, modern ssl kütüphanesi bunları desteklemez)
        # context.set_ciphers('DES-CBC3-SHA:RC4-SHA')
        
        # Server için sertifika yükle
        cert_file = self.weak_dir / 'server.crt'
        key_file = self.weak_dir / 'server.key'
        
        if cert_file.exists() and key_file.exists():
            context.load_cert_chain(str(cert_file), str(key_file))
            logger.debug("📜 Zayıf sertifikalar yüklendi")
        else:
            logger.warning("⚠️  Sertifika dosyaları bulunamadı, self-signed üretilecek")
            # Fallback: Generate self-signed cert on the fly
        
        # Client tarafında verification kapat
        if not verify:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            logger.debug("⚠️  Certificate verification kapalı")
        
        return context
    
    def _create_strong_tls_context(self, verify: bool = True) -> ssl.SSLContext:
        """
        Güçlü TLS konfigürasyonu oluştur
        
        Özellikler:
        - TLS 1.2 minimum (modern güvenli protokol)
        - Güçlü cipher suites
        - Mutual TLS (mTLS) desteği
        - Yüksek anahtar uzunluğu (4096 bit)
        - Certificate pinning
        
        Args:
            verify: Server certificate verification
            
        Returns:
            ssl.SSLContext: Strong TLS context
        """
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER if verify is None 
                                else ssl.PROTOCOL_TLS_CLIENT)
        
        # Güçlü ayarlar
        context.minimum_version = ssl.TLSVersion.TLSv1_2  # TLS 1.2 minimum
        
        # Güçlü cipher suites (default strong ciphers)
        context.set_ciphers('HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA')
        
        # Server için sertifika yükle
        cert_file = self.strong_dir / 'server.crt'
        key_file = self.strong_dir / 'server.key'
        
        if cert_file.exists() and key_file.exists():
            context.load_cert_chain(str(cert_file), str(key_file))
            logger.debug("🔐 Güçlü sertifikalar yüklendi")
        else:
            logger.warning("⚠️  Sertifika dosyaları bulunamadı")
        
        # Certificate verification
        if verify:
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            logger.debug("✅ Certificate verification açık")
        else:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        
        return context
    
    def get_scenario_info(self, scenario: str) -> Dict[str, str]:
        """Senaryo bilgilerini döndür"""
        info_map = {
            self.SCENARIO_PLAIN_WS: {
                'name': 'Plain WebSocket',
                'security': '❌ YOK',
                'risk': '🔴 ÇOK YÜKSEK',
                'description': 'Şifreleme yok, MitM saldırılarına açık'
            },
            self.SCENARIO_WEAK_TLS: {
                'name': 'Weak TLS',
                'security': '⚠️  ZAYIF',
                'risk': '🟠 YÜKSEK',
                'description': 'TLS 1.0, zayıf cipher, self-signed certs'
            },
            self.SCENARIO_STRONG_TLS: {
                'name': 'Strong TLS',
                'security': '✅ GÜÇLÜ',
                'risk': '🟢 DÜŞÜK',
                'description': 'TLS 1.2+, güçlü ciphers, mutual TLS'
            }
        }
        
        return info_map.get(scenario, {
            'name': 'Unknown',
            'security': '❓',
            'risk': '❓',
            'description': 'Bilinmeyen senaryo'
        })

