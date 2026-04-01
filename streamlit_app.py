import streamlit as st
import pandas as pd
import google.generativeai as genai

# Grundlæggende setup
st.set_page_config(page_title="Strategisk Gemini-Rådgiver", layout="wide")
st.title("♊ Strategisk Gemini-Chat")

# --- KONFIGURATION ---
# Din personlige API-nøgle er nu indsat direkte
MY_API_KEY = "AIzaSyCcb-OLgjaO4pNcfP7rYEpJef3OJ36JCXk" 

# Konfigurer Gemini med din nøgle med det samme
genai.configure(api_key=MY_API_KEY)

with st.sidebar:
    st.header("Status")
    st.success("✅ Gemini AI er aktiveret")
    st.info("Project: gen-lang-client-0170594232")

# --- DATA ---
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

# Vis tidligere beskeder
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat-input
if prompt := st.chat_input("Skriv dit spørgsmål her (f.eks. 'Hvad er den vigtigste målgruppe?')"):
    # Gem brugerens spørgsmål
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generer svar fra Gemini
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Giv AI'en kontekst om dine tal
            context = f"Du er en strategisk raadgiver. Her er data om befolkningen: {df.to_string()}. Svar kort og præcist på dansk."
            
            with st.spinner("Gemini tænker..."):
                response = model.generate_content([context, prompt])
                
                if response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    st.error("AI'en gav et tomt svar. Prøv igen.")
                    
        except Exception as e:
            st.error(f"Der opstod en fejl: {str(e)}")
            st.info("Tjek om din API-nøgle stadig er aktiv i Google AI Studio.")
