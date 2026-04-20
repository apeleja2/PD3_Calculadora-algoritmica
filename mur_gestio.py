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
    .slide-export { background-color: #1e1e1e; color: white; padding: 40px; border-radius: 15px; text-align: center; margin-bottom: 20px; border: 2px solid #e67e22; }
    .mural-postit {
        background-color: #feff9c; padding: 15px; border-radius: 0px 0px 20px 0px;
        box-shadow: 3px 3px 7px rgba(0,0,0,0.1); margin-bottom: 15px;
        border-left: 5px solid #f1c40f; color: #2c3e50; min-height: 150px;
    }
    @media print {
        .stButton, .stSelectbox, .stRadio, header, .stSidebar, .stMetric { display: none !important; }
        .slide-export { border: none; margin: 0; padding: 80px; width: 100%; }
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DICCIONARI DE NETEJA
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
    mode = st.sidebar.radio("Secció:", ["🏠 Comparativa", "☁️ Núvols", "🤖 Resum i Cites", "📮 Mural de Centres", "🎬 Exportació"])

    # --- RESUM I CITES (Millorat sense duplicats) ---
    if mode == "🤖 Resum i Cites":
        st.header("🤖 Anàlisi de la Veu de l'Alumnat")
        c_res = st.selectbox("Centre:", escoles)
        df_res = df[df.iloc[:, 1] == c_res]
        for p in preguntes:
            st.subheader(f"❓ {p}")
            respostes = df_res[p].dropna().tolist()
            if respostes:
                text_p = " ".join(respostes).lower()
                # Utilitzem set() per eliminar paraules repetides automàticament
                paraules_netes = [w for w in text_p.split() if w not in STOPWORDS_CAT and len(w) > 4]
                temes = list(dict.fromkeys(pd.Series(paraules_netes).value_counts().head(5).index.tolist()))
                st.markdown(f'<div class="resum-box"><b>Resum:</b> Destaquen conceptes com <b>{", ".join(temes)}</b>.</div>', unsafe_allow_html=True)
                for cita in sorted(respostes, key=len, reverse=True)[:3]:
                    st.markdown(f'<div class="quote-box">"{cita}"</div>', unsafe_allow_html=True)

    # --- MURAL DE CENTRES (Nova secció estètica) ---
    elif mode == "📮 Mural de Centres":
        st.header("📮 Mural de respostes per centre")
        c_mural = st.selectbox("Selecciona centre per veure tot el seu mural:", escoles)
        df_mural = df[df.iloc[:, 1] == c_mural]
        
        st.write(f"Recull de totes les preguntes per a l'escola: **{c_mural}**")
        
        for idx, row in df_mural.iterrows():
            with st.expander(f"👤 Alumne: {row.iloc[2]}", expanded=True):
                cols = st.columns(2)
                for i, p in enumerate(preguntes):
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class="mural-postit">
                            <small><b>{p}</b></small><br>
                            {row[p]}
                        </div>
                        """, unsafe_allow_html=True)

    # --- ALTRES SECCIONS (Sense canvis crítics) ---
    elif mode == "🏠 Comparativa":
        st.header("🏠 Comparativa entre Centres")
        centres_sel = st.multiselect("Centres:", escoles, default=escoles[:2] if len(escoles)>1 else escoles)
        if centres_sel:
            cols = st.columns(len(centres_sel))
            for i, centre in enumerate(centres_sel):
                df_c = df[df.iloc[:, 1] == centre]
                with cols[i]:
                    st.subheader(f"🏫 {centre}")
                    text_c = " ".join(df_c[preguntes].fillna("").astype(str).values.flatten())
                    if len(text_c.strip()) > 10:
                        wc = WordCloud(width=400, height=400, background_color="white", stopwords=STOPWORDS_CAT).generate(text_c.lower())
                        st.image(wc.to_array(), use_container_width=True)

    elif mode == "☁️ Núvols":
        st.header("☁️ Núvol de Paraules Clau")
        c_wc = st.selectbox("Centre:", ["Tots"] + escoles)
        p_wc = st.selectbox("Pregunta:", preguntes)
        df_wc = df if c_wc == "Tots" else df[df.iloc[:, 1] == c_wc]
        text_wc = " ".join(df_wc[p_wc].fillna("").astype(str))
        if len(text_wc.strip()) > 20:
            wc = WordCloud(width=1000, height=500, background_color="white", stopwords=STOPWORDS_CAT, collocations=False).generate(text_wc.lower())
            st.image(wc.to_array(), use_container_width=True)

    elif mode == "🎬 Exportació":
        st.header("🎬 Preparació per a Google Slides / PDF")
        c_exp = st.selectbox("Centre d'exportació:", escoles)
        p_exp = st.selectbox("Pregunta d'exportació:", preguntes)
        df_exp = df[df.iloc[:, 1] == c_exp]
        for _, row in df_exp.iterrows():
            st.markdown(f'<div class="slide-export"><h1 style="font-size:2.2rem;">"{row[p_exp]}"</h1><hr><p style="font-size:1.5rem;">👤 {row.iloc[2]} | {row.iloc[1]}</p></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Error: {e}")
