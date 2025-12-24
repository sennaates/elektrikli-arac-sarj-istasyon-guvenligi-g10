"""
🔥 Saldırı Test Dashboard - Kullanıcı Dostu Versiyon
Elektrikli Araç Şarj İstasyonu Güvenlik Sistemi
"""
import streamlit as st
import requests
import time
from datetime import datetime
import os
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="🔥 Saldırı Test Paneli",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

# 9 Saldırı Senaryosu - Gerçekçi bildirimlerle
SCENARIOS = {
    "overview": {
        "name": "Genel Bakış",
        "icon": "📊",
        "color": "#6366f1",
        "gradient": "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
        "description": "Tüm sistem durumunu ve tespit edilen tehditleri görüntüleyin",
        "attack_func": None,
        "alert_message": "",
        "alert_detail": "",
        "alert_filter": []
    },
    "mitm": {
        "name": "MitM OCPP",
        "icon": "🎭",
        "color": "#ef4444",
        "gradient": "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)",
        "description": "OCPP protokolü üzerinden Man-in-the-Middle saldırısı",
        "attack_func": "mitm_ocpp_manipulation()",
        "alert_message": "⚠️ DİKKAT: Şarj istasyonunuz ile merkez sistem arasındaki iletişim ele geçirildi!",
        "alert_detail": "Bir saldırgan, aracınız şarj olurken istasyon ile sunucu arasındaki mesajları okuyup değiştiriyor. Şarj ücreti manipüle edilebilir, oturumunuz çalınabilir veya sahte komutlar gönderilebilir.",
        "risk_items": ["💳 Şarj ücretiniz değiştirilebilir", "🔑 Oturum bilgileriniz çalınabilir", "⚡ Şarj işlemi aniden durdurulabilir"],
        "alert_filter": ["MITM", "MANIPULATION"],
        "prevention_title": "🛡️ Sistem Bu Saldırıyı Nasıl Önledi?",
        "prevention_detail": "Güvenlik sistemimiz, OCPP mesajlarındaki anormal değişiklikleri tespit etti. Mesaj bütünlüğü kontrolü sayesinde manipüle edilmiş komutlar reddedildi.",
        "prevention_steps": [
            "🔍 Kural Tabanlı IDS: OCPP mesaj yapısındaki anormallik tespit edildi",
            "🤖 ML-IDS: Mesaj içeriğindeki beklenmedik değişiklikler yakalandı",
            "🚫 Önlem: Şüpheli mesajlar bloke edildi, oturum güvenli tutuldu",
            "⛓️ Blockchain: Saldırı girişimi değiştirilemez şekilde kayıt altına alındı"
        ]
    },
    "flood": {
        "name": "CAN Flood",
        "icon": "🌊",
        "color": "#3b82f6",
        "gradient": "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
        "description": "CAN Bus'ı yüksek frekanslı mesajlarla doldurarak DoS saldırısı",
        "attack_func": "can_flood()",
        "alert_message": "⚠️ DİKKAT: Aracınızın iç iletişim sistemi aşırı yükleniyor!",
        "alert_detail": "Saldırgan, aracınızın CAN Bus ağına saniyede binlerce sahte mesaj gönderiyor. Bu durum aracın kontrol sistemlerinin yavaşlamasına veya tamamen durmasına neden olabilir.",
        "risk_items": ["🚗 Araç kontrolleri yanıt vermeyebilir", "📊 Gösterge paneli hatalı bilgi gösterebilir", "🔋 Şarj işlemi kesintiye uğrayabilir"],
        "alert_filter": ["FLOOD", "CAN_FLOOD"],
        "prevention_title": "🛡️ Sistem Bu Saldırıyı Nasıl Önledi?",
        "prevention_detail": "Güvenlik sistemimiz, CAN Bus üzerindeki anormal mesaj yoğunluğunu anında tespit etti. Saniyede gelen mesaj sayısı normal seviyenin çok üzerine çıktığında alarm verildi.",
        "prevention_steps": [
            "🔍 Kural Tabanlı IDS: Mesaj frekansı eşik değerini aştığında alarm verildi",
            "🤖 ML-IDS: Normal trafik paterninden sapma tespit edildi",
            "🚫 Önlem: Flood kaynağı izole edildi, kritik mesajlara öncelik verildi",
            "⛓️ Blockchain: Saldırı detayları kanıt olarak kaydedildi"
        ]
    },
    "sampling": {
        "name": "Sampling Manipulation",
        "icon": "📉",
        "color": "#8b5cf6",
        "gradient": "linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)",
        "description": "Enerji ölçüm verilerinin örnekleme oranını manipüle eder",
        "attack_func": "sampling_manipulation()",
        "alert_message": "⚠️ DİKKAT: Şarj istasyonundaki enerji ölçümleri manipüle ediliyor!",
        "alert_detail": "Saldırgan, şarj istasyonunun enerji sayacını kandırıyor. Ölçüm aralıkları değiştirilerek gerçekte harcanan enerjiden farklı bir miktar raporlanıyor.",
        "risk_items": ["💰 Olduğundan fazla ücret ödersiniz", "📊 Batarya seviyesi yanlış gösterilir", "⚡ Aşırı şarj riski oluşabilir"],
        "alert_filter": ["SAMPLING"],
        "prevention_title": "🛡️ Sistem Bu Saldırıyı Nasıl Önledi?",
        "prevention_detail": "Güvenlik sistemimiz, enerji ölçüm verilerindeki tutarsızlıkları tespit etti. Örnekleme oranındaki ani değişiklikler alarm tetikledi.",
        "prevention_steps": [
            "🔍 Kural Tabanlı IDS: Örnekleme aralığındaki anormal değişiklik tespit edildi",
            "🤖 ML-IDS: Enerji tüketim paternindeki sapma yakalandı",
            "🚫 Önlem: Manipüle edilmiş veriler işaretlendi, doğru değerler kullanıldı",
            "⛓️ Blockchain: Gerçek ölçümler güvenli şekilde saklandı"
        ]
    },
    "fail_open": {
        "name": "Fail-Open Attack",
        "icon": "🔓",
        "color": "#f59e0b",
        "gradient": "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
        "description": "Sistemi offline moda zorlayarak güvenlik kontrollerini devre dışı bırakır",
        "attack_func": "fail_open_attack('ws://localhost:9000')",
        "alert_message": "⚠️ DİKKAT: Şarj istasyonu güvenlik kontrolleri devre dışı bırakıldı!",
        "alert_detail": "Saldırgan, istasyonun merkez sistemle bağlantısını kesti. İstasyon 'offline mod'a geçti ve güvenlik kontrolleri atlandı. Artık yetkisiz kullanıcılar da şarj yapabilir.",
        "risk_items": ["🔓 Yetkilendirme atlanıyor", "💳 Sizin hesabınızdan şarj yapılabilir", "📡 İşlemler kayıt altına alınmıyor"],
        "alert_filter": ["FAIL_OPEN", "OFFLINE"],
        "prevention_title": "🛡️ Sistem Bu Saldırıyı Nasıl Önledi?",
        "prevention_detail": "Güvenlik sistemimiz, kasıtlı bağlantı kesme girişimini tespit etti. Fail-secure modu devreye girdi ve tüm işlemler durduruldu.",
        "prevention_steps": [
            "🔍 Kural Tabanlı IDS: Şüpheli bağlantı kesme paterni tespit edildi",
            "🤖 ML-IDS: Normal olmayan offline geçiş davranışı yakalandı",
            "🚫 Önlem: Fail-secure mod aktif - yetkisiz işlemler engellendi",
            "⛓️ Blockchain: Offline dönemdeki tüm girişimler kayıt altına alındı"
        ]
    },
    "ransomware": {
        "name": "Ransomware",
        "icon": "💀",
        "color": "#dc2626",
        "gradient": "linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)",
        "description": "Sahte firmware güncellemesi ile sistemi ele geçirmeye çalışır",
        "attack_func": "ransomware_attack()",
        "alert_message": "🚨 KRİTİK: Şarj istasyonuna fidye yazılımı bulaştırılmaya çalışılıyor!",
        "alert_detail": "Saldırgan, şarj istasyonuna sahte bir firmware güncellemesi gönderiyor. Bu güncelleme aslında istasyonu kilitleyen ve fidye talep eden zararlı bir yazılım içeriyor.",
        "risk_items": ["🔒 İstasyon tamamen kilitlenebilir", "💰 Fidye talep edilebilir", "📁 Tüm veriler şifrelenebilir"],
        "alert_filter": ["RANSOMWARE", "FIRMWARE", "Firmware"],
        "prevention_title": "🛡️ Sistem Bu Saldırıyı Nasıl Önledi?",
        "prevention_detail": "Güvenlik sistemimiz, sahte firmware güncellemesini tespit etti. Dijital imza doğrulaması başarısız oldu ve güncelleme reddedildi.",
        "prevention_steps": [
            "🔍 Kural Tabanlı IDS: Yetkisiz firmware güncelleme girişimi tespit edildi",
            "🤖 ML-IDS: Zararlı kod imzası tanındı",
            "🚫 Önlem: Güncelleme bloke edildi, sistem korundu",
            "⛓️ Blockchain: Saldırı girişimi kanıt olarak saklandı"
        ]
    },
    "latency": {
        "name": "Latency Exploit",
        "icon": "⏱️",
        "color": "#06b6d4",
        "gradient": "linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)",
        "description": "Sistem gecikmelerini kullanarak saldırı penceresi oluşturur",
        "attack_func": "latency_exploit_attack()",
        "alert_message": "⚠️ DİKKAT: Sistem gecikmeleri kötüye kullanılıyor!",
        "alert_detail": "Saldırgan, şarj istasyonunun yanıt gecikmelerini analiz ederek güvenlik kontrollerinin arasındaki boşlukları tespit etti. Bu boşluklardan yetkisiz işlemler gerçekleştiriliyor.",
        "risk_items": ["⏰ Güvenlik kontrolleri atlanıyor", "🔄 Çift işlem yapılabilir", "💸 Ücretsiz şarj yapılabilir"],
        "alert_filter": ["LATENCY"],
        "prevention_title": "🛡️ Sistem Bu Saldırıyı Nasıl Önledi?",
        "prevention_detail": "Güvenlik sistemimiz, zamanlama bazlı saldırı girişimini tespit etti. İşlem zaman damgaları kontrol edilerek şüpheli aktivite engellendi.",
        "prevention_steps": [
            "🔍 Kural Tabanlı IDS: Anormal zamanlama paterni tespit edildi",
            "🤖 ML-IDS: İşlem aralıklarındaki sapma yakalandı",
            "🚫 Önlem: Şüpheli işlemler için ek doğrulama istendi",
            "⛓️ Blockchain: Tüm işlem zamanları değiştirilemez şekilde kaydedildi"
        ]
    },
    "replay": {
        "name": "Replay Attack",
        "icon": "🔁",
        "color": "#10b981",
        "gradient": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
        "description": "Geçerli CAN mesajlarını kaydedip tekrar göndererek sistemi yanıltır",
        "attack_func": "replay_attack()",
        "alert_message": "⚠️ DİKKAT: Eski komutlarınız tekrar oynatılıyor!",
        "alert_detail": "Saldırgan, daha önce gönderdiğiniz geçerli komutları kaydetti ve şimdi bunları tekrar gönderiyor. Sistem bu komutları sizden geliyormuş gibi kabul ediyor.",
        "risk_items": ["🔄 Eski işlemler tekrarlanıyor", "🚪 Kapı kilidi açılabilir", "⚡ Şarj işlemi manipüle edilebilir"],
        "alert_filter": ["REPLAY"],
        "prevention_title": "🛡️ Sistem Bu Saldırıyı Nasıl Önledi?",
        "prevention_detail": "Güvenlik sistemimiz, tekrar gönderilen eski mesajları tespit etti. Her mesajdaki benzersiz zaman damgası ve sıra numarası kontrol edildi.",
        "prevention_steps": [
            "🔍 Kural Tabanlı IDS: Duplicate mesaj tespit edildi",
            "🤖 ML-IDS: Mesaj sıra numarasındaki anormallik yakalandı",
            "🚫 Önlem: Eski mesajlar reddedildi, sadece yeni mesajlar kabul edildi",
            "⛓️ Blockchain: Her mesajın hash değeri saklanarak tekrar kullanım engellendi"
        ]
    },
    "entropy": {
        "name": "High Entropy",
        "icon": "🎲",
        "color": "#ec4899",
        "gradient": "linear-gradient(135deg, #ec4899 0%, #db2777 100%)",
        "description": "Rastgele yüksek entropi verileri göndererek anomali oluşturur",
        "attack_func": "high_entropy_attack()",
        "alert_message": "⚠️ DİKKAT: Sisteme anlamsız veriler enjekte ediliyor!",
        "alert_detail": "Saldırgan, araç ve istasyon arasındaki iletişime rastgele şifrelenmiş veriler gönderiyor. Bu durum sistemin beklenmedik davranışlar sergilemesine veya çökmesine neden olabilir.",
        "risk_items": ["💥 Sistem çökebilir", "🔀 Veriler bozulabilir", "❓ Beklenmedik davranışlar oluşabilir"],
        "alert_filter": ["ENTROPY", "HIGH_ENTROPY"],
        "prevention_title": "🛡️ Sistem Bu Saldırıyı Nasıl Önledi?",
        "prevention_detail": "Güvenlik sistemimiz, yüksek entropi içeren anormal verileri tespit etti. Rastgele ve anlamsız veriler filtrelenerek sistem korundu.",
        "prevention_steps": [
            "🔍 Kural Tabanlı IDS: Veri yapısı formatına uymayan içerik tespit edildi",
            "🤖 ML-IDS: Yüksek entropi skoru hesaplandı ve alarm verildi",
            "🚫 Önlem: Anlamsız veriler filtrelendi, sistem kararlılığı korundu",
            "⛓️ Blockchain: Saldırı örüntüsü analiz için kaydedildi"
        ]
    },
    "poisoning": {
        "name": "Sensor Poisoning",
        "icon": "☠️",
        "color": "#14b8a6",
        "gradient": "linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)",
        "description": "Sensör verilerini yavaşça değiştirerek tespit edilmeden sapma oluşturur",
        "attack_func": "sensor_data_poisoning(duration=5)",
        "alert_message": "⚠️ DİKKAT: Sensör verileri yavaşça zehirleniyor!",
        "alert_detail": "Saldırgan, şarj istasyonundaki sensör verilerini çok yavaş bir şekilde değiştiriyor. Bu küçük değişiklikler tek başına alarm vermese de, zamanla ciddi sapmalara yol açıyor.",
        "risk_items": ["🌡️ Sıcaklık yanlış ölçülüyor", "🔋 Batarya seviyesi hatalı gösteriliyor", "⚠️ Aşırı şarj/deşarj riski"],
        "alert_filter": ["POISONING", "SENSOR"],
        "prevention_title": "🛡️ Sistem Bu Saldırıyı Nasıl Önledi?",
        "prevention_detail": "Güvenlik sistemimiz, sensör verilerindeki kademeli sapmayı tespit etti. Uzun vadeli trend analizi sayesinde yavaş değişiklikler bile yakalandı.",
        "prevention_steps": [
            "🔍 Kural Tabanlı IDS: Sensör değerlerindeki kümülatif sapma tespit edildi",
            "🤖 ML-IDS: Gradual drift (kademeli kayma) paterni tanındı",
            "🚫 Önlem: Şüpheli sensör verileri işaretlendi, yedek sensörler devreye alındı",
            "⛓️ Blockchain: Tüm sensör geçmişi karşılaştırma için saklandı"
        ]
    }
}

