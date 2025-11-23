"""
Hafif Blockchain Modülü - CAN-Bus Güvenliği İçin
Her OCPP komutu ve CAN frame'i blok zincirine kaydedilir.
"""
import hashlib
import time
import json
from typing import Dict, List, Optional, Any
from ecdsa import SigningKey, SECP256k1, BadSignatureError
from loguru import logger


class Block:
    """Blockchain'deki tek bir blok"""
    
    def __init__(
        self,
        index: int,
        timestamp: float,
        data: Dict[str, Any],
        previous_hash: str,
        signature: Optional[str] = None
    ):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.signature = signature
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Bloğun SHA-256 hash'ini hesapla"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "signature": self.signature
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Bloğu dictionary formatına çevir"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "signature": self.signature
        }
    
    def __repr__(self) -> str:
        return f"Block(#{self.index}, hash={self.hash[:8]}...)"


class Blockchain:
    """
    Tamper-Evident Logging için hafif blockchain implementasyonu.
    Her OCPP ve CAN mesajı zincire eklenir.
    """
    
    def __init__(self, enable_signature: bool = True):
        self.chain: List[Block] = []
        self.enable_signature = enable_signature
        
        # Dijital imza için ECDSA private/public key pair
        if enable_signature:
            self.private_key = SigningKey.generate(curve=SECP256k1)
            self.public_key = self.private_key.get_verifying_key()
        else:
            self.private_key = None
            self.public_key = None
        
        # Genesis block oluştur
        self._create_genesis_block()
        logger.info(f"Blockchain başlatıldı. Genesis hash: {self.chain[0].hash[:16]}...")
    
    def _create_genesis_block(self) -> None:
        """İlk bloğu (Genesis) oluştur"""
        genesis_data = {
            "type": "GENESIS",
            "message": "Secure OCPP-CAN Bridge Initialized",
            "version": "1.0"
        }
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            data=genesis_data,
            previous_hash="0" * 64,
            signature=None
        )
        self.chain.append(genesis_block)
    
    def add_block(self, data: Dict[str, Any], block_type: str = "TRANSACTION") -> Block:
        """
        Zincire yeni blok ekle
        
        Args:
            data: Blokta saklanacak veri (OCPP komutu, CAN frame vb.)
            block_type: Blok tipi (OCPP, CAN, ALERT, IDS)
        
        Returns:
            Eklenen blok
        """
        previous_block = self.chain[-1]
        
        # Data'ya tip bilgisi ekle
        enriched_data = {
            "type": block_type,
            "payload": data,
            "timestamp_iso": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        
        # Yeni blok oluştur
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=enriched_data,
            previous_hash=previous_block.hash,
            signature=self._sign_block(enriched_data) if self.enable_signature else None
        )
        
        self.chain.append(new_block)
        logger.debug(f"Yeni blok eklendi: #{new_block.index} ({block_type})")
        
        return new_block
    
    def _sign_block(self, data: Dict[str, Any]) -> str:
        """Blok verisini ECDSA ile imzala"""
        if not self.private_key:
            return ""
        
        data_string = json.dumps(data, sort_keys=True).encode()
        signature = self.private_key.sign(data_string)
        return signature.hex()
    
    def verify_signature(self, block: Block) -> bool:
        """Bloğun dijital imzasını doğrula"""
        if not self.enable_signature or not block.signature:
            return True  # İmza devre dışıysa her zaman True
        
        try:
            data_string = json.dumps(block.data, sort_keys=True).encode()
            signature_bytes = bytes.fromhex(block.signature)
            self.public_key.verify(signature_bytes, data_string)
            return True
        except BadSignatureError:
            logger.error(f"Blok #{block.index} imza doğrulaması başarısız!")
            return False
        except Exception as e:
            logger.error(f"İmza doğrulama hatası: {e}")
            return False
    
    def is_chain_valid(self) -> bool:
        """
        Tüm zinciri doğrula:
        1. Her bloğun hash'i doğru mu?
        2. Önceki hash'ler tutarlı mı?
        3. İmzalar geçerli mi?
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Hash doğrulama
            if current_block.hash != current_block.calculate_hash():
                logger.error(f"Blok #{i} hash'i geçersiz!")
                return False
            
            # Önceki hash tutarlılığı
            if current_block.previous_hash != previous_block.hash:
                logger.error(f"Blok #{i} önceki hash tutarsızlığı!")
                return False
            
            # İmza doğrulama
            if not self.verify_signature(current_block):
                return False
        
        logger.info("✓ Blockchain bütünlüğü doğrulandı")
        return True
    
    def get_latest_block(self) -> Block:
        """En son bloğu getir"""
        return self.chain[-1]
    
    def get_block(self, index: int) -> Optional[Block]:
        """Belirli bir index'teki bloğu getir"""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def get_blocks_by_type(self, block_type: str) -> List[Block]:
        """Belirli bir tipteki tüm blokları getir"""
        return [
            block for block in self.chain
            if block.data.get("type") == block_type
        ]
    
    def get_recent_blocks(self, count: int = 10) -> List[Block]:
        """Son N bloğu getir"""
        return self.chain[-count:] if len(self.chain) >= count else self.chain
    
    def export_chain(self) -> List[Dict[str, Any]]:
        """Tüm zinciri JSON formatında dışa aktar"""
        return [block.to_dict() for block in self.chain]
    
    def get_chain_stats(self) -> Dict[str, Any]:
        """Blockchain istatistikleri"""
        block_types = {}
        for block in self.chain[1:]:  # Genesis hariç
            block_type = block.data.get("type", "UNKNOWN")
            block_types[block_type] = block_types.get(block_type, 0) + 1
        
        return {
            "total_blocks": len(self.chain),
            "genesis_hash": self.chain[0].hash,
            "latest_hash": self.chain[-1].hash,
            "is_valid": self.is_chain_valid(),
            "block_types": block_types,
            "signature_enabled": self.enable_signature
        }
    
    def __len__(self) -> int:
        return len(self.chain)
    
    def __repr__(self) -> str:
        return f"Blockchain(blocks={len(self.chain)}, valid={self.is_chain_valid()})"


if __name__ == "__main__":
    # Test
    logger.info("Blockchain modülü test ediliyor...")
    
    bc = Blockchain(enable_signature=True)
    
    # OCPP mesajı ekle
    bc.add_block({
        "action": "RemoteStartTransaction",
        "connector_id": 1,
        "id_tag": "USER_001"
    }, block_type="OCPP")
    
    # CAN frame ekle
    bc.add_block({
        "can_id": "0x200",
        "data": [0x01, 0x02, 0x03, 0x04],
        "dlc": 4
    }, block_type="CAN")
    
    # IDS alert ekle
    bc.add_block({
        "alert_type": "UNAUTHORIZED_INJECTION",
        "can_id": "0x9FF",
        "severity": "HIGH"
    }, block_type="ALERT")
    
    print("\n" + "="*50)
    print("BLOCKCHAIN İSTATİSTİKLERİ:")
    print("="*50)
    stats = bc.get_chain_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n" + "="*50)
    print("SON 3 BLOK:")
    print("="*50)
    for block in bc.get_recent_blocks(3):
        print(f"\n{block}")
        print(f"  Timestamp: {time.ctime(block.timestamp)}")
        print(f"  Data: {block.data}")
        print(f"  Hash: {block.hash[:32]}...")

