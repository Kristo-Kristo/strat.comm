import streamlit as st
import pandas as pd
import google.generativeai as genai

# Grundlæggende setup
st.set_page_config(page_title="Strategisk Gemini-Rådgiver", layout="wide")
st.title("♊ Strategisk Gemini-Chat")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Konfiguration")
    google_api_key = st.text_input("Indsæt din Gemini API-nøgle:", type="password")
    st.info("Hent din gratis nøgle på aistudio.google.com")

# --- DATA (Forenklet for at undgå fejl) ---
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

# --- CHAT-SYSTEM ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Vis besked-historik
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat-input
if prompt := st.chat_input("Skriv dit spørgsmål her..."):
    # Gem brugerens spørgsmål
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generer svar fra Gemini
    with st.chat_message("assistant"):
        if not google_api_key:
            st.error("Fejl: Du skal indsætte en API-nøgle i menuen til venstre.")
        else:
            try:
                # Konfigurer API'en
                genai.configure(api_key=google_api_key)
                
                # Prøv at bruge den mest stabile model-version
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Giv AI'en kontekst om dine tal
                context = f"Du er en strategisk raadgiver. Her er data om befolkningen: {df.to_string()}. Svar kort og præcist på dansk."
                
                with st.spinner("Gemini tænker..."):
                    # Vi sender både instruks og spørgsmål
                    response = model.generate_content([context, prompt])
                    
                    if response.text:
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    else:
                        st.error("AI'en gav et tomt svar. Prøv igen.")
                        
            except Exception as e:
                st.error("Der er stadig problemer med forbindelsen til Google.")
                st.info("Tjek venligst om din API-nøgle i AI Studio er markeret som 'Active'.")
