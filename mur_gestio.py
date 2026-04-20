import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓ I ESTILS PROFESSIONALS PER A PDF
st.set_page_config(page_title="Analitzador PD3", layout="wide")

st.markdown("""
    <style>
    /* Estil dels post-its */
    .postit-pdf {
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 10px;
        border: 1px solid rgba(0,0,0,0.05);
        min-height: 60px;
        display: block;
        page-break-inside: avoid;
        font-family: 'Segoe UI', sans-serif;
    }
    .text-resposta { font-size: 1rem !important; color: #333; line-height: 1.2; }
    .nom-infant { font-size: 0.75rem; color: #666; text-align: right; margin-top: 5px; font-style: italic; }
    
    /* Títols discrets */
    .titol-centre-pdf { font-size: 1.4rem !important; color: #2c3e50; text-align: center; margin-bottom: 20px; font-weight: bold; }
    .titol-pregunta-pdf { font-size: 1.1rem !important; color: #e67e22; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 15px; text-transform: uppercase; }

    /* NETEJA TOTAL D'IMPRESSIÓ */
    @media print {
        /* Amaga absolutament tota la interfície de Streamlit */
        header, [data-testid="stSidebar"], [data-testid="stHeader"], .stTabs, .stButton, .stSelectbox, .stRadio, .stMetric, .stAlert, [data-testid="stDecoration"] {
            display: none !important;
        }
        /* Elimina el peu de pàgina de "Manage app" */
        footer { visibility: hidden; }
        .main { background-color: white !important; padding: 0 !important; }
        .block-container { padding: 0 !important; }
        
        /* Força el salt de pàgina per cada pregunta */
        .salt-pagina { page-break-before: always; display: block; height: 0; }
        .targeta-neta { box-shadow: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DICCIONARI DE NETEJA
STOPWORDS_CAT = {"a", "amb", "de", "del", "dels", "la", "les", "el", "els", "un", "una", "i", "que", "per", "és", "són", "va", "ha", "hi", "si", "no", "com", "tot", "molt", "més", "maria", "pol", "aina", "aurora"}

# 3. CÀRREGA DE DADES
sheet_id = "1srWD8f2oN_JeV4lwDYPe6ysLbRsXk9UZHE9vEmqVHlo"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(csv_url)
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df = load_data()
    escoles = sorted(df.iloc[:, 1].unique().tolist())
    preguntes = df.columns[3:7].tolist()
    COLORS_POSTIT = ["#FFF9C4", "#FCE4EC", "#E1F5FE", "#E8F5E9"] # Groc, Rosa, Blau, Verd

    st.sidebar.title("🛠️ Gestió PD3")
    mode = st.sidebar.radio("Secció:", ["🏠 Comparativa", "☁️ Núvols", "🤖 Resum", "📮 Mural PDF"])

    if mode == "📮 Mural PDF":
        c_mural = st.selectbox("Selecciona el centre per al PDF:", escoles)
        st.info("📥 **Per un PDF perfecte:** Prem **Ctrl+P**, tria 'Desar com a PDF'. A 'Més opcions', activa 'Gràfics de fons' i posa els marges a 'Cap'.")
        
        df_mural = df[df.iloc[:, 1] == c_mural]
        st.markdown(f"<div class='titol-centre-pdf'>🏫 {c_mural}</div>", unsafe_allow_html=True)
        
        for i, p in enumerate(preguntes):
            # Salt de pàgina per a cada pregunta
            classe_salt = "salt-pagina" if i > 0 else ""
            st.markdown(f"<div class='{classe_salt}'></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='titol-pregunta-pdf'>Pregunta {i+1}: {p}</div>", unsafe_allow_html=True)
            
            # Organització en graella de 3 columnes
            cols = st.columns(3)
            for idx, (index_row, dades) in enumerate(df_mural.iterrows()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="postit-pdf" style="background-color: {COLORS_POSTIT[i]};">
                        <div class="text-resposta">"{dades[p]}"</div>
                        <div class="nom-infant">({dades.iloc[2]})</div>
                    </div>
                    """, unsafe_allow_html=True)

    elif mode == "🤖 Resum":
        st.header("🤖 Anàlisi de la Veu")
        # Aquí pots mantenir el codi del resum anterior...

except Exception as e:
    st.error(f"❌ Error: {e}")
