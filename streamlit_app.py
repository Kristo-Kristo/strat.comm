import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Strategisk AI-Rådgiver", layout="wide")

st.title("🤖 AI-Drevet Målgruppe-Strategi")
st.subheader("Data fra DST + Strategisk Analyse")

# --- DATA HENTNING ---
def hent_dst_data_simpel(kommune_kode="000"):
    url = f"https://api.statbank.dk/v1/data/FOLK1A/CSV?OMRÅDE={kommune_kode}&ALDER=IALT,0-6,7-16,17-24,25-44,45-66,67+&Tid=2023K4"
    try:
        respons = requests.get(url, timeout=5)
        if respons.status_code == 200:
            df = pd.read_csv(io.StringIO(respons.text), sep=';')
            df.columns = ['Område', 'Aldersgruppe', 'Tid', 'Antal']
            return df
        return None
    except:
        return None

# --- SIDEBAR ---
st.sidebar.header("Konfiguration")
kommune_navn = st.sidebar.selectbox("Vælg Kommune:", ["Hele landet", "København", "Aarhus", "Odense", "Aalborg"])
kommuner = {"Hele landet": "000", "København": "101", "Aarhus": "751", "Odense": "461", "Aalborg": "851"}

# --- HOVEDINDHOLD ---
df = hent_dst_data_simpel(kommuner[kommune_navn])

if df is None:
    st.warning("Bruger demodata (DST serveren hviler sig)")
    df = pd.DataFrame({
        'Aldersgruppe': ["I alt", "0-6 år", "7-16 år", "17-24 år", "25-44 år", "45-66 år", "67+ år"],
        'Antal': [6000000, 450000, 650000, 600000, 1500000, 1600000, 1150000]
    })

col1, col2 = st.columns([1, 1])

with col1:
    st.write(f"### Demografi: {kommune_navn}")
    st.bar_chart(data=df[df['Aldersgruppe'] != 'I alt'], x='Aldersgruppe', y='Antal')

with col2:
    st.write("### Strategisk Analyse")
    st.write("Klik på knappen for at lade AI'en analysere tallene.")
    
    if st.button("🚀 Generér Kommunikationsstrategi"):
        with st.spinner('AI'en tænker over tallene...'):
            # Find den største gruppe (udover "I alt")
            top_gruppe = df[df['Aldersgruppe'] != 'I alt'].sort_values(by='Antal', ascending=False).iloc[0]
            gruppe_navn = top_gruppe['Aldersgruppe']
            
            st.success("Analyse færdig!")
            st.markdown(f"""
            #### 🎯 Primær Målgruppe: {gruppe_navn}
            Baseret på data for {kommune_navn}, er din største målgruppe i alderen **{gruppe_navn}**.
            
            **Strategiske anbefalinger:**
            1. **Kanalvalg:** Da gruppen er {gruppe_navn}, bør du fokusere på {'digitale platforme og korte formater' if '25-44' in gruppe_navn or '17-24' in gruppe_navn else 'traditionelle medier og dybdegående indhold'}.
            2. **Tone-of-Voice:** Sigt efter en tone der er {'ambitiøs og effektiv' if '25-44' in gruppe_navn else 'tryg og inkluderende'}.
            3. **Budskab:** Fokusér på {'tidsbesparelse og karriere' if '25-44' in gruppe_navn else 'fællesskab og livskvalitet'}.
            
            *Dette er en automatisk genereret analyse baseret på din demografiske profil.*
            """)

st.divider()
st.caption("Udviklet af Kristo-Kristo - Strategisk AI Værktøj v1.1")
