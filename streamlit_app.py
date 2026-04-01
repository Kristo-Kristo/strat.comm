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
    st.info("Hent din gratis nøgle på aistudio.google.com")

# --- DATA ---
# Vi bruger faste tal direkte for at undgå API-fejl fra DST i denne test
df = pd.DataFrame({
    "Alder": ["0-6 aar", "7-16 aar", "17-24 aar", "25-44 aar", "45-66 aar", "67+ aar"],
    "Antal": [450000, 650000, 600000, 1500000, 1600000, 1150000]
})

# --- VISUALISERING ---
col1, col2 = st.columns(2)
with col1:
    st.write("### Befolkningstal")
    st.bar_chart(data=df, x="Alder", y="Antal")
with col2:
    st.write("### Data-tabel")
    st.table(df)

st.divider()

# --- CHAT ---
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
            st.error("Indsæt venligst din API-nøgle i venstre side.")
        else:
            try:
                genai.configure(api_key=google_api_key)
                # Vi bruger 'gemini-1.5-flash' som er den mest stabile lige nu
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                context = f"Her er data: {df.to_string()}. Svar kort på dansk."
                response = model.generate_content([context, prompt])
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("Kunne ikke forbinde til Gemini. Tjek om din nøgle er aktiv.")
