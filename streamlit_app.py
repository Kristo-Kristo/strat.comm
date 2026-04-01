import streamlit as st
import pandas as pd
import requests
import io
import google.generativeai as genai

st.set_page_config(page_title="Strategisk Gemini-Rådgiver", layout="wide")

# CSS til at gøre chat-interfacet pænere
st.markdown("""
<style>
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("♊ Strategisk Gemini-Chat")
st.subheader("Data fra DST + Intelligent AI-Rådgivning")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Indstillinger")
    google_api_key = st.text_input("Indsæt din Gemini API-nøgle:", type="password")
    kommune_navn = st.selectbox("Vælg Kommune:", ["Hele landet", "København", "Aarhus", "Odense", "Aalborg"])
    st.info("Hent din gratis nøgle på aistudio.google.com")

# --- DATA HENTNING (Skudsikker metode) ---
kommuner = {"Hele landet": "000", "København": "101", "Aarhus": "751", "Odense": "461", "Aalborg": "851"}

def hent_data(kode):
    url = f"https://api.statbank.dk/v1/data/FOLK1A/CSV?OMRÅDE={kode}&ALDER=IALT,0-6,7-16,17-24,25-44,45-66,67+&Tid=2023K4"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            df = pd.read_csv(io.StringIO(r.text), sep=';')
            df.columns = ['Område', 'Aldersgruppe', 'Tid', 'Antal']
            return df
        return None
    except:
        return None

df = hent_data(kommuner[kommune_navn])

# Hvis DST fejler, bruger vi demodata så appen stadig kan køre
if df is None:
    st.warning("⚠️ DST server
