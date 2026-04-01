import streamlit as st
import pandas as pd
import requests
import io
import google.generativeai as genai

st.set_page_config(page_title="Strategisk Business Intelligence", layout="wide")

# --- DESIGN ---
st.markdown("""
<style>
    .metric-card { background-color: #F8FAFC; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0; }
    .metric-value { font-size: 24px; font-weight: bold; color: #1E293B; }
</style>
""", unsafe_allow_html=True)

# --- KONFIGURATION ---
MY_API_KEY = "AIzaSyCcb-OLgjaO4pNcfP7rYEpJef3OJ36JCXk"
genai.configure(api_key=MY_API_KEY)

# --- KOMMUNER & DATA (Udvidet liste) ---
KOMMUNE_DATA = {
    "København": {"kode": "101", "indkomst": "412.560", "sektor": "Videnerhverv", "aktivitet": 90},
    "Roskilde": {"kode": "265", "indkomst": "389.200", "sektor": "Handel & Industri", "aktivitet": 75},
    "Aarhus": {"kode": "751", "indkomst": "375.400", "sektor": "IT & Uddannelse", "aktivitet": 85},
    "Odense": {"kode": "461", "indkomst": "342.100", "sektor": "Robot-teknologi", "aktivitet": 70},
    "Kolding": {"kode": "621", "indkomst": "338.900", "sektor": "Logistik & Handel", "aktivitet": 65},
    "Aalborg": {"kode": "851", "indkomst": "335.200", "sektor": "Industri & Energi", "aktivitet": 68}
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("Kontrolpanel")
    valgt_navn = st.selectbox("Vælg område:", list(KOMMUNE_DATA.keys()))
    info = KOMMUNE_DATA[valgt_navn]
    st.divider()
    st.success("🤖 Gemini 2.5 Flash Aktiv")

# --- DASHBOARD OPSÆTNING ---
st.title(f"Strategisk Analyse: {valgt_navn}")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""<div class="metric-card">
        <div style="color:gray; font-size:14px;">Gns. Disp. Indkomst</div>
        <div class="metric-value">{info['indkomst']} kr.</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="metric-card">
        <div style="color:gray; font-size:14px;">Dominerende Sektor</div>
        <div class="metric-value">{info['sektor']}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="metric-card">
        <div style="color:gray; font-size:14px;">Aktivitetsniveau</div>
        <div class="metric-value">{info['aktivitet']}%</div>
        <div style="background:#E2E8F0; height:8px; border-radius:4px; margin-top:10px;">
            <div style="background:#3B82F6; width:{info['aktivitet']}%; height:100%; border-radius:4px;"></div>
        </div>
    </div>""", unsafe_allow_html=True)

st.divider()

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Spørg Gemini om strategien..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Vi bruger Gemini 2.5 Flash som bekræftet i din sidebar
            model = genai.GenerativeModel('gemini-2.5-flash')
            kontekst = f"Du rådgiver om {valgt_navn}. Indkomst: {info['indkomst']} kr. Sektor: {info['sektor']}. Svar på dansk."
            res = model.generate_content([kontekst, prompt])
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
        except Exception as e:
            st.error(f"Chat-fejl: {e}")
