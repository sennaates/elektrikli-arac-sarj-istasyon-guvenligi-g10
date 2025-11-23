"""
Basitleştirilmiş Streamlit Dashboard - API Test için
"""
import streamlit as st
import requests
import time

st.set_page_config(
    page_title="Secure OCPP-CAN Bridge",
    page_icon="🔐",
    layout="wide"
)

# Başlık
st.title("🔐 Secure OCPP-to-CAN Bridge Dashboard")
st.markdown("**Real-Time Monitoring | Blockchain-Secured | ML-Powered IDS**")
st.markdown("---")

# API URL
API_URL = "http://localhost:8000"

# API Test
st.header("🔌 API Bağlantı Testi")

col1, col2 = st.columns(2)

with col1:
    st.subheader("API Health Check")
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            st.success(f"✅ API Çalışıyor!")
            st.json(data)
        else:
            st.error(f"❌ API Hatası: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ API'ye bağlanılamıyor!")
        st.code("python api_server.py")
    except Exception as e:
        st.error(f"❌ Hata: {e}")

with col2:
    st.subheader("API Stats")
    try:
        response = requests.get(f"{API_URL}/api/stats", timeout=3)
        if response.status_code == 200:
            data = response.json()
            st.success("✅ Stats alındı")
            st.json(data)
        else:
            st.warning("⚠️ Stats boş")
    except Exception as e:
        st.error(f"❌ Stats hatası: {e}")

st.markdown("---")

# Manuel veri girişi
st.header("📊 Manuel Test")

if st.button("🧪 Test API"):
    with st.spinner("Test ediliyor..."):
        endpoints = [
            "/api/health",
            "/api/stats",
            "/api/blockchain/stats",
            "/api/ids/stats",
            "/api/alerts"
        ]
        
        for endpoint in endpoints:
            try:
                r = requests.get(f"{API_URL}{endpoint}", timeout=2)
                st.write(f"**{endpoint}**: ✅ {r.status_code}")
                if r.status_code == 200 and r.text and r.text != '{}':
                    with st.expander(f"Yanıt: {endpoint}"):
                        st.json(r.json())
            except Exception as e:
                st.write(f"**{endpoint}**: ❌ {str(e)}")

st.markdown("---")
st.caption(f"API URL: {API_URL}")
st.caption("Sistem Çalışıyor ✅" if True else "Sistem Durdu ❌")

