import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓ I ESTILS PROFESSIONALS PER A PDF
st.set_page_config(page_title="Mural PDF PD3", layout="wide")

st.markdown("""
    <style>
    /* NETEJA TOTAL D'IMPRESSIÓ: Amaga interfície de Streamlit i peu de pàgina */
    @media print {
        header, [data-testid="stSidebar"], [data-testid="stHeader"], footer, .stTabs, .stButton, .stSelectbox, [data-testid="stDecoration"] {
            display: none !important;
        }
        .main .block-container { padding: 0 !important; margin: 0 !important; width: 100% !important; }
        .salt-pagina { page-break-before: always; display: block; height: 1px; visibility: hidden; }
        .postit-neta { page-break-inside: avoid !important; }
    }

    /* Estil de la graella de post-its per a gran volum de dades */
    .mural-flex {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: flex-start;
        padding: 10px;
    }

    .postit-neta {
        width: calc(33.33% - 20px);
        min-width: 200px;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #eee;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 5px;
    }

    .text-res { font-size: 0.95rem !important; line-height: 1.3; color: #333; margin-bottom: 8px; }
    .nom-infant { font-size: 0.8rem; color: #666; text-align: right; font-style: italic; border-top: 1px solid rgba(0,0,0,0.05); padding-top: 5px; }
    
    .titol-pdf { font-size: 1.1rem !important; color: #e67e22; border-bottom: 2px solid #e67e22; margin: 20px 0 10px 0; padding-bottom: 5px; width: 100%; text-transform: uppercase; }
    .nom-escola { font-size: 1.4rem !important; text-align: center; color: #2c3e50; margin-bottom: 5px; font-weight: bold; }
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
    COLORS = ["#FFF9C4", "#FCE4EC", "#E1F5FE", "#E8F5E9"] # Groc, Rosa, Blau, Verd

    st.sidebar.title("🛠️ Gestió Mural")
    c_sel = st.sidebar.selectbox("Selecciona Centre:", escoles)
    
    # Contingut per a la impressió
    df_c = df[df.iloc[:, 1] == c_sel]
    st.markdown(f"<div class='nom-escola'>🏫 {c_sel}</div>", unsafe_allow_html=True)

    for i, p in enumerate(preguntes):
        # Força el salt de pàgina per a cada nova pregunta en la impressió
        if i > 0:
            st.markdown('<div class="salt-pagina"></div>', unsafe_allow_html=True)
        
        st.markdown(f"<div class='titol-pdf'>Pregunta {i+1}: {p}</div>", unsafe_allow_html=True)
        
        html_mural = '<div class="mural-flex">'
        for _, row in df_c.iterrows():
            if pd.notna(row[p]):
                html_mural += f"""
                <div class="postit-neta" style="background-color: {COLORS[i]};">
                    <div class="text-res">"{row[p]}"</div>
                    <div class="nom-infant">({row.iloc[2]})</div>
                </div>
                """
        html_mural += '</div>'
        st.markdown(html_mural, unsafe_allow_html=True)

except Exception as e:
    st.error(f"S'ha produït un error en carregar el mural: {e}")
