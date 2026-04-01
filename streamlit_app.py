import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Målgruppe-Analysatoren", layout="wide")

st.title("📊 Strategisk Målgruppe-Dashboard")
st.subheader("Data direkte fra Danmarks Statistik")

def hent_dst_data(kommune_kode="000"):
    # Ny URL og mere simpel forespørgsel
    url = "https://api.statbank.dk/v1/data/FOLK1A/CSV"
    
    # Vi beder om Alder (IALT + grupper) og Område
    payload = {
        "lang": "da",
        "delimiter": "Semicolon",
        "variables": [
            {"code": "OMRÅDE", "values": [kommune_kode]},
            {"code": "ALDER", "values": ["IALT", "0-6", "7-16", "17-24", "25-44", "45-66", "67+"]}
        ]
    }
    
    respons = requests.post(url, json=payload)
    
    if respons.status_code == 200:
        # Vi læser svaret som tekst og laver det til en tabel
        from io import StringIO
        csv_data = StringIO(respons.text)
        df = pd.read_csv(csv_data, sep=';')
        # Vi omdøber kolonnerne så de er pæne
        df.columns = ['Område', 'Aldersgruppe', 'Tid', 'Antal']
        return df
    else:
        st.error(f"Fejl: DST svarede med kode {respons.status_code}")
        st.info("Tip: Det kan skyldes midlertidig overbelastning hos DST.")
        return None

# Menu
st.sidebar.header("Indstillinger")
kommune_valg = st.sidebar.selectbox(
    "Vælg en kommune:",
    ["Hele landet", "København", "Aarhus", "Odense", "Aalborg"]
)

kommuner = {"Hele landet": "000", "København": "101", "Aarhus": "751", "Odense": "461", "Aalborg": "851"}
valgt_kode = kommuner[kommune_valg]

# Hent data
df = hent_dst_data(valgt_kode)

if df is not None:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write(f"### Tal for {kommune_valg}")
        # Vis kun Alder og Antal
        vis_df = df[['Aldersgruppe', 'Antal']]
        st.table(vis_df)
        
    with col2:
        st.write("### Visuel fordeling")
        # Lav graf uden 'I alt'
        graf_df = vis_df[vis_df['Aldersgruppe'] != 'I alt']
        st.bar_chart(data=graf_df, x='Aldersgruppe', y='Antal')
