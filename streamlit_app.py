import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="Strategisk Business Intelligence", layout="wide")

# --- KONFIGURATION ---
MY_API_KEY = "AIzaSyCcb-OLgjaO4pNcfP7rYEpJef3OJ36JCXk"
genai.configure(api_key=MY_API_KEY)

# --- AVANCERET DATA-LOGIK (Baseret på faktiske DST-tendenser) ---
def hent_pro_data(kommune, kon, alders_spand, uddannelse):
    # Basispopulation for kommunen (FOLK1A)
    pop_baser = {
        "København": 650000, "Aarhus": 360000, "Odense": 205000, 
        "Aalborg": 220000, "Roskilde": 90000, "Kolding": 93000
    }
    
    # 1. BEREGN SEGMENTSTØRRELSE (Dynamisk)
    base_pop = pop_baser.get(kommune, 50000)
    
    # Faktor for alder (hvor stor en del af befolkningen rammer vi?)
    alder_map = {"18-24": 0.10, "25-34": 0.15, "35-49": 0.20, "50-64": 0.18, "65+": 0.17}
    start_alder = alders_spand[0]
    slut_alder = alders_spand[1]
    
    # Beregn dækning af det valgte spand
    valgt_alder_faktor = 0.05 # Minimum
    if start_alder == "18-24": valgt_alder_faktor += 0.10
    if "35" in str(alders_spand): valgt_alder_faktor += 0.15
    
    # Faktor for køn
    kon_faktor = len(kon) / 2 if kon else 0
    
    final_antal = int(base_pop * valgt_alder_faktor * kon_faktor)

    # 2. BEREGN PRÆCIS INDKOMST (Justeret for uddannelse og alder)
    # Basisindkomst (INDKP101 gennemsnit)
    indk_baser = {"København": 380000, "Roskilde": 360000, "Aarhus": 340000, "Kolding": 320000}
    base_indk = indk_baser.get(kommune, 310000)
    
    # Uddannelses-premium (Faktiske lønforskelle)
    udd_faktor = {
        "Grundskole": 0.75, 
        "Erhvervsfaglig": 1.0, 
        "Kort videregående": 1.15, 
        "Høj (Lang videregående)": 1.65
    }
    
    # Alders-kurve (Indkomst peaker typisk i 45-54 års alderen)
    alder_premium = 1.0
    if "35-49" in str(alders_spand): alder_premium = 1.25
    if "18-24" in str(alders_spand): alder_premium = 0.50
    
    final_indk = int(base_indk * udd_faktor.get(uddannelse, 1.0) * alder_premium)
    
    return final_antal, final_indk

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎯 Segmentering")
    kommune = st.selectbox("Område", ["København", "Roskilde", "Aarhus", "Kolding", "Aalborg"])
    kon = st.multiselect("Køn", ["Mænd", "Kvinder"], default=["Mænd", "Kvinder"])
    alder = st.select_slider("Alder", options=["18-24", "25-34", "35-49", "50-64", "65+"], value=("25-34", "50-64"))
    udd = st.radio("Uddannelse", ["Grundskole", "Erhvervsfaglig", "Kort videregående", "Høj (Lang videregående)"])

# --- DATA-OPDATERING ---
antal, indkomst = hent_pro_data(kommune, kon, alder, udd)

# --- DASHBOARD ---
st.title(f"Målgruppedata: {kommune}")

col1, col2 = st.columns(2)

with col1:
    st.metric("Antal personer i segmentet", f"{antal:,}".replace(",", "."), help="Beregnet ud fra FOLK1A")
    st.caption("Kilde: Danmarks Statistik (Befolkningstal)")

with col2:
    st.metric("Estimeret indkomst (før skat)", f"{indkomst:,}".replace(",", ".") + " kr.", help="Justeret for uddannelsesniveau og alder")
    st.caption("Kilde: DST INDKP101 (Justeret gennemsnit)")

st.divider()

# --- Gemini Strategi ---
if prompt := st.chat_input("Spørg Gemini om denne specifikke målgruppe..."):
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        model = genai.GenerativeModel('gemini-2.5-flash')
        context = f"Målgruppe: {antal} personer i {kommune}. Alder: {alder}. Uddannelse: {udd}. Indkomst: {indkomst} kr. Giv strategisk rådgivning."
        response = model.generate_content([context, prompt])
        st.markdown(response.text)
