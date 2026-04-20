import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓ DE PÀGINA I ESTILS D'IMPRESSIÓ DINÀMICS
st.set_page_config(page_title="Mural PDF PD3", layout="wide")

st.markdown("""
    <style>
    /* Configuració del contenidor principal per a impressió */
    @media print {
        header, [data-testid="stSidebar"], [data-testid="stHeader"], footer, .stTabs, .stButton, .stSelectbox, [data-testid="stDecoration"] {
            display: none !important;
        }
        .main .block-container { padding: 0 !important; margin: 0 !important; width: 100% !important; }
        .salt-pagina { page-break-before: always; display: block; height: 1px; visibility: hidden; }
    }

    /* Estil de la graella de post-its (Flexbox per evitar talls) */
    .mural-flex {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: flex-start;
        padding: 10px;
    }

    .postit-neta {
        width: calc(33% - 20px); /* 3 columnes amb marge */
        min-width: 200px;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #eee;
        background-color: #fff;
        page-break-inside: avoid; /* Evita que un post-it es talli entre dues pàgines */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .text-res { font-size: 0.95rem !important; line-height: 1.3; color: #333; margin-bottom: 10px; }
    .nom-infant { font-size: 0.8rem; color: #666; text-align: right; font-style: italic; border-top: 1px solid rgba(0,0,0,0.05); padding-top: 5px; }
    
    .titol-pdf { font-size: 1.2rem !important; color: #e67e22; border-bottom: 2px solid #e67e22; margin: 25px 0 15px 0; padding-bottom: 5px; width: 100%; text-transform: uppercase; }
    .nom-escola { font-size: 1.5rem !important; text-align: center; color: #2c3e50; margin-bottom: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. CÀRREGA DE DADES
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
    COLORS = ["#FFF9C4", "#FCE4EC", "#E1F5FE", "#E8F5E9"] # Colors pastís per P1, P2, P3, P4

    st.sidebar.title("🛠️ Gestió PD3")
    mode = st.sidebar.radio("Vés a:", ["🏠 Comparativa", "🤖 Resum", "📮 Mural PDF Neteja"])

    if mode == "📮 Mural PDF Neteja":
        c_sel = st.sidebar.selectbox("Selecciona Centre:", escoles)
        st.info("💡 **Instruccions:** Prem **Ctrl+P**, selecciona 'Desar com a PDF' i assegura't que els **Marges estiguin en 'Predeterminat'** i els **Gràfics de fons estiguin activats**.")
        
        df_c = df[df.iloc[:, 1] == c_sel]
        st.markdown(f"<div class='nom-escola'>🏫 {c_sel}</div>", unsafe_allow_html=True)

        for i, p in enumerate(preguntes):
            # Força el salt de pàgina per a cada nova pregunta
            if i > 0:
                st.markdown('<div class="salt-pagina"></div>', unsafe_allow_html=True)
            
            st.markdown(f"<div class='titol-pdf'>Pregunta {i+1}: {p}</div>", unsafe_allow_html=True)
            
            # Iniciem la graella flex per a les respostes d'aquesta pregunta
            html_mural = '<div class="mural-flex">'
            for _, row in df_c.iterrows():
                # Només afegim si hi ha resposta
                if pd.notna(row[p]):
                    html_mural += f"""
                    <div class="postit-neta" style="background-color: {COLORS[i]};">
                        <div class="text-res">"{row[p]}"</div>
                        <div class="nom-infant">({row.iloc[2]})</div>
                    </div>
                    """
            html_mural += '</div>'
            st.markdown(html_mural, unsafe_allow_html=True)

    elif mode == "🤖 Resum":
        st.header("Anàlisi Veu de l'Alumnat")
        # Aquí pots mantenir la teva lògica de resum...

except Exception as e:
    st.error(f"S'ha produït un error de configuració: {e}")
