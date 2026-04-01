import streamlit as st
import pandas as pd
import requests
import io
import google.generativeai as genai

st.set_page_config(page_title="Strategisk Gemini-Rådgiver", layout="wide")

st.title("♊ Strategisk Gemini-Chat")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Indstillinger")
    google_api_key = st.text_input("Indsæt din Gemini API-nøgle:", type="password")
    kommune_navn = st.selectbox("Vælg Kommune:", ["Hele landet", "København", "Aarhus", "Odense", "Aalborg"])
    st.info("Hent din gratis nøgle på aistudio.google.com")

# --- DATA HENTNING ---
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
    except: return None

df = hent_data(kommuner[kommune_navn])

# --- VISUALISERING ---
col1, col2 = st.columns([1, 1])
if df is not None:
    with col1:
        st.write(f"### Demografi: {kommune_navn}")
        st.bar_chart(data=df[df['Aldersgruppe'] != 'I alt'], x='Aldersgruppe', y='Antal')
    with col2:
        st.write("### Data-overblik")
        st.dataframe(df[['Aldersgruppe', 'Antal']], use_container_width=True)

st.divider()

# --- CHAT MED GEMINI ---
st.subheader("💬 Spørg Gemini om din strategi")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Skriv dit spørgsmål..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not google_api_key:
            st.warning("Venligst indsæt din Gemini API-nøgle i menuen til venstre.")
        else:
            try:
                # Konfigurer Gemini
                genai.configure(api_key=google_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                # Forbered kontekst (tallene fra DST)
                data_context = df.to_string() if df is not None else "Ingen data tilgængelig"
                full_prompt = f"Du er en ekspert i strategisk kommunikation. Her er demografiske tal for {kommune_navn}: {data_context}. Brugeren spørger: {prompt}"
                
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Fejl: {e}")
