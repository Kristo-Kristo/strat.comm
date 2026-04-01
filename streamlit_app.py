import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Målgruppe-Analysatoren", layout="wide")

st.title("📊 Strategisk Målgruppe-Dashboard")
st.subheader("Data direkte fra Danmarks Statistik")

def hent_dst_data_simpel(kommune_kode="000"):
    # Vi prøver den absolut simpleste URL-metode
    url = f"https://api.statbank.dk/v1/data/FOLK1A/CSV?OMRÅDE={kommune_kode}&ALDER=IALT,0-6,7-16,17-24,25-44,45-66,67+&Tid=2023K4"
    
    try:
        respons = requests.get(url)
        if respons.status_code == 200:
            df = pd.read_csv(io.StringIO(respons.text), sep=';')
            df.columns = ['Område', 'Aldersgruppe', 'Tid', 'Antal']
            return df
        else:
            return None
    except:
        return None

# Menu i siden
st.sidebar.header("Indstillinger")
kommune_navn = st.sidebar.selectbox(
    "Vælg en kommune:",
    ["Hele landet", "København", "Aarhus", "Odense", "Aalborg"]
)

kommuner = {"Hele landet": "000", "København": "101", "Aarhus": "751", "Odense": "461", "Aalborg": "851"}
valgt_kode = kommuner[kommune_navn]

# Forsøg at hente rigtig data
df = hent_dst_data_simpel(valgt_kode)

# Hvis DST driller, så brug test-data så du kan se appen virke
if df is None:
    st.warning("⚠️ Kunne ikke hente live-data fra DST lige nu. Viser eksempel-data i stedet.")
    df = pd.DataFrame({
        'Aldersgruppe': ["I alt", "0-6 år", "7-16 år", "17-24 år", "25-44 år", "45-66 år", "67+ år"],
        'Antal': [6000000, 450000, 650000, 600000, 1500000, 1600000, 1150000]
    })
else:
    # Rens data fra DST så den er pæn
    df = df[['Aldersgruppe', 'Antal']]

# Vis resultater
col1, col2 = st.columns([1, 2])

with col1:
    st.write(f"### Målgruppetal for {kommune_navn}")
    st.table(df)

with col2:
    st.write("### Aldersfordeling")
    graf_df = df[df['Aldersgruppe'] != 'I alt']
    st.bar_chart(data=graf_df, x='Aldersgruppe', y='Antal')

st.info("💡 **Hvad betyder det for din strategi?** Hvis søjlen for '25-44 år' er højest, skal din kommunikation ofte fokusere på karriere, familie og tidsoptimering.")
