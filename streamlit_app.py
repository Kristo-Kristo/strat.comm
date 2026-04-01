import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="Strategisk Business Intelligence", layout="wide")

# --- DESIGN & STYLING ---
st.markdown("""
<style>
    .metric-card { background-color: #F8FAFC; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0; height: 100%; }
    .metric-value { font-size: 22px; font-weight: bold; color: #1E293B; margin: 5px 0; }
    .source-label { font-size: 11px; color: #94A3B8; font-style: italic; }
    .section-header { font-size: 1.8rem; font-weight: bold; color: #1E3A8A; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# --- KONFIGURATION ---
MY_API_KEY = "AIzaSyCcb-OLgjaO4pNcfP7rYEpJef3OJ36JCXk"
genai.configure(api_key=MY_API_KEY)

# --- UDVIDET DATASET (Kommunikations-fokuseret) ---
KOMMUNE_DATA = {
    "København": {
        "indkomst": "412.560", "uddannelse": "Høj (52% m. lang videregående)", 
        "alder_fokus": "18-35 år", "digitale_vaner": "Instagram & LinkedIn", "kilde": "DST INDKP101 & HFUDD10"
    },
    "Roskilde": {
        "indkomst": "389.200", "uddannelse": "Middel (38% m. videregående)", 
        "alder_fokus": "30-50 år", "digitale_vaner": "Facebook & Nyhedsbreve", "kilde": "DST INDKP101 & HFUDD10"
    },
    "Aarhus": {
        "indkomst": "375.400", "uddannelse": "Høj (48% m. videregående)", 
        "alder_fokus": "20-40 år", "digitale_vaner": "Instagram & TikTok", "kilde": "DST INDKP101 & HFUDD10"
    },
    "Kolding": {
        "indkomst": "338.900", "uddannelse": "Middel (32% faglærte)", 
        "alder_fokus": "35-55 år", "digitale_vaner": "Facebook & Lokalaviser", "kilde": "DST INDKP101 & HFUDD10"
    }
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("Kontrolpanel")
    valgt_navn = st.selectbox("Vælg målgruppe-område:", list(KOMMUNE_DATA.keys()))
    info = KOMMUNE_DATA[valgt_navn]
    st.divider()
    st.info("📊 Data er baseret på seneste DST-udtræk (2022/23)")

# --- DASHBOARD ---
st.markdown(f"<div class='section-header'>Strategisk Målgruppeanalyse: {valgt_navn}</div>", unsafe_allow_html=True)

# Række 1: Økonomi og Uddannelse
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.markdown(f"""<div class="metric-card">
        <div style="color:#64748B; font-size:14px;">Købekraft (Gns. Disp. Indkomst)</div>
        <div class="metric-value">{info['indkomst']} kr.</div>
        <div class="source-label">Kilde: {info['kilde']}</div>
    </div>""", unsafe_allow_html=True)

with row1_col2:
    st.markdown(f"""<div class="metric-card">
        <div style="color:#64748B; font-size:14px;">Uddannelsesprofil</div>
        <div class="metric-value">{info['uddannelse']}</div>
        <div class="source-label">Kilde: DST HFUDD10</div>
    </div>""", unsafe_allow_html=True)

st.write("") # Mellemrum

# Række 2: Kampagne-indsigt
row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    st.markdown(f"""<div class="metric-card">
        <div style="color:#64748B; font-size:14px;">Primær Aldersgruppe</div>
        <div class="metric-value">{info['alder_fokus']}</div>
        <div class="source-label">Kilde: DST FOLK1A</div>
    </div>""", unsafe_allow_html=True)

with row2_col2:
    st.markdown(f"""<div class="metric-card">
        <div style="color:#64748B; font-size:14px;">Digitale Kanalpræferencer</div>
        <div class="metric-value">{info['digitale_vaner']}</div>
        <div class="source-label">Kilde: Estimat baseret på segmentering</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# --- STRATEGISK CHAT ---
st.subheader("🤖 Strategisk Rådgivning")
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Spørg om kampagneforslag til denne målgruppe..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        model = genai.GenerativeModel('gemini-2.5-flash')
        kontekst = f"""
        Du er kampagnestrateg. For {valgt_navn} har vi disse data:
        Indkomst: {info['indkomst']} kr.
        Uddannelse: {info['uddannelse']}
        Kanaler: {info['digitale_vaner']}
        
        Giv konkrete råd til tone-of-voice og kanalvalg baseret på disse kilder.
        """
        res = model.generate_content([kontekst, prompt])
        st.markdown(res.text)
        st.session_state.messages.append({"role": "assistant", "content": res.text})
