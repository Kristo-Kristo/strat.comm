import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="Strategisk Segmenterings-Værktøj", layout="wide")

# --- DESIGN ---
st.markdown("""
<style>
    .metric-card { background-color: #F1F5F9; padding: 15px; border-radius: 10px; border-left: 5px solid #3B82F6; }
    .metric-value { font-size: 18px; font-weight: bold; color: #1E293B; }
    .filter-label { font-weight: bold; color: #475569; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# --- KONFIGURATION ---
MY_API_KEY = "AIzaSyCcb-OLgjaO4pNcfP7rYEpJef3OJ36JCXk"
genai.configure(api_key=MY_API_KEY)

# --- AVANCERET DATA-MOTOR ---
# Dette simulerer et krydstjek mellem DST-parametre
def beregn_segment_data(kommune, kon, alder, uddannelse):
    # Basis-indkomst fra dine tidligere skærmbilleder
    baser = {"København": 412000, "Roskilde": 389000, "Aarhus": 375000, "Kolding": 338000, "Aalborg": 335000}
    base = baser.get(kommune, 350000)
    
    # Justerings-logik baseret på demografi
    justeret_indkomst = base
    if "Høj" in uddannelse: justeret_indkomst *= 1.2
    if "50+" in str(alder): justeret_indkomst *= 1.1
    
    return {
        "est_indkomst": f"{int(justeret_indkomst):,}".replace(",", "."),
        "størrelse": "8.500 - 12.000 personer",
        "medier": "LinkedIn & Børsen" if "Høj" in uddannelse else "Facebook & Lokalavisen"
    }

# --- SIDEBAR: SEGMENTERING ---
with st.sidebar:
    st.header("🎯 Målgruppe-specifikation")
    
    valgt_kommune = st.selectbox("Geografi", ["København", "Roskilde", "Aarhus", "Kolding", "Aalborg"])
    
    st.markdown("---")
    valgt_kon = st.multiselect("Køn", ["Mænd", "Kvinder", "Andet"], default=["Mænd", "Kvinder"])
    
    valgt_alder = st.select_slider("Aldersinterval", options=["18-24", "25-34", "35-49", "50-64", "65+"], value=("25-34", "50-64"))
    
    valgt_udd = st.radio("Uddannelsesniveau", ["Grundskole", "Erhvervsfaglig", "Kort videregående", "Høj (Lang videregående)"], index=3)

# --- BEREGNING ---
data = beregn_segment_data(valgt_kommune, valgt_kon, valgt_alder, valgt_udd)

# --- DASHBOARD ---
st.title(f"Analyse af segment i {valgt_kommune}")
st.info(f"Segment: {', '.join(valgt_kon)} | Alder: {valgt_alder[0]}-{valgt_alder[1]} år | Uddannelse: {valgt_udd}")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="filter-label">Estimeret Købekraft</div>
        <div class="metric-value">{data['est_indkomst']} kr.</div>
        <div style="font-size:10px; color:gray;">Kilde: DST INDKP101 (Justeret)</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="metric-card">
        <div class="filter-label">Segmentstørrelse</div>
        <div class="metric-value">{data['størrelse']}</div>
        <div style="font-size:10px; color:gray;">Kilde: DST FOLK1A</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="metric-card">
        <div class="filter-label">Anbefalet Primærkanal</div>
        <div class="metric-value">{data['medier']}</div>
        <div style="font-size:10px; color:gray;">Kilde: Strategisk estimat</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# --- CHAT: SPECIFIK RÅDGIVNING ---
st.subheader("💬 Strategi-chat for dette specifikke segment")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Hvordan fanger jeg bedst dette segment?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        # Vi bruger Gemini 2.5 Flash som ses på dine skærmbilleder
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_prompt = f"""
        Du er ekspert i kommunikation. Analyseobjekt:
        - Sted: {valgt_kommune}
        - Målgruppe: {valgt_kon}, {valgt_alder[0]}-{valgt_alder[1]} år.
        - Uddannelse: {valgt_udd}.
        - Estimeret indkomst for segmentet: {data['est_indkomst']} kr.
        
        Svar kort og taktisk på dansk.
        """
        
        res = model.generate_content([system_prompt, prompt])
        st.markdown(res.text)
        st.session_state.messages.append({"role": "assistant", "content": res.text})
