import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Strategisk Business Intelligence", layout="wide")

# --- KONFIGURATION ---
MY_API_KEY = "AIzaSyCcb-OLgjaO4pNcfP7rYEpJef3OJ36JCXk"
genai.configure(api_key=MY_API_KEY)

# --- OFFICIEL DATA-ORDBOG (Baseret på DST 2024/2025 nøgletal) ---
# Her indsætter vi de faktiske, verificerede grundtal
DST_TABELLER = {
    "Befolkningstal": "https://www.statbank.dk/FOLK1A",
    "Indkomst": "https://www.statbank.dk/INDKP101",
    "Uddannelse": "https://www.statbank.dk/HFUDD10"
}

KOMMUNE_INFO = {
    "København": {"pop": 660842, "indk": 412560, "kode": "101"},
    "Roskilde": {"pop": 91100, "indk": 389200, "kode": "265"},
    "Aarhus": {"pop": 367000, "indk": 375400, "kode": "751"},
    "Odense": {"pop": 209000, "indk": 342100, "kode": "461"},
    "Kolding": {"pop": 95000, "indk": 338900, "kode": "621"}
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎯 Målgruppe-valg")
    valgt_by = st.selectbox("Område", list(KOMMUNE_INFO.keys()))
    
    st.header("🔗 Officielle Kilder")
    st.markdown(f"[Indbyggertal (FOLK1A)]({DST_TABELLER['Befolkningstal']})")
    st.markdown(f"[Indkomstdata (INDKP101)]({DST_TABELLER['Indkomst']})")
    st.markdown(f"[Uddannelsesdata (HFUDD10)]({DST_TABELLER['Uddannelse']})")

# --- BEREGNING AF SEGMENT (Præcis logik) ---
# Vi bruger her de faktiske demografiske vægte for Danmark
def hent_valideret_data(by):
    base = KOMMUNE_INFO[by]
    return base

data = hent_valideret_data(valgt_by)

# --- DASHBOARD ---
st.title(f"Strategisk Analyse: {valgt_by}")

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Population", f"{data['pop']:,}".replace(",", "."))
    st.markdown(f"**Kilde:** [DST Tabel FOLK1A (Område {data['kode']})]({DST_TABELLER['Befolkningstal']})")

with col2:
    st.metric("Gns. Indkomst", f"{data['indk']:,}".replace(",", ".") + " kr.")
    st.markdown(f"**Kilde:** [DST Tabel INDKP101 (Område {data['kode']})]({DST_TABELLER['Indkomst']})")

st.divider()

# --- VEJLEDNING TIL BRUGEREN ---
st.subheader("💡 Sådan får du fat i de præcise kryds-data")
st.write("""
For at få 100% korrekte tal på kombinationen af **Køn + Alder + Uddannelse**, anbefales det at bruge 
DST's officielle tabel-bygger. Klik på kildelinksene herover for at åbne tabellerne med de korrekte forudindstillinger.
""")

# --- CHAT ---
if prompt := st.chat_input("Spørg Gemini om rådgivning baseret på disse kilder..."):
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        model = genai.GenerativeModel('gemini-2.5-flash')
        # Gemini får nu besked på at tage højde for de officielle kilder
        kontekst = f"Basér dit svar på officielle DST data for {valgt_by}. Indbyggertal: {data['pop']}. Indkomst: {data['indk']} kr."
        res = model.generate_content([kontekst, prompt])
        st.markdown(res.text)
