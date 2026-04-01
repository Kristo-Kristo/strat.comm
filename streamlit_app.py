import streamlit as st
import pandas as pd
import requests

# Sæt sidens titel
st.set_page_config(page_title="Målgruppe-Analysatoren", layout="wide")

st.title("📊 Strategisk Målgruppe-Dashboard")
st.subheader("Data direkte fra Danmarks Statistik")

# Funktion til at hente data fra DST API
def hent_dst_data(kommune_kode="000"):
    url = "https://api.statbank.dk/v1/data/FOLK1A/JSONSTAT"
    
    forespørgsel = {
        "table": "folk1a",
        "format": "jsonstat",
        "variables": [
            {"code": "OMRÅDE", "values": [kommune_kode]},
            {"code": "ALDER", "values": ["IALT", "0-6", "7-16", "17-24", "25-44", "45-66", "67+"]}
        ]
    }
    
    respons = requests.post(url, json=forespørgsel)
    data = respons.json()
    
    værdier = data['dataset']['value']
    labels = ["I alt", "0-6 år", "7-16 år", "17-24 år", "25-44 år", "45-66 år", "67+ år"]
    
    return pd.DataFrame({"Aldersgruppe": labels, "Antal": værdier})

# Sidebjælke til valg af kommune
st.sidebar.header("Indstillinger")
kommune_navn = st.sidebar.selectbox(
    "Vælg en kommune:",
    ["Hele landet", "København", "Aarhus", "Odense", "Aalborg"]
)

kommuner = {"Hele landet": "000", "København": "101", "Aarhus": "751", "Odense": "461", "Aalborg": "851"}
valgt_kode = kommuner[kommune_navn]

try:
    df = hent_dst_data(valgt_kode)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write(f"### Tal for {kommune_navn}")
        st.table(df)
        
    with col2:
        st.write("### Visuel fordeling")
        st.bar_chart(df.set_index("Aldersgruppe").drop("I alt"))

except Exception as e:
    st.error(f"Der skete en fejl: {e}")
