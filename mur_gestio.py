import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64

# 1. CONFIGURACIÓ I ESTILS REDUÏTS
st.set_page_config(page_title="Analitzador PD3", layout="wide")

COLORS_PREG = ["#feff9c", "#ffccf9", "#7afcff", "#c0ff8a"]
ICONES = ["✨", "🧠", "🚧", "🚀"]
TEMES = ["Activitats preferides", "Reflexió", "Dificultats", "Millores de codi"]

st.markdown("""
    <style>
    .resum-box { background-color: #f9f9f9; padding: 10px; border-radius: 8px; border: 1px solid #eee; margin-bottom: 15px; }
    .quote-box { font-style: italic; color: #444; padding: 3px 10px; border-left: 2px solid #ddd; margin-bottom: 4px; font-size: 0.85rem; }
    .mural-postit {
        padding: 8px; border-radius: 0px 0px 10px 0px; box-shadow: 1px 1px 3px rgba(0,0,0,0.05); 
        margin-bottom: 6px; border-left: 4px solid rgba(0,0,0,0.1); color: #2c3e50; 
        min-height: 60px; font-family: 'Comic Sans MS', cursive, sans-serif; font-size: 0.85rem;
    }
    .nom-infant { font-size: 0.7rem; color: #888; font-style: italic; margin-top: 3px; display: block; text-align: right; }
    .titol-pregunta-app { font-size: 0.9rem !important; color: #444 !important; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FILTRE ESTRICTE (SENSE NOMS NI PARAULES BUIDES)
STOPWORDS_CAT = {
    "a", "amb", "de", "del", "dels", "la", "les", "el", "els", "un", "una", "i", "que", "per", "perquè", "què", "com",
    "és", "són", "va", "ha", "hi", "si", "no", "tot", "molt", "més", "altre", "altres", "això", "aquí", "està", "quan",
    "maria", "pol", "aina", "aurora", "quico", "vull", "puc", "fer", "fet", "dir", "diria", "ser", "estat", "anar", 
    "veure", "crec", "sembla", "tenir", "tenia", "molta", "molts", "cada", "tots", "només", "també", "però", "perque",
    "li", "els", "per", "pels", "ens", "et", "em", "tot", "tota"
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

    if mode == "☁️ Núvols":
        st.header("☁️ Núvols de paraules (P1, P3, P4)")
        p_sel = st.selectbox("Tria pregunta:", [preguntes[0], preguntes[2], preguntes[3]])
        text_wc = " ".join(df[p_sel].fillna("").astype(str))
        if len(text_wc.strip()) > 5:
            wc = WordCloud(width=800, height=400, background_color="white", stopwords=STOPWORDS_CAT).generate(text_wc.lower())
            fig, ax = plt.subplots(); ax.imshow(wc); ax.axis("off")
            st.pyplot(fig)

    elif mode == "🤖 Resum":
        st.header("🤖 Resum i Cites")
        c_res = st.selectbox("Centre:", escoles)
        df_res = df[df.iloc[:, 1] == c_res]
        for i, p in enumerate(preguntes):
            st.markdown(f"<div class='titol-pregunta-app'>{ICONES[i]} {p}</div>", unsafe_allow_html=True)
            respostes = df_res[p].dropna().tolist()
            if respostes:
                text_net = " ".join(respostes).lower().replace('"', '').replace('.', '').replace(',', '')
                paraules = [w for w in text_net.split() if w not in STOPWORDS_CAT and len(w) > 4]
                conceptes = list(dict.fromkeys(pd.Series(paraules).value_counts().head(6).index.tolist()))
                st.markdown(f'<div class="resum-box" style="border-left: 6px solid {COLORS_PREG[i]};"><b>{TEMES[i]}</b>: {", ".join(conceptes).upper()}</div>', unsafe_allow_html=True)
                for cita in sorted(respostes, key=len, reverse=True)[:5]:
                    st.markdown(f'<div class="quote-box">"{cita}"</div>', unsafe_allow_html=True)

    elif mode == "📮 Mural PDF":
        c_mural = st.selectbox("Centre:", escoles)
        df_mural = df[df.iloc[:, 1]
