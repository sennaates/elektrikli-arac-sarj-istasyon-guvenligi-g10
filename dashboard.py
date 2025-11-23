"""
Streamlit Dashboard - Real-Time Monitoring
Blockchain, IDS ve CAN-Bus trafiğini görselleştirir.
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()


# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Secure OCPP-CAN Bridge",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# API URL
API_URL = "http://127.0.0.1:8000"  # Use 127.0.0.1 instead of localhost for better compatibility


# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
    }
    .alert-critical {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .alert-high {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .alert-medium {
        background-color: #fff9c4;
        border-left: 5px solid #ffeb3b;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .blockchain-valid {
        color: #4CAF50;
        font-weight: bold;
    }
    .blockchain-invalid {
        color: #f44336;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Helper functions

def fetch_api(endpoint: str):
    """API'den veri çek"""
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"API {response.status_code} hatası: {endpoint}")
            return None
    except requests.exceptions.ConnectionError:
        st.error(f"❌ API'ye bağlanılamıyor: {API_URL}")
        st.info("🔧 api_server.py çalışıyor mu kontrol edin!")
        return None
    except requests.exceptions.Timeout:
        st.error(f"⏱️ API zaman aşımı: {endpoint}")
        return None
    except Exception as e:
        st.error(f"❌ Beklenmeyen hata: {str(e)}")
        return None


def format_timestamp(ts: float) -> str:
    """Timestamp'i okunabilir formata çevir"""
    return datetime.fromtimestamp(ts).strftime("%H:%M:%S")


# Başlık
st.title("🔐 Secure OCPP-to-CAN Bridge Dashboard")
st.markdown("**Real-Time Monitoring | Blockchain-Secured | ML-Powered IDS**")
st.markdown("---")


# Sidebar
with st.sidebar:
    st.header("⚙️ Ayarlar")
    
    auto_refresh = st.checkbox("Otomatik Yenileme", value=True)
    refresh_interval = st.slider("Yenileme Süresi (sn)", 1, 10, 3)
    
    st.markdown("---")
    st.header("📊 Filtreler")
    
    show_alerts = st.checkbox("Alert'leri Göster", value=True)
    show_blockchain = st.checkbox("Blockchain'i Göster", value=True)
    show_traffic = st.checkbox("Trafik Analizi", value=True)
    
    st.markdown("---")
    
    # Health check
    health = fetch_api("/api/health")
    if health and health.get("status") == "healthy":
        st.success("✅ Sistem Çalışıyor")
    else:
        st.error("❌ Sistem Erişilemez")
    
    st.markdown("---")
    st.caption(f"API: {API_URL}")


# Ana içerik

# KPI Metrikleri
stats = fetch_api("/api/stats")

