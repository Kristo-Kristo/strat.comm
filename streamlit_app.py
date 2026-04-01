import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Målgruppe-Analysatoren", layout="wide")

st.title("📊 Strategisk Målgruppe-Dashboard")
st.subheader("Data direkte fra Danmarks Statistik")

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
    
    # Vi tilføjer 'headers' for at fortælle DST hvem vi er (standard procedure)
    headers = {'User-Agent': 'MaalgruppeApp/1.0 (kristokristo@example.com)'}
    
    respons = requests.post(url, json=forespørgsel, headers=headers)
    
    if respons.status_code == 200:
        data = respons.json()
        # Vi tjekker om 'dataset' findes, ellers kigger vi direkte i json
        root = data.get('dataset', data) 
        værdier = root['value']
        labels = ["I alt", "0-6 år", "7-16 år", "17-24 år", "25-44 år", "45-66 år", "67+ år"]
        return pd.DataFrame({"Aldersgruppe": labels, "Antal": værdier})
    else:
        st.error(f"Fejl ved hentning: Statuskode {respons.status_code}")
        return None

st.sidebar.header("Indstillinger")
kommune_navn = st.sidebar.selectbox(
    "Vælg en kommune:",
    ["Hele landet", "København", "Aarhus", "Odense", "Aalborg"]
)

kommuner = {"Hele landet": "000", "København": "101", "Aarhus": "751", "Odense": "461", "Aalborg": "851"}
valgt_kode = kommuner[kommune_navn]

df = hent_dst_data(valgt_kode)

if df is not None:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write(f"### Tal for {kommune_navn}")
        st.table(df)
    with col2:
        st.write("### Visuel fordeling")
        st.bar_chart(df.set_index("Aldersgruppe").drop("I alt"))
