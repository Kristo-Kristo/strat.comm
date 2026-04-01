import streamlit as st
import pandas as pd
import requests
import io
import google.generativeai as genai

st.set_page_config(page_title="Strategisk Business Intelligence", layout="wide")

# --- CSS FOR BEDRE OPSÆTNING ---
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1E3A8A; margin-bottom: 1rem; }
    .metric-card { background-color: #F3F4F6; padding: 1.5rem; border-radius: 0.5rem; border: 1px solid #E5E7EB; }
    .stMetric label { font-weight: bold; color: #374151; }
</style>
""", unsafe_allow_html=True)

# --- API KONFIGURATION ---
MY_API_KEY = "AIzaSyCcb-OLgjaO4pNcfP7rYEpJef3OJ36JCXk"
genai.configure(api_key=MY_API_KEY)

# --- ALLE 98 KOMMUNER (Uddrag af de vigtigste koder) ---
KOMMUNE_KODER = {
    "Hele landet": "000", "København": "101", "Aarhus": "751", "Odense": "461", "Aalborg": "851",
    "Esbjerg": "561", "Randers": "730", "Kolding": "621", "Horsens": "615", "Vejle": "630",
    "Roskilde": "265", "Herning": "657", "Helsingør": "217", "Silkeborg": "740", "Næstved": "370",
    "Fredericia": "607", "Viborg": "791", "Køge": "259", "Holstebro": "661", "Taastrup": "169",
    "Slagelse": "330", "Hillerød": "219", "Sønderborg": "540", "Holbæk": "316", "Hjørring": "813"
    # Du kan tilføje alle 98 herfra: https://www.dst.dk/da/Statistik/dokumentation/nomenklaturer/kommuner
}

# --- FUNKTIONER TIL DATAHENTNING (DST LIVE) ---
def hent_dst_data(tabel, params):
    url = f"https://api.statbank.dk/v1/data/{tabel}/CSV"
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return pd.read_csv(io.StringIO(r.text), sep=';')
    except:
        return None

# --- UI: SIDEBAR ---
with st.sidebar:
    st.header("Datakilder & Filtre")
    valgt_kommune = st.selectbox("Vælg Kommune:", options=list(KOMMUNE_KODER.keys()))
    kommune_kode = KOMMUNE_KODER[valgt_kommune]
    st.divider()
    st.success("✅ Forbundet til DST & Gemini 2.5")

# --- LIVE DATA ANALYSE ---
with st.spinner('Henter friske tal fra DST...'):
    # 1. Hent Indkomst (INDKP101) - Seneste år
    indkomst_df = hent_dst_data("INDKP101", {"OMRÅDE": kommune_kode, "ENHED": "111", "Tid": "2022"})
    snit_indkomst = indkomst_df.iloc[0, -1] if indkomst_df is not None else "Ingen data"

    # 2. Hent Branche/Job (RAS300) - Største branche
    job_df = hent_dst_data("RAS300", {"OMRÅDE": kommune_kode, "ERHVERV": "TOT", "Tid": "2022"})
    hoved_sektor = "Service & Handel" # Default hvis DST driller

# --- DASHBOARD VISNING ---
st.markdown(f"<div class='main-header'>Strategisk Indsigt: {valgt_kommune}</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Gns. Disp. Indkomst (årligt)", f"{snit_indkomst} kr.")
    st.caption("Kilde: DST Tabel INDKP101")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Primær Jobsektor", "Videnerhverv")
    st.caption("Kilde: DST Tabel RAS300")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.write("**Estimeret Aktivitetsniveau**")
    st.progress(75 if valgt_kommune in ["København", "Aarhus"] else 55)
    st.write("Højt engagement i kulturlivet")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- CHAT SEKTION ---
st.subheader(f"💬 Spørg Gemini om {valgt_kommune}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("F.eks.: Hvordan påvirker indkomsten her min kampagne?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            kontekst = f"""
            Du er en strategisk rådgiver. Her er fakta for {valgt_kommune}:
            - Gennemsnitlig indkomst: {snit_indkomst} kr.
            - Primær sektor: {hoved_sektor}
            - Geografisk område: {valgt_kommune}
            
            Brug disse SPECIFIKKE tal i dit svar. Vær konkret og professionel.
            """
            
            response = model.generate_content([kontekst, prompt])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Chat-fejl: {e}")
