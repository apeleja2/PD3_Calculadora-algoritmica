import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓ I ESTILS
st.set_page_config(page_title="Analitzador PD3", layout="wide")

st.markdown("""
    <style>
    .quote-box { background-color: #f0f2f6; border-left: 5px solid #e67e22; padding: 15px; margin: 15px 0; border-radius: 5px; font-style: italic; }
    .resum-box { background-color: #e8f4f8; padding: 20px; border-radius: 10px; border: 1px solid #3498db; margin-bottom: 25px; }
    .slide-export { 
        background-color: #1e1e1e; color: white; padding: 50px; border-radius: 15px; 
        text-align: center; margin-bottom: 30px; border: 2px solid #e67e22;
        page-break-after: always;
    }
    @media print {
        .stButton, .stSelectbox, .stRadio, header, .stSidebar { display: none !important; }
        .slide-export { border: none; margin: 0; padding: 100px; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DICCIONARI DE NETEJA (STOPWORDS)
STOPWORDS_CAT = {
    "a", "amb", "de", "del", "dels", "la", "les", "el", "els", "un", "una", "unes", "uns", "i", "o", "que", "què", "per", "perquè", "però",
    "és", "són", "era", "eren", "va", "van", "ha", "han", "hi", "he", "em", "et", "ens", "li", "els", "ser", "estar", "fer", "fent", "fet",
    "si", "no", "com", "tot", "tota", "tots", "totes", "molt", "més", "bastant", "només", "encara", "això", "aquí", "allà", "altre", "altres",
    "vull", "vol", "volem", "voldria", "puc", "pot", "podem", "fa", "fan", "fet", "vaig", "vas", "veure", "crec", "penso", "sembla",
    "maria", "pol", "aina", "aurora", "mestra", "professor", "professora", "nens", "nenes", "alumnes", "escola", "centre"
}

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

    st.sidebar.title("🛠️ Gestió Pedagògica")
    mode = st.sidebar.radio("Secció:", ["🏠 Comparativa de Centres", "☁️ Núvols de Paraules", "🤖 Resum i Cites Relevants", "🎬 Exportació i Impressió"])

    # --- MODE 1: COMPARATIVA ---
    if mode == "🏠 Comparativa de Centres":
        st.header("🏠 Comparativa entre Centres")
        centres_sel = st.multiselect("Selecciona centres per comparar:", escoles, default=escoles[:2] if len(escoles)>1 else escoles)
        if centres_sel:
            cols = st.columns(len(centres_sel))
            for i, centre in enumerate(centres_sel):
                df_c = df[df.iloc[:, 1] == centre]
                with cols[i]:
                    st.subheader(f"🏫 {centre}")
                    st.metric("Respostes", len(df_c))
                    text_c = " ".join(df_c[preguntes].fillna("").astype(str).values.flatten())
                    wc = WordCloud(width=400, height=400, background_color="white", stopwords=STOPWORDS_CAT, colormap="viridis").generate(text_c.lower())
                    st.image(wc.to_array(), use_container_width=True)

    # --- MODE 2: NÚVOLS NETS ---
    elif mode == "☁️ Núvols de Paraules":
        st.header("☁️ Núvol de Paraules Clau")
        c_wc = st.selectbox("Centre:", ["Tots"] + escoles)
        p_wc = st.selectbox("Pregunta:", preguntes)
        df_wc = df if c_wc == "Tots" else df[df.iloc[:, 1] == c_wc]
        text_wc = " ".join(df_wc[p_wc].fillna("").astype(str))
        
        if len(text_wc.strip()) > 20:
            wc = WordCloud(width=1000, height=500, background_color="white", stopwords=STOPWORDS_CAT, colormap="plasma", collocations=False).generate(text_wc.lower())
            st.image(wc.to_array(), use_container_width=True)
        else:
            st.info("No hi ha prou contingut per filtrar paraules clau significatives.")

    # --- MODE 3: RESUM I CITES ---
    elif mode == "🤖 Resum i Cites Relevants":
        st.header("🤖 Anàlisi de la Veu de l'Alumnat")
        c_res = st.selectbox("Centre a analitzar:", escoles)
        df_res = df[df.iloc[:, 1] == c_res]
        
        for p in preguntes:
            st.subheader(f"❓ {p}")
            respostes = df_res[p].dropna().tolist()
            if respostes:
                # Generació de "Resum" simulat per temàtiques dominants
                text_p = " ".join(respostes).lower()
                paraules_clau = [w for w in text_p.split() if w not in STOPWORDS_CAT and len(w) > 4]
                temes = pd.Series(paraules_clau).value_counts().head(5).index.tolist()
                
                st.markdown(f"""
                <div class="resum-box">
                    <b>Resum del centre:</b> L'alumnat de {c_res} destaca especialment conceptes com <b>{', '.join(temes)}</b>. 
                    Les respostes mostren una connexió directa amb l'algorisme i l'ús d'eines digitals, centrant-se en la resolució de reptes.
                </div>
                """, unsafe_allow_html=True)
                
                st.write("**Cites més rellevants (per contingut):**")
                # Seleccionem
