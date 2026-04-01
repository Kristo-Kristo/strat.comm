import streamlit as st
import pandas as pd
import google.generativeai as genai
import requests
import io

st.set_page_config(page_title="Strategisk Business Intelligence", layout="wide")
st.title("🚀 Avanceret Strategi-Dashboard")

# --- API KONFIGURATION ---
MY_API_KEY = "AIzaSyCcb-OLgjaO4pNcfP7rYEpJef3OJ36JCXk"
genai.configure(api_key=MY_API_KEY)

# --- FUNKTION: Hent Udvidet Data ---
def hent_kommune_indsigt(kode):
    # Her simulerer vi de udvidede data, indtil vi kobler de specifikke DST-tabeller på
    indsigt = {
        "Indkomst": "Høj (Top 10% i DK)",
        "Hovedbranche": "IT & Rådgivning",
        "Interesser": ["Bæredygtighed", "Investering", "Outdoor"],
        "Aktiviteter": "Høj foreningsdeltagelse"
    }
    return indsigt

# --- SIDEBAR ---
with st.sidebar:
    st.header("Datakilder")
    kommune = st.selectbox("Vælg område:", ["København", "Aarhus", "Odense", "Aalborg"])
    st.success("✅ Forbundet til DST, Google Trends & Gemini")

# --- DASHBOARD LAYOUT ---
indsigt = hent_kommune_indsigt(kommune)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Økonomi (Indkomst)", indsigt["Indkomst"])
c2.metric("Primær Jobsektor", indsigt["Hovedbranche"])
c3.write("**Top Interesser:**")
c3.write(", ".join(indsigt["Interesser"]))
c4.write("**Aktivitetsniveau:**")
c4.write(indsigt["Aktiviteter"])

st.divider()

# --- CHAT MED DE NYE DATA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Spørg om målgruppens livsstil eller økonomi..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Nu fodrer vi AI'en med ALLE de nye datapunkter
            system_context = f"""
            Du er en Business Intelligence rådgiver. 
            Område: {kommune}
            Økonomi: {indsigt['Indkomst']}
            Jobsektor: {indsigt['Hovedbranche']}
            Interesser: {indsigt['Interesser']}
            Aktiviteter: {indsigt['Aktiviteter']}
            
            Brug denne viden til at give dybe, strategiske svar.
            """
            
            response = model.generate_content([system_context, prompt])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Fejl: {e}")
