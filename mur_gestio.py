import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64

# 1. CONFIGURACIÓ I ESTILS
st.set_page_config(page_title="Analitzador PD3", layout="wide")

# Configuració de Preguntes, Icones i Temes
COLORS_PREG = ["#feff9c", "#ffccf9", "#7afcff", "#c0ff8a"]
ICONES = ["✨", "🧠", "🚧", "🚀"]
TEMES = ["Activitats preferides", "Reflexió sobre l'aprenentatge", "Dificultats trobades", "Millores del codi"]

st.markdown("""
    <style>
    /* Estils de les caixes de resum */
    .resum-box { background-color: #fcfcfc; padding: 15px; border-radius: 8px; border: 1px solid #eee; margin-bottom: 20px; }
    .quote-box { 
        font-style: italic; color: #555; padding: 5px 15px; 
        border-left: 3px solid #ddd; margin-bottom: 8px; font-size: 0.9rem; 
    }
    
    /* Estils de l'App (mides reduïdes) */
    .mural-postit {
        padding: 12px; border-radius: 0px 0px 15px 0px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px;
        border-left: 5px solid rgba(0,0,0,0.1); color: #2c3e50; min-height: 80px;
        font-family: 'Comic Sans MS', cursive, sans-serif; font-size: 0.9rem;
    }
    .nom-infant { font-size: 0.75rem; color: #777; font-style: italic; margin-top: 5px; display: block; text-align: right; }
    
    .titol-pregunta-app {
        font-size: 0.95rem !important;
        color: #444 !important;
        font-weight: bold;
        margin-top: 15px;
        padding-bottom: 3px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DICCIONARI DE NETEJA ESTRICTE
STOPWORDS_CAT = {
    "a", "amb", "de", "del", "dels", "la", "les", "el", "els", "un", "una", "i", "que", "per", "perquè", "què", "com",
    "és", "són", "va", "ha", "hi", "si", "no", "tot", "molt", "més", "altre", "altres", "això", "aquí", "està", "quan",
    "maria", "pol", "aina", "aurora", "quico", "vull", "puc", "fer", "fet", "dir", "diria", "ser", "estat", "anar", 
    "veure", "crec", "sembla", "tenir", "tenia", "molta", "molts", "cada", "tots", "només", "també", "però"
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

    st.sidebar.title("🛠️ Gestió PD3")
    mode = st.sidebar.radio("Secció:", ["🏠 Comparativa", "☁️ Núvols", "🤖 Resum", "📮 Mural PDF"])

    # --- PESTANYA NÚVOLS (P1, P3, P4) ---
    if mode == "☁️ Núvols":
        st.header("☁️ Núvols de paraules")
        # Filtrem només P1, P3 i P4
        preg_nuvol = [preguntes[0], preguntes[2], preguntes[3]]
        p_sel = st.selectbox("Selecciona la pregunta per al núvol:", preg_nuvol)
        
        text_nuvol = " ".join(df[p_sel].fillna("").astype(str))
        if len(text_nuvol.strip()) > 20:
            wc = WordCloud(width=800, height=400, background_color="white", 
                          stopwords=STOPWORDS_CAT, colormap='Dark2').generate(text_nuvol.lower())
            fig, ax = plt.subplots()
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.warning("No hi ha prou dades per generar el núvol.")

    # --- PESTANYA RESUM (Amb Cites Literals) ---
    elif mode == "🤖 Resum":
        st.header("🤖 Resum de la Veu de l'Alumnat")
        c_res = st.selectbox("Selecciona Centre:", escoles)
        df_res = df[df.iloc[:, 1] == c_res]
        
        for i, p in enumerate(preguntes):
            st.markdown(f"<div class='titol-pregunta-app'>{ICONES[i]} {p}</div>", unsafe_allow_html=True)
            respostes = df_res[p].dropna().tolist()
            
            if respostes:
                # Conceptes clau (Neteja estricta)
                text_net = " ".join(respostes).lower().replace('"', '').replace('.', '').replace(',', '')
                paraules = [w for w in text_net.split() if w not in STOPWORDS_CAT and len(w) > 4]
                conceptes = list(dict.fromkeys(pd.Series(paraules).value_counts().head(6).index.tolist()))
                
                # Renderitzat del resum
                st.markdown(f"""
                <div class="resum-box" style="border-left: 8px solid {COLORS_PREG[i]};">
                    <b>Temàtica:</b> {TEMES[i]}<br>
                    <b>Conceptes clau:</b> {", ".join(conceptes).upper()}
                </div>
                """, unsafe_allow_html=True)
                
                # Selecció de cites literals (màxim 5, les més llargues solen ser les més significatives)
                st.markdown("<b>Cites literals destacades:</b>", unsafe_allow_html=True)
                cites_destacades = sorted(respostes, key=len, reverse=True)[:5]
                for cita in cites_destacades:
                    st.markdown(f'<div class="quote-box">"{cita}"</div>', unsafe_allow_html=True)
                st.write("") # Espaiat

    # --- PESTANYA MURAL PDF (Igual però amb mides reduïdes) ---
    elif mode == "📮 Mural PDF":
        c_mural = st.selectbox("Selecciona el centre:", escoles)
        df_mural = df[df.iloc[:, 1] == c_mural]
        
        # Botó de descàrrega (Codi HTML net)
        # ... (Mantinc la teva lògica de descàrrega HTML que ja funcionava) ...
        
        st.divider()
        for i, p in enumerate(preguntes):
            st.markdown(f"<div class='titol-pregunta-app'>{ICONES[i]} {p}</div>", unsafe_allow_html=True)
            cols = st.columns(3)
            respostes_p = df_mural[pd.notna(df_mural[p])]
            for idx, (index_row, dades) in enumerate(respostes_p.iterrows()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="mural-postit" style="background-color: {COLORS_PREG[i]};">
                        "{dades[p]}"
                        <span class="nom-infant">({dades.iloc[2]})</span>
                    </div>
                    """, unsafe_allow_html=True)

    elif mode == "🏠 Comparativa":
        st.header("🏠 Comparativa")
