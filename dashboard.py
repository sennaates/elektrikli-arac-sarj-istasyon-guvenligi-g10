"""
Modern Streamlit Dashboard - Real-Time Monitoring
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
API_URL = "http://127.0.0.1:8000"

# Modern CSS - Glassmorphism & Gradient Design
st.markdown("""
<style>
    /* Ana Stil - Daha açık arka plan */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
    }
    
    /* Streamlit'in varsayılan arka planını override et */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header Stil */
    .main-header {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    /* Modern Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px 0 rgba(31, 38, 135, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #4b5563;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Alert Cards */
    .alert-card {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.15);
        border-left: 4px solid;
        transition: all 0.3s ease;
    }
    
    .alert-card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px 0 rgba(31, 38, 135, 0.25);
    }
    
    .alert-critical {
        border-left-color: #ef4444;
        background: rgba(255, 255, 255, 0.98);
    }
    
    .alert-high {
        border-left-color: #f59e0b;
        background: rgba(255, 255, 255, 0.98);
    }
    
    .alert-medium {
        border-left-color: #eab308;
        background: rgba(255, 255, 255, 0.98);
    }
    
    .alert-low {
        border-left-color: #10b981;
        background: rgba(255, 255, 255, 0.98);
    }
    
    /* Section Headers */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 2rem 0 1rem 0;
        font-size: 1.5rem;
        font-weight: 700;
        box-shadow: 0 4px 16px 0 rgba(102, 126, 234, 0.3);
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    /* Blockchain Status */
    .blockchain-status {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.15);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .status-valid {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .status-invalid {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }
    
    /* Sidebar yazı renkleri */
    [data-testid="stSidebar"] label {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stCheckbox label {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stSlider label {
        color: white !important;
    }
    
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stCaption {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Badge Styling */
    .severity-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-critical {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    .badge-high {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .badge-medium {
        background: linear-gradient(135deg, #eab308 0%, #ca8a04 100%);
        color: white;
    }
    
    .badge-low {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 3rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        margin: 2rem 0;
        color: #1f2937;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #4b5563;
        font-size: 0.9rem;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 12px;
        margin-top: 2rem;
    }
    
    /* Tüm yazıların okunabilir olması için */
    h1, h2, h3, h4, h5, h6 {
        color: #1f2937 !important;
    }
    
    p, span, div {
        color: #1f2937;
    }
    
    /* Tablo yazıları */
    .dataframe {
        background: rgba(255, 255, 255, 0.98) !important;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    .dataframe td {
        color: #1f2937 !important;
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
            return None
    except Exception as e:
        return None

def format_timestamp(ts: float) -> str:
    """Timestamp'i okunabilir formata çevir"""
    return datetime.fromtimestamp(ts).strftime("%H:%M:%S")

def create_metric_card(label: str, value, delta=None, icon="📊"):
    """Modern metric card oluştur"""
    delta_html = ""
    if delta:
        delta_color = "#ef4444" if isinstance(delta, str) and "-" in str(delta) else "#10b981"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.9rem; margin-top: 0.5rem;">{delta}</div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

# Modern Header
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem; font-weight: 800;">
        🔐 Secure OCPP-to-CAN Bridge
    </h1>
    <p style="margin: 0.5rem 0 0 0; color: #6c757d; font-size: 1.1rem;">
        Real-Time Monitoring | Blockchain-Secured | ML-Powered IDS
    </p>
</div>
""", unsafe_allow_html=True)

# Modern Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="color: white; margin: 0;">⚙️ Kontrol Paneli</h2>
    </div>
    """, unsafe_allow_html=True)
    
    auto_refresh = st.checkbox("🔄 Otomatik Yenileme", value=True)
    refresh_interval = st.slider("⏱️ Yenileme Süresi (sn)", 1, 10, 3)
    
    st.markdown("---")
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h3 style="color: white; margin: 0;">📊 Filtreler</h3>
    </div>
    """, unsafe_allow_html=True)
    
    show_alerts = st.checkbox("🚨 Alert'ler", value=True)
    show_blockchain = st.checkbox("⛓️ Blockchain", value=True)
    show_traffic = st.checkbox("📡 Trafik", value=True)
    show_ml = st.checkbox("🤖 ML-IDS", value=True)
    
    st.markdown("---")
    
    # Health check
    health = fetch_api("/api/health")
    if health and health.get("status") == "healthy":
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.2); padding: 1rem; border-radius: 12px; text-align: center;">
            <div style="color: #10b981; font-weight: 700; font-size: 1.1rem;">✅ Sistem Aktif</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.2); padding: 1rem; border-radius: 12px; text-align: center;">
            <div style="color: #ef4444; font-weight: 700; font-size: 1.1rem;">❌ Sistem Erişilemez</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption(f"🌐 API: {API_URL}")

# Ana içerik
stats = fetch_api("/api/stats")

if stats is not None:
    if not stats:
        st.info("ℹ️ Bridge henüz başlatılmamış. Veriler görünmeyecek.")
        st.markdown("---")
    
    # Modern KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        blockchain_stats = stats.get("blockchain", {})
        total_blocks = blockchain_stats.get("total_blocks", 0)
        st.markdown(create_metric_card("Toplam Blok", total_blocks, icon="📦"), unsafe_allow_html=True)
    
    with col2:
        ids_stats = stats.get("ids", {})
        total_alerts = ids_stats.get("total_alerts", 0)
        st.markdown(create_metric_card("Toplam Alert", total_alerts, icon="🚨"), unsafe_allow_html=True)
    
    with col3:
        total_can = ids_stats.get("total_can_frames", 0)
        unauthorized = ids_stats.get("unauthorized_can_frames", 0)
        delta = f"-{unauthorized} yetkisiz" if unauthorized > 0 else "Tümü yetkili"
        st.markdown(create_metric_card("CAN Frame", total_can, delta=delta, icon="📡"), unsafe_allow_html=True)
    
    with col4:
        ml_stats = stats.get("ml", {})
        ml_trained = ml_stats.get("is_trained", False)
        ml_status = "✅ Aktif" if ml_trained else "⚠️ Eğitilmemiş"
        st.markdown(create_metric_card("ML-IDS", ml_status, icon="🤖"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Alert Section
    if show_alerts:
        st.markdown('<div class="section-header">🚨 Real-Time Alerts</div>', unsafe_allow_html=True)
        
        alerts = fetch_api("/api/alerts?count=10")
        
        if alerts and len(alerts) > 0:
            # Severity distribution cards
            alert_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for alert in alerts:
                severity = alert.get("severity", "LOW")
                alert_counts[severity] = alert_counts.get(severity, 0) + 1
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card" style="border-left: 4px solid #ef4444;">
                    <div class="metric-label">🔴 CRITICAL</div>
                    <div class="metric-value">{alert_counts["CRITICAL"]}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card" style="border-left: 4px solid #f59e0b;">
                    <div class="metric-label">🟠 HIGH</div>
                    <div class="metric-value">{alert_counts["HIGH"]}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card" style="border-left: 4px solid #eab308;">
                    <div class="metric-label">🟡 MEDIUM</div>
                    <div class="metric-value">{alert_counts["MEDIUM"]}</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                <div class="metric-card" style="border-left: 4px solid #10b981;">
                    <div class="metric-label">🟢 LOW</div>
                    <div class="metric-value">{alert_counts["LOW"]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 📋 Son Alert'ler")
            
            for alert in alerts[:10]:
                severity = alert.get("severity", "LOW")
                alert_type = alert.get("alert_type", "UNKNOWN")
                description = alert.get("description", "")
                timestamp = alert.get("timestamp_iso", alert.get("timestamp", ""))
                
                severity_class = f"alert-{severity.lower()}"
                badge_class = f"badge-{severity.lower()}"
                
                st.markdown(f"""
                <div class="alert-card {severity_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span class="severity-badge {badge_class}">{severity}</span>
                        <span style="color: #4b5563; font-size: 0.85rem; font-weight: 500;">{timestamp}</span>
                    </div>
                    <div style="font-weight: 700; color: #1f2937; margin-bottom: 0.5rem; font-size: 1rem;">{alert_type}</div>
                    <div style="color: #374151; font-size: 0.95rem; line-height: 1.5;">{description}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div style="font-size: 4rem; margin-bottom: 1rem;">✅</div>
                <h3 style="color: #10b981; margin: 0;">Sistem Güvenli</h3>
                <p style="color: #6c757d; margin: 0.5rem 0 0 0;">Hiç alert yok</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Blockchain Section
    if show_blockchain:
        st.markdown('<div class="section-header">⛓️ Blockchain Durumu</div>', unsafe_allow_html=True)
        
        blockchain_stats = stats.get("blockchain", {})
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="blockchain-status">
            """, unsafe_allow_html=True)
            
            is_valid = blockchain_stats.get("is_valid", False)
            status_class = "status-valid" if is_valid else "status-invalid"
            status_text = "✅ GEÇERLİ" if is_valid else "❌ GEÇERSİZ"
            
            st.markdown(f"""
            <div style="margin-bottom: 1.5rem;">
                <div style="font-size: 0.9rem; color: #4b5563; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Blockchain Doğrulama</div>
                <span class="status-badge {status_class}">{status_text}</span>
            </div>
            """, unsafe_allow_html=True)
            
            genesis_hash = blockchain_stats.get('genesis_hash', '')[:20]
            latest_hash = blockchain_stats.get('latest_hash', '')[:20]
            
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <div style="font-size: 0.9rem; color: #4b5563; margin-bottom: 0.5rem; font-weight: 600;">Genesis Hash</div>
                <div style="font-family: monospace; background: rgba(102, 126, 234, 0.15); padding: 0.75rem; border-radius: 8px; font-size: 0.9rem; color: #1f2937; border: 1px solid rgba(102, 126, 234, 0.3);">{genesis_hash}...</div>
            </div>
            <div style="margin-bottom: 1rem;">
                <div style="font-size: 0.9rem; color: #4b5563; margin-bottom: 0.5rem; font-weight: 600;">En Son Hash</div>
                <div style="font-family: monospace; background: rgba(102, 126, 234, 0.15); padding: 0.75rem; border-radius: 8px; font-size: 0.9rem; color: #1f2937; border: 1px solid rgba(102, 126, 234, 0.3);">{latest_hash}...</div>
            </div>
            """, unsafe_allow_html=True)
            
            signature_enabled = blockchain_stats.get('signature_enabled', False)
            sig_status = "✅ Etkin" if signature_enabled else "❌ Devre Dışı"
            sig_color = "#10b981" if signature_enabled else "#ef4444"
            
            st.markdown(f"""
            <div>
                <div style="font-size: 0.9rem; color: #4b5563; margin-bottom: 0.5rem; font-weight: 600;">Dijital İmza</div>
                <div style="color: {sig_color}; font-weight: 700; font-size: 1.1rem;">{sig_status}</div>
            </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            block_types = blockchain_stats.get("block_types", {})
            if block_types:
                fig = go.Figure(data=[go.Pie(
                    labels=list(block_types.keys()),
                    values=list(block_types.values()),
                    hole=0.4,
                    marker=dict(colors=['#667eea', '#764ba2', '#f59e0b', '#10b981', '#ef4444'])
                )])
                fig.update_layout(
                    title=dict(text="Blok Tipi Dağılımı", font=dict(size=18, color="#1f2937")),
                    height=350,
                    showlegend=True,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Henüz blok tipi verisi yok")
        
        # Son bloklar
        st.markdown("### 📋 Son Bloklar")
        blocks = fetch_api("/api/blockchain/blocks?count=10")
        
        if blocks and len(blocks) > 0:
            block_data = []
            for block in blocks:
                # Sadece geçerli blokları ekle
                if block and block.get("index") is not None:
                    block_type = block.get("data", {}).get("type", block.get("block_type", "N/A"))
                    block_hash = block.get("hash", "")
                    prev_hash = block.get("previous_hash", "")
                    timestamp = block.get("timestamp", 0)
                    
                    block_data.append({
                        "Index": block.get("index"),
                        "Tip": block_type,
                        "Hash": block_hash[:20] + "..." if block_hash else "N/A",
                        "Önceki Hash": prev_hash[:20] + "..." if prev_hash else "N/A",
                        "Zaman": format_timestamp(timestamp) if timestamp else "N/A"
                    })
            
            if block_data:
                df = pd.DataFrame(block_data)
                # Sadece veri olan satırları göster, height parametresini kaldır
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Henüz blok verisi yok")
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Traffic Analysis Section
    if show_traffic:
        st.markdown('<div class="section-header">📊 Trafik Analizi</div>', unsafe_allow_html=True)
        
        ids_stats = stats.get("ids", {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📡 CAN ID Frekansı")
            can_freq = ids_stats.get("can_id_frequency", {})
            if can_freq:
                df_can = pd.DataFrame([
                    {"CAN ID": hex(k) if isinstance(k, int) else k, "Sayı": v} 
                    for k, v in can_freq.items()
                ])
                fig = px.bar(
                    df_can, 
                    x="CAN ID", 
                    y="Sayı",
                    color="Sayı",
                    color_continuous_scale="viridis",
                    title="CAN Frame Frekansı"
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#1f2937")
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown("""
                <div class="empty-state">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">📡</div>
                    <p style="color: #6c757d;">Henüz CAN trafiği yok</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### ⚡ OCPP Action Frekansı")
            ocpp_freq = ids_stats.get("ocpp_action_frequency", {})
            if ocpp_freq:
                df_ocpp = pd.DataFrame([
                    {"Action": k, "Sayı": v}
                    for k, v in ocpp_freq.items()
                ])
                fig = px.bar(
                    df_ocpp, 
                    x="Action", 
                    y="Sayı",
                    color="Sayı",
                    color_continuous_scale="plasma",
                    title="OCPP Komut Frekansı"
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#1f2937")
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown("""
                <div class="empty-state">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">⚡</div>
                    <p style="color: #6c757d;">Henüz OCPP trafiği yok</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # ML Model Section
    if show_ml:
        st.markdown('<div class="section-header">🤖 Makine Öğrenmesi</div>', unsafe_allow_html=True)
        
        ml_stats = stats.get("ml", {})
        
        if ml_stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                is_trained = ml_stats.get("is_trained", False)
                status = "✅ Eğitilmiş" if is_trained else "⚠️ Eğitilmemiş"
                status_color = "#10b981" if is_trained else "#f59e0b"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Model Durumu</div>
                    <div style="color: {status_color}; font-size: 1.5rem; font-weight: 700; margin-top: 0.5rem;">{status}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                training_samples = ml_stats.get("training_samples", 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Eğitim Verisi</div>
                    <div class="metric-value">{training_samples}</div>
                    <div style="color: #6c757d; font-size: 0.9rem; margin-top: 0.5rem;">örnek</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                contamination = ml_stats.get("contamination", 0.1)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Anomali Oranı</div>
                    <div class="metric-value">{contamination:.1%}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Eğitim butonu
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🎓 Modeli Eğit", use_container_width=True, type="primary"):
                    with st.spinner("Model eğitiliyor..."):
                        result = fetch_api("/api/ml/train")
                        if result and result.get("status") == "success":
                            st.success(f"✅ {result.get('message')}")
                            st.rerun()
                        else:
                            st.error("❌ Model eğitimi başarısız")
        else:
            st.warning("⚠️ ML-IDS devre dışı veya mevcut değil")

else:
    st.error("❌ API'ye bağlanılamıyor!")
    st.info(f"🌐 API URL: {API_URL}")
    st.info("🔧 api_server.py çalışıyor mu kontrol edin!")

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Modern Footer
st.markdown("""
<div class="footer">
    🔐 Secure OCPP-CAN Bridge | University IoT Security Project | 2024
</div>
""", unsafe_allow_html=True)
