import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓ I ESTILS PROFESSIONALS PER A IMPRESSIÓ
st.set_page_config(page_title="Analitzador PD3", layout="wide")

st.markdown("""
    <style>
    /* Disseny de les targetes (Post-its) */
    .targeta-neta {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #ddd;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .text-resposta {
        font-size: 1.1rem !important;
        line-height: 1.3;
        color: #2c3e50;
        margin-bottom: 8px;
    }
    .nom-infant {
        font-size: 0.85rem;
        color: #7f8c8d;
        text-align: right;
        font-style: italic;
    }
    
    /* Millora de les capçaleres de pregunta */
    .titol-pregunta {
        font-size: 1.3rem !important;
        color: #e67e22;
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    /* CSS per a la impressió neta (Elimina tot el que no sigui contingut) */
    @media print {
        header, .stSidebar, .stTabs, .stButton, .stSelectbox, .stRadio, .stMetric, .stAlert {
            display: none !important;
        }
        .main { background-color: white !important; }
        .targeta-neta { 
            box-shadow: none !important; 
            border: 0.5px solid #ccc !important;
            page-break-inside: avoid;
        }
        .page-break { page-break-before: always; display: block; height: 0; }
        .stMarkdown { width: 100% !important; }
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

# BLOC PRINCIPAL AMB CORRECCIÓ D'ERROR DE SINTAXI
try:
    df = load_data()
    escoles = sorted(df.iloc[:, 1].unique().tolist())
    preguntes = df.columns[3:7].tolist()
    COLORS_PREG = ["#FFF9C4", "#FCE4EC", "#E1F5FE", "#E8F5E9"] # Groc, Rosa, Blau, Verd suaus

    st.sidebar.title("🛠️ Gestió PD3")
    mode = st.sidebar.radio("Secció:", ["🏠 Comparativa", "☁️ Núvols", "🤖 Resum", "📮 Mural PDF"])

    if mode == "📮 Mural PDF":
        c_mural = st.selectbox("Selecciona el centre:", escoles)
        st.info("📥 Per un PDF net: Prem **Ctrl+P**, tria 'Desar com a PDF' i assegura't que 'Gràfics de fons' estigui activat.")
        
        df_mural = df[df.iloc[:, 1] == c_mural]
        st.markdown(f"<h1 style='text-align:center;'>🏫 {c_mural}</h1>", unsafe_allow_html=True)
        
        for i, p in enumerate(preguntes):
            if i > 0: st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
            st.markdown(f"<div class='titol-pregunta'>📌 {p}</div>", unsafe_allow_html=True)
            
            cols = st.columns(3)
            for idx, (index_row, dades) in enumerate(df_mural.iterrows()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="targeta-neta" style="background-color: {COLORS_PREG[i]};">
                        <div class="text-resposta">"{dades[p]}"</div>
                        <div class="nom-infant">({dades.iloc[2]})</div>
                    </div>
                    """, unsafe_allow_html=True)

    # (Aquí anirien les altres seccions: Comparativa, Núvols, Resum...)
    elif mode == "🤖 Resum":
        st.header("🤖 Anàlisi de la Veu")
        # ... (Codi del resum anterior) ...

except Exception as e:
    st.error(f"❌ Error: {e}")
