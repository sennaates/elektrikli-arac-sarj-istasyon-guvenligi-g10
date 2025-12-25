"""
Intrusion Detection System (IDS) - Rule-Based
CAN-Bus ve OCPP trafiğinde anomali tespiti yapar.
"""
import time
import numpy as np
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
from loguru import logger


@dataclass
class Alert:
    """IDS Alert veri yapısı"""
    alert_id: str
    timestamp: float
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    alert_type: str
    description: str
    source: str  # OCPP, CAN, SYSTEM
    data: Dict
    
    def to_dict(self) -> Dict:
        return {
            "alert_id": self.alert_id,
            "timestamp": self.timestamp,
            "timestamp_iso": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp)),
            "severity": self.severity,
            "alert_type": self.alert_type,
            "description": self.description,
            "source": self.source,
            "data": self.data
        }


@dataclass
class TrafficStats:
    """Trafik istatistikleri"""
    total_ocpp_messages: int = 0
    total_can_frames: int = 0
    authorized_can_frames: int = 0
    unauthorized_can_frames: int = 0
    total_alerts: int = 0
    
    # CAN ID frekans sayacı
    can_id_frequency: Dict[int, int] = field(default_factory=dict)
    
    # OCPP action sayacı
    ocpp_action_frequency: Dict[str, int] = field(default_factory=dict)
    
    # Son aktivite zamanları
    last_ocpp_time: Optional[float] = None
    last_can_time: Optional[float] = None
    
    # Senaryo #2: OCPP mesaj rate tracking
    ocpp_message_timestamps: deque = field(default_factory=lambda: deque(maxlen=1000))
    ocpp_rate_alerts: int = 0
    
    # Senaryo #3: Sampling manipulation tracking
    meter_samples: deque = field(default_factory=lambda: deque(maxlen=1000))  # (timestamp, value)
    samples_per_minute: int = 0
    energy_variance_history: List[float] = field(default_factory=list)
    raw_sample_buffer_size: int = 0
    sent_sample_count: int = 0
    
    # Senaryo #4: Fail-open behavior tracking
    auth_timeout_timestamps: deque = field(default_factory=lambda: deque(maxlen=100))  # Auth timeout zamanları
    auth_success_count: int = 0
    auth_failure_count: int = 0
    consecutive_auth_timeouts: int = 0
    charge_starts_without_auth: int = 0
    last_successful_auth_time: Optional[float] = None
    
    # Senaryo #5: Duplicate Booking tracking
    reservations: Dict[str, Dict] = field(default_factory=dict)  # reservationId -> {connectorId, idTag, timestamp, expiry}
    reservation_ids_used: Set[str] = field(default_factory=set)  # Kullanılmış reservation ID'ler
    connector_reservations: Dict[int, List[str]] = field(default_factory=lambda: defaultdict(list))  # connectorId -> [reservationId]
    reservation_to_transaction: Dict[str, str] = field(default_factory=dict)  # reservationId -> transactionId