if stats is not None:  # Boş dict de geçerli (bridge çalışmıyor olabilir)
    # Eğer stats boşsa (bridge çalışmıyor), bilgi göster
    if not stats:
        st.info("ℹ️ Bridge henüz başlatılmamış. Veriler görünmeyecek. Bridge'i başlatmak için: `python secure_bridge.py`")
        st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        blockchain_stats = stats.get("blockchain", {})
        total_blocks = blockchain_stats.get("total_blocks", 0)
        st.metric(
            label="📦 Toplam Blok",
            value=total_blocks,
            delta=None
        )
    
    with col2:
        ids_stats = stats.get("ids", {})
        total_alerts = ids_stats.get("total_alerts", 0)
        st.metric(
            label="🚨 Toplam Alert",
            value=total_alerts,
            delta=None
        )
    
    with col3:
        total_can = ids_stats.get("total_can_frames", 0)
        unauthorized = ids_stats.get("unauthorized_can_frames", 0)
        st.metric(
            label="📡 CAN Frame",
            value=total_can,
            delta=f"-{unauthorized} yetkisiz" if unauthorized > 0 else "Tümü yetkili"
        )
    
    with col4:
        ml_stats = stats.get("ml", {})
        ml_trained = ml_stats.get("is_trained", False)
        ml_status = "✅ Aktif" if ml_trained else "⚠️ Eğitilmemiş"
        st.metric(
            label="🤖 ML-IDS",
            value=ml_status
        )
    
    st.markdown("---")
    
    # Alert Section
    if show_alerts:
        st.header("🚨 Real-Time Alerts")
        
        alerts = fetch_api("/api/alerts?count=10")
        
        if alerts and len(alerts) > 0:
            # Alert sayısı severity'ye göre
            alert_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for alert in alerts:
                severity = alert.get("severity", "LOW")
                alert_counts[severity] = alert_counts.get(severity, 0) + 1
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🔴 CRITICAL", alert_counts["CRITICAL"])
            col2.metric("🟠 HIGH", alert_counts["HIGH"])
            col3.metric("🟡 MEDIUM", alert_counts["MEDIUM"])
            col4.metric("🟢 LOW", alert_counts["LOW"])
            
            st.markdown("### Son Alert'ler")
            
            for alert in alerts[:5]:
                severity = alert.get("severity", "LOW")
                alert_type = alert.get("alert_type", "UNKNOWN")
                description = alert.get("description", "")
                timestamp = alert.get("timestamp_iso", "")
                
                if severity == "CRITICAL":
                    st.markdown(f"""
                    <div class="alert-critical">
                        <strong>🔴 CRITICAL</strong> | {alert_type} | {timestamp}<br>
                        {description}
                    </div>
                    """, unsafe_allow_html=True)
                elif severity == "HIGH":
                    st.markdown(f"""
                    <div class="alert-high">
                        <strong>🟠 HIGH</strong> | {alert_type} | {timestamp}<br>
                        {description}
                    </div>
                    """, unsafe_allow_html=True)
                elif severity == "MEDIUM":
                    st.markdown(f"""
                    <div class="alert-medium">
                        <strong>🟡 MEDIUM</strong> | {alert_type} | {timestamp}<br>
                        {description}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("✅ Hiç alert yok - Sistem güvenli")
        
        st.markdown("---")
    
    # Blockchain Section
    if show_blockchain:
        st.header("⛓️ Blockchain Durumu")
        
        blockchain_stats = stats.get("blockchain", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            is_valid = blockchain_stats.get("is_valid", False)
            status_class = "blockchain-valid" if is_valid else "blockchain-invalid"
            status_text = "✅ GEÇERLİ" if is_valid else "❌ GEÇERSİZ"
            
            st.markdown(f"**Blockchain Doğrulama:** <span class='{status_class}'>{status_text}</span>", 
                       unsafe_allow_html=True)
            
            st.markdown(f"**Genesis Hash:** `{blockchain_stats.get('genesis_hash', '')[:16]}...`")
            st.markdown(f"**En Son Hash:** `{blockchain_stats.get('latest_hash', '')[:16]}...`")
            st.markdown(f"**Dijital İmza:** {'✅ Etkin' if blockchain_stats.get('signature_enabled') else '❌ Devre Dışı'}")
        
        with col2:
            block_types = blockchain_stats.get("block_types", {})
            if block_types:
                # Pie chart
                fig = go.Figure(data=[go.Pie(
                    labels=list(block_types.keys()),
                    values=list(block_types.values()),
                    hole=.3
                )])
                fig.update_layout(
                    title="Blok Tipi Dağılımı",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Son bloklar
        st.markdown("### Son Bloklar")
        blocks = fetch_api("/api/blockchain/blocks?count=5")
        
        if blocks:
            block_data = []
            for block in blocks:
                block_data.append({
                    "Index": block.get("index"),
                    "Tip": block.get("data", {}).get("type", ""),
                    "Hash": block.get("hash", "")[:16] + "...",
                    "Önceki Hash": block.get("previous_hash", "")[:16] + "...",
                    "Timestamp": block.get("data", {}).get("timestamp_iso", "")
                })
            
            df = pd.DataFrame(block_data)
            st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
    
    # Traffic Analysis Section
    if show_traffic:
        st.header("📊 Trafik Analizi")
        
        ids_stats = stats.get("ids", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### CAN ID Frekansı")
            can_freq = ids_stats.get("can_id_frequency", {})
            if can_freq:
                df_can = pd.DataFrame([
                    {"CAN ID": k, "Sayı": v} 
                    for k, v in can_freq.items()
                ])
                fig = px.bar(df_can, x="CAN ID", y="Sayı", 
                           title="CAN Frame Frekansı")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Henüz CAN trafiği yok")
        
        with col2:
            st.markdown("### OCPP Action Frekansı")
            ocpp_freq = ids_stats.get("ocpp_action_frequency", {})
            if ocpp_freq:
                df_ocpp = pd.DataFrame([
                    {"Action": k, "Sayı": v}
                    for k, v in ocpp_freq.items()
                ])
                fig = px.bar(df_ocpp, x="Action", y="Sayı",
                           title="OCPP Komut Frekansı")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Henüz OCPP trafiği yok")
        
        st.markdown("---")
    
    # ML Model Section
    st.header("🤖 Makine Öğrenmesi")
    
    ml_stats = stats.get("ml", {})
    
    if ml_stats:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            is_trained = ml_stats.get("is_trained", False)
            status = "✅ Eğitilmiş" if is_trained else "❌ Eğitilmemiş"
            st.metric("Model Durumu", status)
        
        with col2:
            training_samples = ml_stats.get("training_samples", 0)
            st.metric("Eğitim Verisi", f"{training_samples} örnek")
        
        with col3:
            contamination = ml_stats.get("contamination", 0.1)
            st.metric("Anomali Oranı", f"{contamination:.1%}")
        
        # Eğitim butonu
        if st.button("🎓 Modeli Eğit", help="ML modelini mevcut verilerle eğitir"):
            with st.spinner("Model eğitiliyor..."):
                result = fetch_api("/api/ml/train")
                if result and result.get("status") == "success":
                    st.success(f"✅ {result.get('message')}")
                else:
                    st.error("❌ Model eğitimi başarısız")
    else:
        st.warning("ML-IDS devre dışı veya mevcut değil")

else:
    # API'ye bağlanılamadı (ConnectionError)
    st.error("❌ API'ye bağlanılamıyor!")
    st.info(f"API URL: {API_URL}")
    st.info("🔧 api_server.py çalışıyor mu kontrol edin!")
    st.info("💡 Terminal'de: `ps aux | grep api_server`")


# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()


# Footer
st.markdown("---")
st.caption("🔐 Secure OCPP-CAN Bridge | University IoT Security Project | 2024")

