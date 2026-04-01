import streamlit as st
import pandas as pd
import google.generativeai as genai

# Grundlæggende setup
st.set_page_config(page_title="Strategisk Gemini-Rådgiver", layout="wide")
st.title("♊ Strategisk Gemini-Chat")

# --- KONFIGURATION ---
MY_API_KEY = "AIzaSyCcb-OLgjaO4pNcfP7rYEpJef3OJ36JCXk" 

try:
    genai.configure(api_key=MY_API_KEY)
    
    # Hent liste over modeller for at tjekke adgang
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    with st.sidebar:
        st.header("System Status")
        st.success("✅ Forbundet til Google AI")
        st.write("**Tilgængelige modeller på din konto:**")
        for m in available_models:
            st.code(m.replace('models/', ''))
except Exception as e:
    st.sidebar.error(f"Kunne ikke hente modeller: {e}")

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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Skriv dit spørgsmål her..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Vi prøver først den mest almindelige model, men uden 'models/' præfiks
            # Hvis den fejler, prøver vi den første fra din liste over tilgængelige modeller
            model_name = 'gemini-1.5-flash'
            model = genai.GenerativeModel(model_name)
            
            context = f"Du er en strategisk raadgiver. Data: {df.to_string()}. Svar paa dansk."
            
            with st.spinner("Gemini analyserer..."):
                response = model.generate_content([context, prompt])
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Model-fejl: {e}")
            st.info("Tjek listen i venstre side for at se, hvilke model-navne din konto understøtter.")