class RuleBasedIDS:
    """
    Kural tabanlı saldırı tespit sistemi.
    
    Tespit Kuralları:
    1. Unauthorized CAN Injection: Bridge tarafından gönderilmeyen CAN frame
    2. CAN Flood: Belirli bir sürede çok fazla CAN mesajı
    3. Replay Attack: Aynı mesajın kısa sürede tekrarı
    4. Timing Anomaly: Beklenmeyen zamanlama sapmaları
    5. Invalid CAN ID: İzin listesinde olmayan CAN ID'ler
    """
    
    def __init__(
        self,
        can_flood_threshold: int = 100,  # 1 saniyede max CAN frame
        replay_window: float = 5.0,  # Replay detection penceresi (saniye)
        allowed_can_ids: Optional[Set[int]] = None,
        ocpp_rate_threshold: int = 5,  # Senaryo #2: Max OCPP mesaj/saniye
        ocpp_rate_window: float = 1.0  # Senaryo #2: Rate hesaplama penceresi
    ):
        self.can_flood_threshold = can_flood_threshold
        self.replay_window = replay_window
        self.ocpp_rate_threshold = ocpp_rate_threshold
        self.ocpp_rate_window = ocpp_rate_window
        
        # Senaryo #3: Sampling manipulation thresholds
        self.min_sampling_rate = 30  # Minimum 30 sample/minute
        self.variance_drop_threshold = 0.30  # %30'dan fazla düşüş anomali
        self.buffer_mismatch_ratio = 2.0  # raw/sent > 2x ise şüpheli
        
        # Senaryo #4: Fail-open behavior thresholds
        self.auth_timeout_threshold = 3  # 60 saniyede 3 timeout = şüpheli
        self.auth_timeout_window = 60.0  # saniye
        self.consecutive_timeout_threshold = 5  # 5 ardışık timeout
        self.fail_open_detection_window = 10.0  # saniye (fail-open tespit penceresi)
        
        # Senaryo #5: Duplicate Booking thresholds
        self.duplicate_reservation_window = 60.0  # saniye (çift rezervasyon tespit penceresi)
        self.reservation_reuse_window = 300.0  # saniye (5 dakika - rezervasyon ID tekrar kullanım tespiti)
        
        # İzin verilen CAN ID'ler (whitelist)
        self.allowed_can_ids = allowed_can_ids or {
            0x200, 0x201, 0x202, 0x210, 0x220, 0x230, 0x231, 0x240, 0x300
        }
        
        # Yetkili CAN frame'lerin kaydı (OCPP → CAN mapping sonucu)
        # Key: CAN ID, Value: set of message hashes
        self.authorized_frames: Dict[int, Set[str]] = defaultdict(set)
        
        # Son görülen mesajlar (replay detection için)
        self.recent_messages: deque = deque(maxlen=1000)
        
        # CAN frame zamanlama kuyruğu (flood detection için)
        self.can_timestamps: deque = deque(maxlen=1000)
        
        # Alert listesi
        self.alerts: List[Alert] = []
        
        # İstatistikler
        self.stats = TrafficStats()
        
        # Senaryo #1 için ek tracking
        # K1: Timing mismatch detection
        self.last_ocpp_actions: deque = deque(maxlen=100)  # (timestamp, action)
        
        # K2: Session fingerprint tracking
        self.session_fingerprints: Dict[str, Set[str]] = defaultdict(set)  # idTag -> {IP/fingerprints}
        
        # K3: OCPP-CAN mapping tracking
        self.expected_can_frames: Dict[str, int] = {}  # OCPP action → expected CAN ID
        
        logger.info("Rule-Based IDS başlatıldı")
    
    def register_authorized_can_frame(self, can_id: int, data: List[int]) -> None:
        """
        Bridge tarafından gönderilen (yetkili) CAN frame'i kaydet.
        Bu, OCPP komutu sonucu oluşturulan CAN frame'leri için kullanılır.
        """
        frame_hash = self._hash_frame(can_id, data)
        self.authorized_frames[can_id].add(frame_hash)
        self.stats.authorized_can_frames += 1
        logger.debug(f"Yetkili CAN frame kaydedildi: ID={hex(can_id)}")
    
    def check_can_frame(self, can_id: int, data: List[int], timestamp: float, 
                       expected_ocpp_action: Optional[str] = None) -> Optional[Alert]:
        """
        CAN frame'i kontrol et ve anomali varsa alert üret.
        
        Args:
            expected_ocpp_action: Bu CAN frame'in hangi OCPP action'dan kaynaklanması beklendiği
        
        Returns:
            Alert objesi veya None
        """
        self.stats.total_can_frames += 1
        self.stats.last_can_time = timestamp
        
        # Frekans sayacını güncelle
        self.stats.can_id_frequency[can_id] = self.stats.can_id_frequency.get(can_id, 0) + 1
        
        # K3: OCPP-CAN Mapping Mismatch (Senaryo #1)
        if expected_ocpp_action and expected_ocpp_action in self.expected_can_frames:
            expected_can_id = self.expected_can_frames[expected_ocpp_action]
            
            if can_id != expected_can_id:
                alert = self._create_alert(
                    alert_type="OCPP_CAN_MISMATCH_K3",
                    severity="CRITICAL",
                    description=f"OCPP-CAN mapping uyuşmazlığı: {expected_ocpp_action} için {hex(expected_can_id)} bekleniyor ama {hex(can_id)} geldi",
                    source="CAN",
                    data={
                        "ocpp_action": expected_ocpp_action,
                        "expected_can_id": hex(expected_can_id),
                        "actual_can_id": hex(can_id),
                        "data": [hex(b) for b in data]
                    }
                )
                logger.error(f"🚨 CRITICAL ALERT [K3]: {alert.description}")
                self.stats.unauthorized_can_frames += 1
                return alert
        
        # Kural 1: Unauthorized Injection Check
        frame_hash = self._hash_frame(can_id, data)
        if frame_hash not in self.authorized_frames.get(can_id, set()):
            alert = self._create_alert(
                alert_type="UNAUTHORIZED_CAN_INJECTION",
                severity="HIGH",
                description=f"CAN ID {hex(can_id)} için yetkisiz frame tespit edildi",
                source="CAN",
                data={"can_id": hex(can_id), "data": [hex(b) for b in data]}
            )
            self.stats.unauthorized_can_frames += 1
            logger.warning(f"⚠ ALERT: {alert.description}")
            return alert
        
        # Kural 2: CAN Flood Detection
        self.can_timestamps.append(timestamp)
        if len(self.can_timestamps) >= self.can_flood_threshold:
            time_window = timestamp - self.can_timestamps[0]
            if time_window < 1.0:  # 1 saniyeden kısa sürede threshold aşıldı
                alert = self._create_alert(
                    alert_type="CAN_FLOOD_ATTACK",
                    severity="CRITICAL",
                    description=f"{len(self.can_timestamps)} CAN frame {time_window:.2f} saniyede alındı",
                    source="CAN",
                    data={"frame_count": len(self.can_timestamps), "time_window": time_window}
                )
                logger.error(f"🚨 CRITICAL ALERT: {alert.description}")
                return alert
        
        # Kural 3: Replay Attack Detection
        for msg_time, msg_hash in self.recent_messages:
            if timestamp - msg_time <= self.replay_window and msg_hash == frame_hash:
                alert = self._create_alert(
                    alert_type="REPLAY_ATTACK",
                    severity="HIGH",
                    description=f"CAN frame replay tespit edildi: ID={hex(can_id)}",
                    source="CAN",
                    data={"can_id": hex(can_id), "time_diff": timestamp - msg_time}
                )
                logger.warning(f"⚠ ALERT: {alert.description}")
                return alert
        
        # Kural 4: Invalid CAN ID Check
        if can_id not in self.allowed_can_ids:
            alert = self._create_alert(
                alert_type="INVALID_CAN_ID",
                severity="MEDIUM",
                description=f"İzin listesinde olmayan CAN ID: {hex(can_id)}",
                source="CAN",
                data={"can_id": hex(can_id), "data": [hex(b) for b in data]}
            )
            logger.warning(f"⚠ ALERT: {alert.description}")
            return alert
        
        # Mesajı recent listesine ekle
        self.recent_messages.append((timestamp, frame_hash))
        
        return None  # Anomali yok
    
    def check_ocpp_message(self, action: str, payload: Dict, timestamp: float, 
                          source_ip: Optional[str] = None) -> Optional[Alert]:
        """
        OCPP mesajını kontrol et.
        
        Returns:
            Alert objesi veya None
        """
        self.stats.total_ocpp_messages += 1
        self.stats.last_ocpp_time = timestamp
        
        # Frekans sayacını güncelle
        self.stats.ocpp_action_frequency[action] = \
            self.stats.ocpp_action_frequency.get(action, 0) + 1
        
        # OCPP action'ı kaydet (K1 için)
        self.last_ocpp_actions.append((timestamp, action))
        
        # Senaryo #2: OCPP Rate Limiting Check (DoS Detection)
        self.stats.ocpp_message_timestamps.append(timestamp)
        
        # Rate hesapla: Son N mesaj kaç saniyede geldi?
        if len(self.stats.ocpp_message_timestamps) >= self.ocpp_rate_threshold:
            oldest_time = self.stats.ocpp_message_timestamps[0]
            time_window = timestamp - oldest_time
            
            if time_window < self.ocpp_rate_window:
                messages_per_second = len(self.stats.ocpp_message_timestamps) / time_window
                
                if messages_per_second > self.ocpp_rate_threshold:
                    self.stats.ocpp_rate_alerts += 1
                    alert = self._create_alert(
                        alert_type="OCPP_RATE_LIMIT_EXCEEDED",
                        severity="CRITICAL",
                        description=f"OCPP mesaj yoğunluğu saldırısı tespit edildi: {messages_per_second:.1f} mesaj/saniye (eşik: {self.ocpp_rate_threshold})",
                        source="OCPP",
                        data={
                            "action": action,
                            "messages_per_second": round(messages_per_second, 2),
                            "threshold": self.ocpp_rate_threshold,
                            "time_window": round(time_window, 3),
                            "message_count": len(self.stats.ocpp_message_timestamps),
                            "source_ip": source_ip
                        }
                    )
                    logger.error(f"🚨 CRITICAL ALERT [SCENARIO-2]: {alert.description}")
                    return alert
        
        # K1: Timing Mismatch Detection (Senaryo #1)
        # RemoteStartTransaction sonrası 2 saniye içinde RemoteStopTransaction
        if action == "RemoteStopTransaction":
            for ts, prev_action in self.last_ocpp_actions:
                if prev_action == "RemoteStartTransaction" and (timestamp - ts) < 2.0:
                    alert = self._create_alert(
                        alert_type="TIMING_MISMATCH_K1",
                        severity="HIGH",
                        description=f"RemoteStart sonrası {timestamp - ts:.2f}s içinde RemoteStop tespit edildi",
                        source="OCPP",
                        data={
                            "prev_action": prev_action,
                            "current_action": action,
                            "time_diff": timestamp - ts,
                            "threshold": 2.0
                        }
                    )
                    logger.warning(f"⚠ ALERT [K1]: {alert.description}")
                    return alert
        
        # K2: Session Fingerprint Change (Senaryo #1)
        # Aynı idTag için farklı IP/fingerprint
        if source_ip and "id_tag" in payload:
            id_tag = payload["id_tag"]
            
            # Fingerprint setine ekle
            self.session_fingerprints[id_tag].add(source_ip)
            
            # Eğer aynı tag için 2'den fazla farklı IP varsa
            if len(self.session_fingerprints[id_tag]) > 2:
                alert = self._create_alert(
                    alert_type="SESSION_FINGERPRINT_CHANGE_K2",
                    severity="CRITICAL",
                    description=f"idTag {id_tag} için {len(self.session_fingerprints[id_tag])} farklı IP tespit edildi",
                    source="OCPP",
                    data={
                        "id_tag": id_tag,
                        "fingerprints": list(self.session_fingerprints[id_tag]),
                        "count": len(self.session_fingerprints[id_tag])
                    }
                )
                logger.error(f"🚨 CRITICAL ALERT [K2]: {alert.description}")
                return alert
        
        # Kural: Timestamp Anomaly (eski zaman damgası)
        if self.stats.last_ocpp_time and timestamp < self.stats.last_ocpp_time - 60:
            alert = self._create_alert(
                alert_type="OCPP_TIMESTAMP_ANOMALY",
                severity="MEDIUM",
                description=f"Eski timestamp ile OCPP mesajı: {action}",
                source="OCPP",
                data={"action": action, "timestamp": timestamp}
            )
            logger.warning(f"⚠ ALERT: {alert.description}")
            return alert
        
        return None
    
    def check_meter_values(
        self, 
        meter_value: float, 
        timestamp: float,
        raw_buffer_size: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Optional[Alert]:
        """
        MeterValues mesajını kontrol et (Senaryo #3: Sampling Manipulation).
        
        Args:
            meter_value: Ölçülen enerji değeri (kWh veya W)
            timestamp: Ölçüm zamanı
            raw_buffer_size: Cihazda bekleyen ham örnek sayısı
            session_id: Şarj seans ID'si
        
        Returns:
            Alert objesi veya None
        """
        # Meter sample'ı kaydet
        self.stats.meter_samples.append((timestamp, meter_value))
        self.stats.sent_sample_count += 1
        
        if raw_buffer_size is not None:
            self.stats.raw_sample_buffer_size = raw_buffer_size
        
        # Kural-1: Sampling Rate Düşüşü
        # Son 60 saniyedeki sample sayısını hesapla
        recent_samples = [
            (t, v) for t, v in self.stats.meter_samples 
            if timestamp - t <= 60.0
        ]
        samples_per_minute = len(recent_samples)
        self.stats.samples_per_minute = samples_per_minute
        
        if len(recent_samples) >= 5 and samples_per_minute < self.min_sampling_rate:
            alert = self._create_alert(
                alert_type="SAMPLING_RATE_DROP",
                severity="HIGH",
                description=f"Örnekleme oranı düştü: {samples_per_minute} sample/min (min: {self.min_sampling_rate})",
                source="OCPP",
                data={
                    "samples_per_minute": samples_per_minute,
                    "threshold": self.min_sampling_rate,
                    "session_id": session_id,
                    "time_window": 60.0
                }
            )
            logger.warning(f"⚠ ALERT [SCENARIO-3]: {alert.description}")
            return alert
        
        # Kural-2: Varyans Düşüşü (Energy Flatness / Peak Smoothing)
        if len(recent_samples) >= 10:
            values = [v for _, v in recent_samples]
            current_variance = np.var(values) if len(values) > 1 else 0.0
            
            # Historical variance hesapla (önceki 5 dakika)
            old_samples = [
                v for t, v in self.stats.meter_samples 
                if 60 < (timestamp - t) <= 360
            ]
            
            if len(old_samples) >= 10:
                historical_variance = np.var(old_samples)
                self.stats.energy_variance_history.append(current_variance)
                
                # %30'dan fazla düşüş varsa alarm
                if historical_variance > 0 and current_variance < historical_variance * self.variance_drop_threshold:
                    alert = self._create_alert(
                        alert_type="ENERGY_VARIANCE_DROP",
                        severity="CRITICAL",
                        description=f"Enerji varyansı anormal düştü: {current_variance:.4f} (beklenen: {historical_variance:.4f})",
                        source="OCPP",
                        data={
                            "current_variance": round(current_variance, 4),
                            "historical_variance": round(historical_variance, 4),
                            "drop_ratio": round(current_variance / historical_variance, 2),
                            "threshold": self.variance_drop_threshold,
                            "session_id": session_id,
                            "note": "Peak değerler gizleniyor olabilir"
                        }
                    )
                    logger.error(f"🚨 CRITICAL ALERT [SCENARIO-3]: {alert.description}")
                    return alert
        
        # Kural-3: Buffer Mismatch (Ham veri vs Gönderilen veri)
        if raw_buffer_size is not None and raw_buffer_size > 0:
            if self.stats.sent_sample_count > 0:
                buffer_ratio = raw_buffer_size / self.stats.sent_sample_count
                
                if buffer_ratio > self.buffer_mismatch_ratio:
                    alert = self._create_alert(
                        alert_type="BUFFER_MANIPULATION",
                        severity="CRITICAL",
                        description=f"Ham veri buffer anormali: {raw_buffer_size} raw sample, {self.stats.sent_sample_count} sent (oran: {buffer_ratio:.1f}x)",
                        source="OCPP",
                        data={
                            "raw_buffer_size": raw_buffer_size,
                            "sent_sample_count": self.stats.sent_sample_count,
                            "ratio": round(buffer_ratio, 2),
                            "threshold": self.buffer_mismatch_ratio,
                            "session_id": session_id,
                            "note": "Yerelde veri birikiyor → Manipülasyon şüphesi"
                        }
                    )
                    logger.error(f"🚨 CRITICAL ALERT [SCENARIO-3]: {alert.description}")
                    return alert
        
        return None
    
    def check_auth_failure(self, auth_status: str, timestamp: float, 
                          auth_response_time: Optional[float] = None) -> Optional[Alert]:
        """
        Senaryo #4: Auth başarısızlığını kontrol et (Fail-Open davranışı tespiti).
        
        Args:
            auth_status: "SUCCESS", "FAILED", "TIMEOUT", "UNAVAILABLE"
            timestamp: İşlem zamanı
            auth_response_time: Auth yanıt süresi (None ise timeout)
        
        Returns:
            Alert objesi veya None
        """
        # Auth timeout tracking
        if auth_status in ["TIMEOUT", "UNAVAILABLE"] or auth_response_time is None:
            self.stats.auth_timeout_timestamps.append(timestamp)
            self.stats.consecutive_auth_timeouts += 1
            self.stats.auth_failure_count += 1
            
            # Kural-1: Auth Servis Erişilemezlik Tespiti
            # Son 60 saniyede 3+ timeout
            current_time = timestamp
            recent_timeouts = [
                ts for ts in self.stats.auth_timeout_timestamps
                if current_time - ts <= self.auth_timeout_window
            ]
            
            if len(recent_timeouts) >= self.auth_timeout_threshold:
                alert = self._create_alert(
                    alert_type="AUTH_SERVICE_UNAVAILABLE",
                    severity="HIGH",
                    description=f"Auth Servis erişilemez: Son {self.auth_timeout_window}s içinde {len(recent_timeouts)} timeout",
                    source="OCPP",
                    data={
                        "auth_status": auth_status,
                        "timeout_count": len(recent_timeouts),
                        "threshold": self.auth_timeout_threshold,
                        "window": self.auth_timeout_window,
                        "consecutive_timeouts": self.stats.consecutive_auth_timeouts
                    }
                )
                logger.warning(f"⚠ ALERT [SCENARIO-4]: {alert.description}")
                return alert
            
            # Kural-3: Auth Timeout Pattern (Ardışık timeout'lar)
            if self.stats.consecutive_auth_timeouts >= self.consecutive_timeout_threshold:
                alert = self._create_alert(
                    alert_type="AUTH_TIMEOUT_PATTERN",
                    severity="HIGH",
                    description=f"Ardışık auth timeout pattern: {self.stats.consecutive_auth_timeouts} ardışık timeout",
                    source="OCPP",
                    data={
                        "consecutive_timeouts": self.stats.consecutive_auth_timeouts,
                        "threshold": self.consecutive_timeout_threshold,
                        "auth_status": auth_status
                    }
                )
                logger.warning(f"⚠ ALERT [SCENARIO-4]: {alert.description}")
                return alert
        elif auth_status == "SUCCESS":
            # Başarılı auth: timeout sayacını sıfırla
            self.stats.consecutive_auth_timeouts = 0
            self.stats.auth_success_count += 1
            self.stats.last_successful_auth_time = timestamp
        
        return None
    
    def check_charge_without_auth(self, charge_started: bool, auth_status: str, 
                                  timestamp: float) -> Optional[Alert]:
        """
        Senaryo #4: Auth olmadan şarj başlatma tespiti (Fail-Open davranışı).
        
        Args:
            charge_started: Şarj başlatıldı mı?
            auth_status: Auth durumu ("SUCCESS", "FAILED", "TIMEOUT", "UNAVAILABLE", "NONE")
            timestamp: İşlem zamanı
        
        Returns:
            Alert objesi veya None
        """
        if not charge_started:
            return None
        
        # Auth başarısız veya yok ama şarj başladı → Fail-Open davranışı
        if auth_status in ["FAILED", "TIMEOUT", "UNAVAILABLE", "NONE"]:
            self.stats.charge_starts_without_auth += 1
            
            # Kural-2: Fail-Open Davranış Tespiti (Kritik)
            alert = self._create_alert(
                alert_type="FAIL_OPEN_BEHAVIOR",
                severity="CRITICAL",
                description=f"FAIL-OPEN DAVRANIŞI TESPİT EDİLDİ: Auth durumu '{auth_status}' olmasına rağmen şarj başlatıldı",
                source="OCPP",
                data={
                    "auth_status": auth_status,
                    "charge_started": charge_started,
                    "timestamp": timestamp,
                    "last_successful_auth": self.stats.last_successful_auth_time,
                    "consecutive_timeouts": self.stats.consecutive_auth_timeouts,
                    "note": "Sistem fail-closed yerine fail-open davranışı gösteriyor!"
                }
            )
            logger.error(f"🚨 CRITICAL ALERT [SCENARIO-4]: {alert.description}")
            return alert
        
        # Kural-4: Unauthorized Charge Start (Auth başarısız ama şarj başladı)
        if auth_status == "FAILED" and charge_started:
            alert = self._create_alert(
                alert_type="UNAUTHORIZED_CHARGE_START",
                severity="CRITICAL",
                description=f"Yetkisiz şarj başlatma: Auth başarısız olmasına rağmen şarj başlatıldı",
                source="OCPP",
                data={
                    "auth_status": auth_status,
                    "charge_started": charge_started,
                    "timestamp": timestamp,
                    "note": "Kimlik doğrulama başarısız ama şarj başladı"
                }
            )
            logger.error(f"🚨 CRITICAL ALERT [SCENARIO-4]: {alert.description}")
            return alert
        
        return None
    
    def check_reservation(
        self,
        reservation_id: str,
        connector_id: int,
        id_tag: str,
        timestamp: float,
        expiry_date: Optional[str] = None,
        action: str = "ReserveNow"
    ) -> Optional[Alert]:
        """
        Senaryo #5: Rezervasyon (ReserveNow) kontrolü - Duplicate Booking tespiti.
        
        Args:
            reservation_id: Rezervasyon ID'si
            connector_id: Connector ID
            id_tag: Kullanıcı ID tag'i
            timestamp: Rezervasyon zamanı
            expiry_date: Rezervasyon bitiş zamanı (ISO format)
            action: OCPP action ("ReserveNow" veya "CancelReservation")
        
        Returns:
            Alert objesi veya None
        """
        if action == "CancelReservation":
            # Rezervasyon iptal edildi, kayıttan çıkar
            if reservation_id in self.stats.reservations:
                connector_id = self.stats.reservations[reservation_id]["connector_id"]
                if connector_id in self.stats.connector_reservations:
                    if reservation_id in self.stats.connector_reservations[connector_id]:
                        self.stats.connector_reservations[connector_id].remove(reservation_id)
                del self.stats.reservations[reservation_id]
            return None
        
        # Kural-1: Duplicate Reservation ID Tespiti (CRITICAL)
        if reservation_id in self.stats.reservations:
            existing_reservation = self.stats.reservations[reservation_id]
            time_diff = timestamp - existing_reservation["timestamp"]
            
            if time_diff <= self.duplicate_reservation_window:
                alert = self._create_alert(
                    alert_type="DUPLICATE_RESERVATION_ID",
                    severity="CRITICAL",
                    description=f"Çift rezervasyon ID tespit edildi: {reservation_id} (önceki rezervasyon {time_diff:.1f}s önce)",
                    source="OCPP",
                    data={
                        "reservation_id": reservation_id,
                        "connector_id": connector_id,
                        "id_tag": id_tag,
                        "existing_connector": existing_reservation["connector_id"],
                        "existing_id_tag": existing_reservation["id_tag"],
                        "time_diff": round(time_diff, 2),
                        "window": self.duplicate_reservation_window,
                        "note": "Aynı rezervasyon ID birden fazla kez kullanıldı"
                    }
                )
                logger.error(f"🚨 CRITICAL ALERT [SCENARIO-5]: {alert.description}")
                return alert
        
        # Kural-3: Reservation ID Reuse Pattern (HIGH)
        if reservation_id in self.stats.reservation_ids_used:
            # Daha önce kullanılmış bir ID tekrar kullanılıyor
            alert = self._create_alert(
                alert_type="RESERVATION_ID_REUSE",
                severity="HIGH",
                description=f"Rezervasyon ID tekrar kullanımı: {reservation_id} daha önce kullanılmış",
                source="OCPP",
                data={
                    "reservation_id": reservation_id,
                    "connector_id": connector_id,
                    "id_tag": id_tag,
                    "note": "Rezervasyon ID'leri benzersiz olmalı (UUID önerilir)"
                }
            )
            logger.warning(f"⚠ ALERT [SCENARIO-5]: {alert.description}")
            return alert
        
        # Rezervasyonu kaydet
        self.stats.reservations[reservation_id] = {
            "connector_id": connector_id,
            "id_tag": id_tag,
            "timestamp": timestamp,
            "expiry_date": expiry_date
        }
        self.stats.reservation_ids_used.add(reservation_id)
        self.stats.connector_reservations[connector_id].append(reservation_id)
        
        # Kural-2: Multiple Reservations for Same Connector (CRITICAL)
        active_reservations = self.stats.connector_reservations[connector_id]
        if len(active_reservations) > 1:
            alert = self._create_alert(
                alert_type="MULTIPLE_CONNECTOR_RESERVATIONS",
                severity="CRITICAL",
                description=f"Aynı connector ({connector_id}) için {len(active_reservations)} aktif rezervasyon tespit edildi",
                source="OCPP",
                data={
                    "connector_id": connector_id,
                    "reservation_count": len(active_reservations),
                    "reservation_ids": active_reservations,
                    "current_reservation_id": reservation_id,
                    "current_id_tag": id_tag,
                    "note": "Bir connector'a aynı anda tek rezervasyon olmalı"
                }
            )
            logger.error(f"🚨 CRITICAL ALERT [SCENARIO-5]: {alert.description}")
            return alert
        
        return None
    
    def check_reservation_transaction_match(
        self,
        transaction_id: str,
        id_tag: str,
        connector_id: int,
        timestamp: float
    ) -> Optional[Alert]:
        """
        Senaryo #5: Rezervasyon-Transaction eşleşmesi kontrolü.
        StartTransaction'da kullanılan idTag, rezervasyondaki idTag ile eşleşmeli.
        
        Args:
            transaction_id: Transaction ID
            id_tag: StartTransaction'da kullanılan idTag
            connector_id: Connector ID
            timestamp: İşlem zamanı
        
        Returns:
            Alert objesi veya None
        """
        # Bu connector için aktif rezervasyon var mı?
        active_reservations = self.stats.connector_reservations.get(connector_id, [])
        
        if not active_reservations:
            # Rezervasyon olmadan şarj başlatıldı (bu başka bir senaryo olabilir)
            return None
        
        # En son rezervasyonu kontrol et
        for reservation_id in active_reservations:
            if reservation_id in self.stats.reservations:
                reservation = self.stats.reservations[reservation_id]
                reservation_id_tag = reservation["id_tag"]
                
                # Kural-5: Reservation-Transaction Mismatch (CRITICAL)
                if reservation_id_tag != id_tag:
                    alert = self._create_alert(
                        alert_type="RESERVATION_TRANSACTION_MISMATCH",
                        severity="CRITICAL",
                        description=f"Rezervasyon-İşlem uyuşmazlığı: Rezervasyondaki idTag ({reservation_id_tag}) ile StartTransaction'daki idTag ({id_tag}) eşleşmiyor",
                        source="OCPP",
                        data={
                            "reservation_id": reservation_id,
                            "reservation_id_tag": reservation_id_tag,
                            "transaction_id_tag": id_tag,
                            "connector_id": connector_id,
                            "transaction_id": transaction_id,
                            "note": "Yetkisiz kullanıcı başkasının rezervasyonunu kullanıyor olabilir"
                        }
                    )
                    logger.error(f"🚨 CRITICAL ALERT [SCENARIO-5]: {alert.description}")
                    return alert
                
                # Eşleşme başarılı, rezervasyonu transaction'a bağla
                self.stats.reservation_to_transaction[reservation_id] = transaction_id
                # Rezervasyonu aktif listeden çıkar (şarj başladı)
                if reservation_id in self.stats.connector_reservations[connector_id]:
                    self.stats.connector_reservations[connector_id].remove(reservation_id)
        
        return None
    
    def register_expected_can_frame(self, ocpp_action: str, can_id: int):
        """
        OCPP action için beklenen CAN ID'yi kaydet (K3 için).
        
        Args:
            ocpp_action: OCPP action (örn. "RemoteStartTransaction")
            can_id: Beklenen CAN ID (örn. 0x200)
        """
        self.expected_can_frames[ocpp_action] = can_id
        logger.debug(f"Beklenen mapping kaydedildi: {ocpp_action} → {hex(can_id)}")
    
    def _hash_frame(self, can_id: int, data: List[int]) -> str:
        """CAN frame için unique hash oluştur"""
        frame_str = f"{can_id:03X}:{''.join(f'{b:02X}' for b in data)}"
        return frame_str
    
    def _create_alert(
        self,
        alert_type: str,
        severity: str,
        description: str,
        source: str,
        data: Dict
    ) -> Alert:
        """Yeni alert oluştur"""
        alert_id = f"ALERT-{len(self.alerts):06d}"
        alert = Alert(
            alert_id=alert_id,
            timestamp=time.time(),
            severity=severity,
            alert_type=alert_type,
            description=description,
            source=source,
            data=data
        )
        self.alerts.append(alert)
        self.stats.total_alerts += 1
        return alert
    
    def get_recent_alerts(self, count: int = 10) -> List[Alert]:
        """Son N alert'i getir"""
        return self.alerts[-count:] if len(self.alerts) >= count else self.alerts
    
    def get_alerts_by_severity(self, severity: str) -> List[Alert]:
        """Belirli bir severity'deki alert'leri getir"""
        return [alert for alert in self.alerts if alert.severity == severity]
    
    def get_stats(self) -> Dict:
        """IDS istatistiklerini getir"""
        return {
            "total_ocpp_messages": self.stats.total_ocpp_messages,
            "total_can_frames": self.stats.total_can_frames,
            "authorized_can_frames": self.stats.authorized_can_frames,
            "unauthorized_can_frames": self.stats.unauthorized_can_frames,
            "total_alerts": self.stats.total_alerts,
            "alert_breakdown": {
                "LOW": len(self.get_alerts_by_severity("LOW")),
                "MEDIUM": len(self.get_alerts_by_severity("MEDIUM")),
                "HIGH": len(self.get_alerts_by_severity("HIGH")),
                "CRITICAL": len(self.get_alerts_by_severity("CRITICAL"))
            },
            "can_id_frequency": {hex(k): v for k, v in self.stats.can_id_frequency.items()},
            "ocpp_action_frequency": self.stats.ocpp_action_frequency,
            # Senaryo #4: Auth statistics
            "auth_success_count": self.stats.auth_success_count,
            "auth_failure_count": self.stats.auth_failure_count,
            "consecutive_auth_timeouts": self.stats.consecutive_auth_timeouts,
            "charge_starts_without_auth": self.stats.charge_starts_without_auth
        }
    
    def clear_old_authorized_frames(self, older_than: float = 3600) -> None:
        """
        Eski yetkili frame kayıtlarını temizle (memory optimization)
        
        Args:
            older_than: Saniye cinsinden yaş sınırı
        """
        # Bu implementasyon basit bir versiyondur.
        # Production'da timestamp ile takip edilebilir.
        if len(self.authorized_frames) > 10000:
            logger.info("Yetkili frame cache'i temizleniyor...")
            for can_id in list(self.authorized_frames.keys()):
                if len(self.authorized_frames[can_id]) > 1000:
                    # En eski yarısını temizle (basit strateji)
                    frame_list = list(self.authorized_frames[can_id])
                    self.authorized_frames[can_id] = set(frame_list[-500:])


if __name__ == "__main__":
    # Test
    logger.info("Rule-Based IDS test ediliyor...")
    
    ids = RuleBasedIDS()
    
    print("\n" + "="*50)
    print("TEST 1: Normal Trafik")
    print("="*50)
    
    # Yetkili OCPP → CAN akışı
    ids.check_ocpp_message("RemoteStartTransaction", {"connector_id": 1}, time.time())
    ids.register_authorized_can_frame(0x200, [0x01, 0x01, 0xAB, 0xCD, 0x00, 0x00, 0x00, 0x00])
    alert = ids.check_can_frame(0x200, [0x01, 0x01, 0xAB, 0xCD, 0x00, 0x00, 0x00, 0x00], time.time())
    
    if alert:
        print(f"❌ Alert: {alert.description}")
    else:
        print("✓ Normal trafik, anomali yok")
    
    print("\n" + "="*50)
    print("TEST 2: Unauthorized CAN Injection")
    print("="*50)
    
    # Yetkisiz CAN frame (Bridge tarafından gönderilmedi)
    alert = ids.check_can_frame(0x200, [0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00], time.time())
    if alert:
        print(f"🚨 Alert: {alert.description} (Severity: {alert.severity})")
    
    print("\n" + "="*50)
    print("TEST 3: CAN Flood Attack")
    print("="*50)
    
    # 150 CAN frame 0.5 saniyede
    start_time = time.time()
    for i in range(150):
        ids.register_authorized_can_frame(0x201, [i & 0xFF, 0x00])
        alert = ids.check_can_frame(0x201, [i & 0xFF, 0x00], start_time + i * 0.003)
        if alert and alert.alert_type == "CAN_FLOOD_ATTACK":
            print(f"🚨 FLOOD DETECTED after {i} frames!")
            break
    
    print("\n" + "="*50)
    print("IDS İSTATİSTİKLERİ")
    print("="*50)
    stats = ids.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