# Modern CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Ana başlık kartı */
    .header-card {
        background: var(--gradient);
        border-radius: 24px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }
    
    .header-card h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .header-card p {
        font-size: 1.25rem;
        opacity: 0.9;
        margin: 0.75rem 0 0 0;
    }
    
    /* Saldırı uyarı kutusu */
    .attack-alert-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%);
        border: 3px solid #ef4444;
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        animation: pulse-border 2s infinite;
    }
    
    @keyframes pulse-border {
        0%, 100% { border-color: #ef4444; }
        50% { border-color: #fca5a5; }
    }
    
    .attack-alert-title {
        color: #fca5a5;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .attack-alert-detail {
        color: rgba(255,255,255,0.9);
        font-size: 1.15rem;
        line-height: 1.7;
        margin-bottom: 1.25rem;
    }
    
    .risk-item {
        background: rgba(0,0,0,0.2);
        padding: 0.75rem 1.25rem;
        border-radius: 10px;
        margin: 0.4rem 0;
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
    }
    
    /* Metrik kartları */
    .stat-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        background: rgba(255,255,255,0.1);
        transform: translateY(-3px);
    }
    
    .stat-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
    .stat-value { font-size: 2.5rem; font-weight: 700; color: white; }
    .stat-label { font-size: 1rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.25rem; }
    .stat-help { font-size: 0.9rem; color: rgba(255,255,255,0.6); margin-top: 0.5rem; font-style: italic; }
    
    /* Alert kartları */
    .alert-item {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin: 0.75rem 0;
        border-left: 5px solid;
        transition: all 0.2s;
    }
    
    .alert-item:hover {
        background: rgba(255,255,255,0.08);
    }
    
    .alert-critical { border-left-color: #ef4444; }
    .alert-high { border-left-color: #f59e0b; }
    .alert-medium { border-left-color: #eab308; }
    .alert-low { border-left-color: #22c55e; }
    
    .alert-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .alert-type {
        color: white;
        font-weight: 700;
        font-size: 1.15rem;
    }
    
    .alert-time {
        color: rgba(255,255,255,0.5);
        font-size: 0.95rem;
    }
    
    .alert-desc {
        color: rgba(255,255,255,0.8);
        font-size: 1.05rem;
        line-height: 1.5;
    }
    
    .severity-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    .badge-critical { background: #ef4444; color: white; }
    .badge-high { background: #f59e0b; color: white; }
    .badge-medium { background: #eab308; color: black; }
    .badge-low { background: #22c55e; color: white; }
    
    /* Bölüm başlıkları */
    .section-title {
        color: white;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(255,255,255,0.1);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-help {
        color: rgba(255,255,255,0.6);
        font-size: 1rem;
        font-weight: 400;
        margin-left: auto;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
    }
    
    [data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 1rem 1.25rem !important;
        border-radius: 12px !important;
        transition: all 0.3s !important;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.2) !important;
        transform: translateX(5px) !important;
    }
    
    [data-testid="stSidebar"] .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        border: none !important;
    }
    
    /* Başarı kutusu */
    .success-box {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(22, 163, 74, 0.2) 100%);
        border: 2px solid rgba(34, 197, 94, 0.5);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        text-align: center;
    }
    
    .success-text {
        color: #4ade80;
        font-weight: 700;
        font-size: 1.25rem;
    }
    
    /* Info kutusu */
    .info-box {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 1rem 0;
        color: rgba(255,255,255,0.85);
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    .info-box strong {
        color: #60a5fa;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def fetch_api(endpoint: str):
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def run_attack(scenario_key: str):
    """Saldırıyı çalıştır"""
    scenario = SCENARIOS.get(scenario_key, {})
    attack_func = scenario.get("attack_func")
    
    if not attack_func:
        return None
    
    cmd = f"from attack_simulator import AttackSimulator; s=AttackSimulator(); s.connect(); s.{attack_func}; s.disconnect()"
    
    try:
        result = subprocess.run(
            [sys.executable, "-c", cmd],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        return {
            "success": True,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

def filter_alerts(alerts, scenario_key):
    if scenario_key == "overview" or not alerts:
        return alerts
    
    scenario = SCENARIOS.get(scenario_key, {})
    filters = scenario.get("alert_filter", [])
    
    if not filters:
        return alerts
    
    filtered = []
    for alert in alerts:
        alert_str = str(alert.get("type", "")) + str(alert.get("alert_type", "")) + str(alert.get("description", ""))
        if any(f.upper() in alert_str.upper() for f in filters):
            filtered.append(alert)
    
    return filtered if filtered else alerts

# Session state
if 'current_scenario' not in st.session_state:
    st.session_state.current_scenario = "overview"
if 'attack_executed' not in st.session_state:
    st.session_state.attack_executed = {}
if 'attack_running' not in st.session_state:
    st.session_state.attack_running = False

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <div style="font-size: 3.5rem; margin-bottom: 0.75rem;">🔥</div>
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">Saldırı Test Paneli</h2>
        <p style="color: rgba(255,255,255,0.7); font-size: 1rem; margin-top: 0.75rem;">
            Aşağıdan bir senaryo seçin
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    for key, scenario in SCENARIOS.items():
        is_active = st.session_state.current_scenario == key
        btn_type = "primary" if is_active else "secondary"
        
        if st.button(
            f"{scenario['icon']} {scenario['name']}",
            key=f"btn_{key}",
            use_container_width=True,
            type=btn_type
        ):
            st.session_state.current_scenario = key
            if key != "overview":
                st.session_state.attack_running = True
            st.rerun()
    
    st.markdown("---")
    
    # Sistem durumu
    health = fetch_api("/api/health")
    if health and health.get("status") == "healthy":
        st.markdown("""
        <div style="background: rgba(34, 197, 94, 0.2); padding: 0.75rem; border-radius: 10px; text-align: center; border: 1px solid rgba(34, 197, 94, 0.3);">
            <div style="color: #22c55e; font-weight: 600; font-size: 0.9rem;">✅ Sistem Aktif</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.2); padding: 0.75rem; border-radius: 10px; text-align: center; border: 1px solid rgba(239, 68, 68, 0.3);">
            <div style="color: #ef4444; font-weight: 600; font-size: 0.9rem;">❌ Sistem Kapalı</div>
        </div>
        """, unsafe_allow_html=True)

# Ana içerik
current = st.session_state.current_scenario
scenario = SCENARIOS[current]

# Saldırı çalıştır
if st.session_state.attack_running and current != "overview":
    progress_placeholder = st.empty()
    
    with progress_placeholder.container():
        st.markdown(f"""
        <div style="background: {scenario['gradient']}; border-radius: 20px; padding: 2rem; text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⏳</div>
            <h2 style="color: white; margin: 0;">{scenario['icon']} {scenario['name']}</h2>
            <p style="color: rgba(255,255,255,0.8); margin-top: 0.5rem;">Saldırı simüle ediliyor...</p>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.015)
            progress_bar.progress(i + 1)
    
    result = run_attack(current)
    st.session_state.attack_executed[current] = result
    st.session_state.attack_running = False
    progress_placeholder.empty()
    time.sleep(0.3)
    st.rerun()

# ==================== GENEL BAKIŞ SAYFASI ====================
if current == "overview":
    # API'den sistem durumunu al
    stats = fetch_api("/api/stats")
    health = fetch_api("/api/health")
    
    # Header - Genel Bakış için özel
    st.markdown(f"""
    <div class="header-card" style="--gradient: {scenario['gradient']};">
        <h1>{scenario['icon']} {scenario['name']}</h1>
        <p>{scenario['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Güvenli sistem durumu göster
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(22, 163, 74, 0.15) 100%); 
                border: 3px solid rgba(34, 197, 94, 0.4); 
                border-radius: 24px; 
                padding: 3rem; 
                text-align: center; 
                margin: 1.5rem 0 2.5rem 0;">
        <div style="font-size: 5rem; margin-bottom: 1.5rem;">🛡️</div>
        <div style="color: #4ade80; font-size: 2.25rem; font-weight: 700; margin-bottom: 0.75rem;">
            Sistem Güvenli
        </div>
        <div style="color: rgba(255,255,255,0.85); font-size: 1.25rem; margin-bottom: 1.5rem;">
            Şu anda aktif bir saldırı tespit edilmedi
        </div>
        <div style="display: flex; justify-content: center; gap: 3rem; flex-wrap: wrap; margin-top: 2rem;">
            <div style="text-align: center;">
                <div style="color: #4ade80; font-size: 2.5rem; font-weight: 700;">✓</div>
                <div style="color: rgba(255,255,255,0.7); font-size: 1.1rem;">CAN Bus Normal</div>
            </div>
            <div style="text-align: center;">
                <div style="color: #4ade80; font-size: 2.5rem; font-weight: 700;">✓</div>
                <div style="color: rgba(255,255,255,0.7); font-size: 1.1rem;">OCPP Bağlı</div>
            </div>
            <div style="text-align: center;">
                <div style="color: #4ade80; font-size: 2.5rem; font-weight: 700;">✓</div>
                <div style="color: rgba(255,255,255,0.7); font-size: 1.1rem;">ML-IDS Aktif</div>
            </div>
            <div style="text-align: center;">
                <div style="color: #4ade80; font-size: 2.5rem; font-weight: 700;">✓</div>
                <div style="color: rgba(255,255,255,0.7); font-size: 1.1rem;">Blockchain Çalışıyor</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Saldırı senaryoları başlık
    st.markdown(f"""
    <div class="section-title">
        🎯 Test Edilebilir Saldırı Senaryoları
        <span class="section-help">Sol menüden seçerek test başlatın</span>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(3)
    scenario_items = [(k, v) for k, v in SCENARIOS.items() if k != "overview"]
    
    for i, (key, scen) in enumerate(scenario_items):
        with cols[i % 3]:
            tested = "✅ Test Edildi" if key in st.session_state.attack_executed else "🔘 Henüz Test Edilmedi"
            tested_color = "#22c55e" if key in st.session_state.attack_executed else "#6b7280"
            border_color = "rgba(34, 197, 94, 0.3)" if key in st.session_state.attack_executed else "rgba(255,255,255,0.1)"
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border-radius: 14px; padding: 1.25rem; margin: 0.5rem 0; border: 2px solid {border_color};">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 2.25rem;">{scen['icon']}</span>
                    <div style="flex: 1;">
                        <div style="color: white; font-weight: 700; font-size: 1.15rem;">{scen['name']}</div>
                        <div style="color: rgba(255,255,255,0.6); font-size: 0.95rem; margin-top: 0.3rem;">{scen['description'][:45]}...</div>
                    </div>
                </div>
                <div style="color: {tested_color}; font-size: 1rem; margin-top: 0.75rem; text-align: right; font-weight: 500;">{tested}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Sistem açıklaması
    st.markdown("""
    <div style="background: rgba(59, 130, 246, 0.1); border: 2px solid rgba(59, 130, 246, 0.3); border-radius: 20px; padding: 2rem; margin-top: 2.5rem;">
        <div style="color: #60a5fa; font-size: 1.5rem; font-weight: 700; margin-bottom: 1.25rem;">🔐 Bu Sistem Ne Yapar?</div>
        <div style="color: rgba(255,255,255,0.85); font-size: 1.15rem; line-height: 1.8;">
            Bu güvenlik sistemi, elektrikli araç şarj istasyonlarına yapılabilecek <strong style="color: #f87171;">siber saldırıları tespit eder ve engeller</strong>. 
            Sol menüden bir saldırı seçtiğinizde, o saldırı simüle edilir ve sistemin nasıl tepki verdiğini görebilirsiniz.
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-top: 2rem;">
            <div style="text-align: center; padding: 1.5rem; background: rgba(0,0,0,0.2); border-radius: 14px;">
                <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🤖</div>
                <div style="color: white; font-weight: 700; font-size: 1.15rem;">ML-IDS</div>
                <div style="color: rgba(255,255,255,0.6); font-size: 1rem; margin-top: 0.5rem;">Yapay zeka ile<br>otomatik tespit</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: rgba(0,0,0,0.2); border-radius: 14px;">
                <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">⛓️</div>
                <div style="color: white; font-weight: 700; font-size: 1.15rem;">Blockchain</div>
                <div style="color: rgba(255,255,255,0.6); font-size: 1rem; margin-top: 0.5rem;">Değiştirilemez<br>olay kaydı</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: rgba(0,0,0,0.2); border-radius: 14px;">
                <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🛡️</div>
                <div style="color: white; font-weight: 700; font-size: 1.15rem;">Kural Tabanlı</div>
                <div style="color: rgba(255,255,255,0.6); font-size: 1rem; margin-top: 0.5rem;">Bilinen saldırıları<br>anında yakalar</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== SALDIRI SENARYOLARI SAYFALARI ====================
else:
    # Header
    st.markdown(f"""
    <div class="header-card" style="--gradient: {scenario['gradient']};">
        <h1>{scenario['icon']} {scenario['name']}</h1>
        <p>{scenario['description']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Saldırı uyarısı (eğer saldırı yapıldıysa)
    if current in st.session_state.attack_executed:
        attack_result = st.session_state.attack_executed[current]
        
        # Saldırı uyarısı
        st.markdown(f"""
        <div class="attack-alert-box">
            <div class="attack-alert-title">{scenario['alert_message']}</div>
            <div class="attack-alert-detail">{scenario['alert_detail']}</div>
            <div style="margin-top: 1.25rem;">
                <strong style="color: #fca5a5; font-size: 1.1rem;">🎯 Olası Riskler:</strong>
            </div>
        """, unsafe_allow_html=True)
        
        for risk in scenario.get('risk_items', []):
            st.markdown(f'<div class="risk-item">{risk}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ====== YENİ: SİSTEM NASIL ÖNLEDİ KISMI ======
        prevention_title = scenario.get('prevention_title', '🛡️ Sistem Bu Saldırıyı Nasıl Önledi?')
        prevention_detail = scenario.get('prevention_detail', '')
        prevention_steps = scenario.get('prevention_steps', [])
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(22, 163, 74, 0.15) 100%); 
                    border: 2px solid rgba(34, 197, 94, 0.4); 
                    border-radius: 20px; 
                    padding: 2rem; 
                    margin: 1.5rem 0;">
            <div style="color: #4ade80; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">
                {prevention_title}
            </div>
            <div style="color: rgba(255,255,255,0.9); font-size: 1.15rem; line-height: 1.7; margin-bottom: 1.5rem;">
                {prevention_detail}
            </div>
            <div style="color: white; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">
                📋 Uygulanan Güvenlik Adımları:
            </div>
        """, unsafe_allow_html=True)
        
        for step in prevention_steps:
            st.markdown(f"""
            <div style="background: rgba(0,0,0,0.2); padding: 1rem 1.25rem; border-radius: 12px; margin: 0.5rem 0; 
                        color: rgba(255,255,255,0.9); font-size: 1.05rem; border-left: 4px solid #4ade80;">
                {step}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tespit durumu
        st.markdown(f"""
        <div class="success-box">
            <div class="success-text">✅ Saldırı tespit edildi, önlendi ve kayıt altına alındı!</div>
            <div style="color: rgba(255,255,255,0.8); font-size: 1rem; margin-top: 0.75rem;">
                Saldırı zamanı: {attack_result.get('timestamp', '')} • Sistem güvenlik önlemlerini devreye aldı
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tekrar test butonu
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(f"🔄 Tekrar Test Et", use_container_width=True, type="primary"):
                st.session_state.attack_running = True
                st.rerun()

    # API verilerini al
    stats = fetch_api("/api/stats")
    all_alerts = fetch_api("/api/alerts?count=50") or []
    filtered_alerts = filter_alerts(all_alerts, current)

    # KPI Kartları
    st.markdown(f"""
    <div class="section-title">
        📈 Güvenlik Metrikleri
        <span class="section-help">Her sayının ne anlama geldiğini aşağıda görebilirsiniz</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">🚨</div>
            <div class="stat-value">{len(filtered_alerts)}</div>
            <div class="stat-label">Tespit Edilen Tehdit</div>
            <div class="stat-help">Sistemin yakaladığı şüpheli aktivite sayısı</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        critical = sum(1 for a in filtered_alerts if a.get("severity") == "CRITICAL")
        high = sum(1 for a in filtered_alerts if a.get("severity") == "HIGH")
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">🔴</div>
            <div class="stat-value">{critical + high}</div>
            <div class="stat-label">Yüksek Öncelikli</div>
            <div class="stat-help">Acil müdahale gerektiren tehditler</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        ml_stats = stats.get("ml", {}) if stats else {}
        ml_status = "Aktif" if ml_stats.get("is_trained") else "Pasif"
        ml_icon = "✅" if ml_stats.get("is_trained") else "⚠️"
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">🤖</div>
            <div class="stat-value" style="font-size: 1.3rem;">{ml_icon} {ml_status}</div>
            <div class="stat-label">ML-IDS Durumu</div>
            <div class="stat-help">Yapay zeka tabanlı saldırı tespiti</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        bc_stats = stats.get("blockchain", {}) if stats else {}
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">⛓️</div>
            <div class="stat-value">{bc_stats.get("total_blocks", 0)}</div>
            <div class="stat-label">Blockchain Blok</div>
            <div class="stat-help">Değiştirilemez güvenlik kaydı sayısı</div>
        </div>
        """, unsafe_allow_html=True)

    # Açıklama kutuları
    st.markdown("""
    <div class="info-box">
        <strong>🚨 Tehdit:</strong> Sistemdeki anormal aktiviteler (saldırı girişimleri, şüpheli trafik) &nbsp;|&nbsp;
        <strong>🤖 ML-IDS:</strong> Makine öğrenmesi ile otomatik tehdit tespiti &nbsp;|&nbsp;
        <strong>⛓️ Blockchain:</strong> Tüm olayların değiştirilemez kaydı
    </div>
    """, unsafe_allow_html=True)

    # Alertler bölümü - Sadece saldırı senaryolarında göster
    st.markdown(f"""
    <div class="section-title">
        🚨 Tespit Edilen Tehditler
        <span class="section-help">Güvenlik sistemi tarafından yakalanan saldırı girişimleri</span>
    </div>
    """, unsafe_allow_html=True)

    if filtered_alerts:
        # Severity özeti
        cols = st.columns(4)
        severity_config = {
            "CRITICAL": ("🔴", "#ef4444", "Kritik", "Sistem çökmesine neden olabilir"),
            "HIGH": ("🟠", "#f59e0b", "Yüksek", "Ciddi güvenlik açığı"),
            "MEDIUM": ("🟡", "#eab308", "Orta", "İzlenmesi gereken durum"),
            "LOW": ("🟢", "#22c55e", "Düşük", "Bilgilendirme amaçlı")
        }
        
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for alert in filtered_alerts:
            sev = alert.get("severity", "LOW")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        for i, (sev, count) in enumerate(severity_counts.items()):
            icon, color, label, desc = severity_config[sev]
            with cols[i]:
                st.markdown(f"""
                <div class="stat-card" style="border-left: 3px solid {color}; padding: 0.75rem;">
                    <div style="font-size: 1.25rem;">{icon} {count}</div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.75rem;">{label}</div>
                    <div style="color: rgba(255,255,255,0.4); font-size: 0.65rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Alert açıklamaları
        alert_explanations = {
            "MITM": "İletişim araya girme - Verileriniz izleniyor olabilir",
            "MANIPULATION": "Veri değişikliği - Bilgiler manipüle edilmiş olabilir",
            "FLOOD": "Aşırı yük saldırısı - Sistem yavaşlatılmaya çalışılıyor",
            "CAN_FLOOD": "Araç ağı saldırısı - CAN Bus aşırı yükleniyor",
            "REPLAY": "Tekrar saldırısı - Eski komutlar tekrar gönderildi",
            "ENTROPY": "Anormal veri - Şüpheli içerik tespit edildi",
            "RANSOMWARE": "Fidye yazılımı - Sistem ele geçirilmeye çalışılıyor",
            "FIRMWARE": "Sahte güncelleme - Zararlı yazılım enjeksiyonu",
            "SAMPLING": "Ölçüm manipülasyonu - Enerji verileri değiştirildi",
            "FAIL_OPEN": "Güvenlik bypass - Kontroller atlanıyor",
            "LATENCY": "Zamanlama saldırısı - Gecikmeler kötüye kullanılıyor",
            "POISONING": "Veri zehirleme - Sensörler yanıltılıyor",
            "SENSOR": "Sensör saldırısı - Ölçümler hatalı"
        }
        
        # Alert listesi
        for alert in filtered_alerts[:10]:
            severity = alert.get("severity", "LOW")
            alert_type = alert.get("type", alert.get("alert_type", "UNKNOWN"))
            description = alert.get("description", "Detay yok")
            timestamp = alert.get("timestamp_iso", alert.get("timestamp", ""))
            
            # Alert tipine göre açıklama
            explanation = ""
            for key, exp in alert_explanations.items():
                if key.upper() in alert_type.upper() or key.upper() in description.upper():
                    explanation = exp
                    break
            
            severity_class = f"alert-{severity.lower()}"
            badge_class = f"badge-{severity.lower()}"
            
            st.markdown(f"""
            <div class="alert-item {severity_class}">
                <div class="alert-header">
                    <span class="alert-type">{alert_type}</span>
                    <span class="severity-badge {badge_class}">{severity}</span>
                </div>
                <div class="alert-desc">{description}</div>
                {f'<div style="color: #60a5fa; font-size: 0.8rem; margin-top: 0.5rem;">💡 {explanation}</div>' if explanation else ''}
                <div class="alert-time" style="margin-top: 0.5rem; color: rgba(255,255,255,0.4);">🕐 {timestamp}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.05); border-radius: 16px; padding: 2.5rem; text-align: center; border: 1px dashed rgba(255,255,255,0.2);">
            <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🔍</div>
            <div style="color: rgba(255,255,255,0.8); font-size: 1rem;">Bu saldırı türüne ait tehdit tespit edilmedi</div>
            <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin-top: 0.5rem;">Saldırı çalıştırıldıktan sonra tehditler burada görünecek</div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem 0; margin-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">
    <div style="color: rgba(255,255,255,0.4); font-size: 0.85rem;">
        🔐 Elektrikli Araç Şarj İstasyonu Güvenlik Sistemi
    </div>
</div>
""", unsafe_allow_html=True)
