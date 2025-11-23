"""
FastAPI Server - Dashboard için REST API ve WebSocket
"""
import asyncio
import time
from typing import List, Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger
import os
from dotenv import load_dotenv

# Internal modules
from utils.blockchain import Blockchain
from utils.ids import RuleBasedIDS
from utils.ml_ids import MLBasedIDS, SKLEARN_AVAILABLE


load_dotenv()


# Pydantic models
class BlockchainStats(BaseModel):
    total_blocks: int
    is_valid: bool
    block_types: Dict[str, int]


class IDSStats(BaseModel):
    total_ocpp_messages: int
    total_can_frames: int
    authorized_can_frames: int
    unauthorized_can_frames: int
    total_alerts: int
    alert_breakdown: Dict[str, int]


class AlertModel(BaseModel):
    alert_id: str
    timestamp: float
    timestamp_iso: str
    severity: str
    alert_type: str
    description: str
    source: str


# FastAPI app
app = FastAPI(
    title="Secure OCPP-CAN Bridge API",
    description="API for monitoring OCPP-to-CAN bridge with blockchain security",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global state (Bridge service tarafından doldurulacak)
class GlobalState:
    blockchain: Optional[Blockchain] = None
    ids: Optional[RuleBasedIDS] = None
    ml_ids: Optional[MLBasedIDS] = None
    websocket_clients: List[WebSocket] = []
    event_queue: asyncio.Queue = asyncio.Queue()
    bridge_active: bool = False
    bridge_stats: Optional[dict] = None


state = GlobalState()


# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client bağlandı. Toplam: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket client ayrıldı. Kalan: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Tüm bağlı client'lara mesaj gönder"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"WebSocket broadcast hatası: {e}")


manager = ConnectionManager()


# REST Endpoints

@app.get("/")
async def root():
    """API bilgisi"""
    return {
        "service": "Secure OCPP-CAN Bridge API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "blockchain": "/api/blockchain",
            "ids": "/api/ids",
            "alerts": "/api/alerts",
            "stats": "/api/stats",
            "websocket": "/ws"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {
            "blockchain": state.blockchain is not None or (state.bridge_active and state.bridge_stats and "blockchain" in state.bridge_stats),
            "ids": state.ids is not None or (state.bridge_active and state.bridge_stats and "ids" in state.bridge_stats),
            "ml_ids": (state.ml_ids is not None and state.ml_ids.is_trained) or (state.bridge_active and state.bridge_stats and "ml" in state.bridge_stats),
            "bridge": state.bridge_active
        }
    }


@app.get("/api/blockchain/stats")
async def get_blockchain_stats():
    """Blockchain istatistikleri"""
    # Bridge'den gelen stats varsa onu kullan
    if state.bridge_active and state.bridge_stats and "blockchain" in state.bridge_stats:
        return state.bridge_stats["blockchain"]
    
    if not state.blockchain:
        return JSONResponse({"error": "Blockchain not initialized"}, status_code=503)
    
    return state.blockchain.get_chain_stats()


@app.get("/api/blockchain/blocks")
async def get_blockchain_blocks(count: int = 10):
    """Son N bloğu getir"""
    # Bridge'den gelen blocks varsa onları kullan
    if state.bridge_active and state.bridge_stats and "blockchain" in state.bridge_stats:
        blockchain_stats = state.bridge_stats["blockchain"]
        if "recent_blocks" in blockchain_stats:
            blocks = blockchain_stats["recent_blocks"][:count]
            return blocks
        else:
            # Bridge aktif ama recent_blocks yok, boş liste döndür
            return []
    
    # Yoksa mevcut state'den oku
    if not state.blockchain:
        # Bridge aktif değilse 503 döndür
        if not state.bridge_active:
            return JSONResponse({"error": "Blockchain not initialized"}, status_code=503)
        # Bridge aktif ama state yok, boş liste döndür
        return []
    
    blocks = state.blockchain.get_recent_blocks(count)
    return [block.to_dict() for block in blocks]


@app.get("/api/blockchain/blocks/{block_index}")
async def get_block(block_index: int):
    """Belirli bir bloğu getir"""
    if not state.blockchain:
        return JSONResponse({"error": "Blockchain not initialized"}, status_code=503)
    
    block = state.blockchain.get_block(block_index)
    if not block:
        return JSONResponse({"error": "Block not found"}, status_code=404)
    
    return block.to_dict()


@app.get("/api/blockchain/blocks/type/{block_type}")
async def get_blocks_by_type(block_type: str):
    """Belirli bir tipteki blokları getir"""
    if not state.blockchain:
        return JSONResponse({"error": "Blockchain not initialized"}, status_code=503)
    
    blocks = state.blockchain.get_blocks_by_type(block_type)
    return [block.to_dict() for block in blocks]


@app.get("/api/ids/stats")
async def get_ids_stats():
    """IDS istatistikleri"""
    # Bridge'den gelen stats varsa onu kullan
    if state.bridge_active and state.bridge_stats and "ids" in state.bridge_stats:
        return state.bridge_stats["ids"]
    
    if not state.ids:
        return JSONResponse({"error": "IDS not initialized"}, status_code=503)
    
    return state.ids.get_stats()


@app.get("/api/alerts")
async def get_alerts(count: int = 20, severity: Optional[str] = None):
    """Alert'leri getir"""
    # Bridge'den gelen alerts varsa onları kullan
    if state.bridge_active and state.bridge_stats and "ids" in state.bridge_stats:
        ids_stats = state.bridge_stats["ids"]
        if "recent_alerts" in ids_stats:
            alerts = ids_stats["recent_alerts"][:count]
            # Severity filtresi
            if severity:
                alerts = [a for a in alerts if a.get("severity") == severity]
            return alerts
        else:
            # Bridge aktif ama recent_alerts yok, boş liste döndür
            return []
    
    # Yoksa mevcut state'den oku
    if not state.ids:
        # Bridge aktif değilse 503 döndür
        if not state.bridge_active:
            return JSONResponse({"error": "IDS not initialized"}, status_code=503)
        # Bridge aktif ama state yok, boş liste döndür
        return []
    
    if severity:
        alerts = state.ids.get_alerts_by_severity(severity)
    else:
        alerts = state.ids.get_recent_alerts(count)
    
    return [alert.to_dict() for alert in alerts]


@app.get("/api/stats")
async def get_all_stats():
    """Tüm istatistikler"""
    stats = {}
    
    # Bridge'den gelen stats varsa onları kullan
    if state.bridge_active and state.bridge_stats:
        stats = state.bridge_stats
    else:
        # Yoksa mevcut state'den oku
        if state.blockchain:
            stats["blockchain"] = state.blockchain.get_chain_stats()
        
        if state.ids:
            stats["ids"] = state.ids.get_stats()
        
        if state.ml_ids:
            stats["ml"] = {
                "is_trained": state.ml_ids.is_trained,
                "training_samples": len(state.ml_ids.training_buffer),
                "contamination": state.ml_ids.contamination
            }
    
    return stats


@app.post("/api/bridge/register")
async def register_bridge(bridge_stats: dict):
    """
    Bridge'in state'ini API server'a kaydet.
    Bridge başlatıldığında bu endpoint'e stats gönderir.
    """
    # Bridge'in state'ini cache'le (basit yaklaşım)
    state.bridge_stats = bridge_stats
    state.bridge_active = True
    logger.info("Bridge state API'ye kaydedildi")
    return {"status": "registered", "timestamp": time.time()}


@app.get("/api/bridge/status")
async def get_bridge_status():
    """Bridge durumunu getir"""
    return {
        "active": state.bridge_active,
        "stats": getattr(state, 'bridge_stats', None),
        "timestamp": time.time()
    }


@app.get("/api/ml/train")
async def train_ml_model():
    """ML modelini eğit"""
    if not state.ml_ids:
        return JSONResponse({"error": "ML-IDS not available"}, status_code=503)
    
    if not SKLEARN_AVAILABLE:
        return JSONResponse({"error": "sklearn not installed"}, status_code=503)
    
    logger.info("ML model eğitimi başlatılıyor...")
    success = state.ml_ids.train(min_samples=100)
    
    if success:
        return {
            "status": "success",
            "message": "Model başarıyla eğitildi",
            "training_samples": len(state.ml_ids.training_buffer)
        }
    else:
        return JSONResponse({
            "status": "failed",
            "message": "Model eğitimi başarısız",
            "training_samples": len(state.ml_ids.training_buffer)
        }, status_code=400)


@app.post("/api/ml/save")
async def save_ml_model(path: str = "./models/isolation_forest.pkl"):
    """ML modelini kaydet"""
    if not state.ml_ids:
        return JSONResponse({"error": "ML-IDS not available"}, status_code=503)
    
    success = state.ml_ids.save_model(path)
    
    if success:
        return {"status": "success", "path": path}
    else:
        return JSONResponse({"status": "failed"}, status_code=400)


# WebSocket endpoint (Real-time updates)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint - Real-time event stream
    
    Message format:
    {
        "type": "alert" | "ocpp_message" | "can_frame" | "blockchain_update",
        "data": {...},
        "timestamp": float
    }
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Client'tan mesaj bekle (keep-alive için)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                # Ping-pong
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Timeout normal, devam et
                pass
            
            # Event queue'den mesaj var mı kontrol et
            try:
                event = state.event_queue.get_nowait()
                await manager.broadcast(event)
            except asyncio.QueueEmpty:
                pass
            
            await asyncio.sleep(0.1)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket hatası: {e}")
        manager.disconnect(websocket)


# Background task: Event broadcaster

async def event_broadcaster():
    """Bridge'den gelen event'leri WebSocket'e broadcast et"""
    while True:
        try:
            event = await state.event_queue.get()
            await manager.broadcast(event)
        except Exception as e:
            logger.error(f"Event broadcast hatası: {e}")
        
        await asyncio.sleep(0.01)


# Startup/Shutdown events

@app.on_event("startup")
async def startup_event():
    """API başlangıç"""
    logger.info("FastAPI server başlatıldı")
    
    # Event broadcaster'ı başlat
    asyncio.create_task(event_broadcaster())


@app.on_event("shutdown")
async def shutdown_event():
    """API kapatılıyor"""
    logger.info("FastAPI server kapatılıyor")


# Helper function: Bridge'den veri al

def inject_bridge_state(blockchain, ids, ml_ids, event_queue):
    """
    Bridge service tarafından çağrılır.
    Global state'i doldurur.
    """
    state.blockchain = blockchain
    state.ids = ids
    state.ml_ids = ml_ids
    state.event_queue = event_queue
    logger.info("Bridge state API'ye enjekte edildi")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    logger.info(f"API Server başlatılıyor: http://{host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

