import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64

# 1. CONFIGURACIÓ I ESTILS
st.set_page_config(page_title="Analitzador PD3", layout="wide")

# Colors definits per preguntes
COLORS_PREG = ["#feff9c", "#ffccf9", "#7afcff", "#c0ff8a"]

st.markdown("""
    <style>
    .resum-box { background-color: #e8f4f8; padding: 20px; border-radius: 10px; border: 1px solid #3498db; margin-bottom: 25px; }
    .mural-postit {
        padding: 20px; border-radius: 0px 0px 20px 0px;
        box-shadow: 3px 3px 7px rgba(0,0,0,0.1); margin-bottom: 15px;
        border-left: 5px solid rgba(0,0,0,0.1); color: #2c3e50; min-height: 120px;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        page-break-inside: avoid;
    }
    .nom-infant { font-size: 0.85rem; color: #555; font-style: italic; margin-top: 10px; display: block; text-align: right; }
    
    @media print {
        header, .stSidebar, .stTabs, .stButton, .stSelectbox, .stRadio, .stInfo { display: none !important; }
        .page-break { page-break-before: always; display: block; height: 0; }
        .mural-postit { box-shadow: none; border: 1px solid #ddd; }
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

try:
    df = load_data()
    escoles = sorted(df.iloc[:, 1].unique().tolist())
    preguntes = df.columns[3:7].tolist()

    st.sidebar.title("🛠️ Gestió PD3")
    mode = st.sidebar.radio("Secció:", ["🏠 Comparativa", "☁️ Núvols", "🤖 Resum", "📮 Mural PDF"])

    if mode == "📮 Mural PDF":
        c_mural = st.selectbox("Selecciona el centre per generar el document:", escoles)
        
        # Generar l'HTML per a la finestra d'impressió neta
        df_mural = df[df.iloc[:, 1] == c_mural]
        
        html_export = f"<html><head><title>Mural {c_mural}</title>"
        html_export += """<style>
            body { font-family: sans-serif; padding: 20px; }
            .grid { display: flex; flex-wrap: wrap; gap: 10px; }
            .postit { 
                width: 30%; padding: 15px; border-radius: 0 0 15px 0; 
                margin-bottom: 10px; border-left: 5px solid #ccc;
                page-break-inside: avoid; font-family: 'Comic Sans MS', cursive;
            }
            .nom { font-size: 0.8rem; text-align: right; display: block; font-style: italic; }
            .page-break { page-break-before: always; }
            h1 { text-align: center; color: #2c3e50; }
            h2 { color: #e67e22; border-bottom: 2px solid #e67e22; padding-top: 20px; }
        </style></head><body>"""
        
        html_export += f"<h1>🏫 {c_mural}</h1>"
        
        for i, p in enumerate(preguntes):
            salt = "page-break" if i > 0 else ""
            html_export += f"<div class='{salt}'><h2>📌 {p}</h2><div class='grid'>"
            for _, row in df_mural.iterrows():
                html_export += f"""
                <div class="postit" style="background-color: {COLORS_PREG[i]};">
                    "{row[p]}"
                    <span class="nom">({row.iloc[2]})</span>
                </div>"""
            html_export += "</div></div>"
        html_export += "</body></html>"

        # Botó de descàrrega/impressió neta
        b64 = base64.b64encode(html_export.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" target="_blank" style="text-decoration: none;"><button style="background-color: #e67e22; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 GENERAR MURAL NET PER A PDF</button></a>'
        
        st.write("### 🖨️ Pas final per a una impressió perfecta")
        st.info("Fes clic al botó taronja. S'obrirà una pestanya nova amb el mural net. Un cop allà, prem **Ctrl+P** per desar-ho com a PDF.")
        st.markdown(href, unsafe_allow_html=True)

        # Visualització prèvia a la web (per si no volen imprimir)
        st.divider()
        st.markdown(f"<h1 style='text-align:center;'>🏫 {c_mural}</h1>", unsafe_allow_html=True)
        for i, p in enumerate(preguntes):
            st.markdown(f"<h2 style='color:#e67e22; border-bottom:2px solid #e67e22;'>📌 {p}</h2>", unsafe_allow_html=True)
            cols = st.columns(3)
            for idx, (index_row, dades) in enumerate(df_mural.iterrows()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="mural-postit" style="background-color: {COLORS_PREG[i]};">
                        "{dades[p]}"
                        <span class="nom-infant">({dades.iloc[2]})</span>
                    </div>
                    """, unsafe_allow_html=True)

    elif mode == "🤖 Resum":
        st.header("🤖 Anàlisi de la Veu")
        c_res = st.selectbox("Centre:", escoles)
        df_res = df[df.iloc[:, 1] == c_res]
        for i, p in enumerate(preguntes):
            st.subheader(f"❓ {p}")
            respostes = df_res[p].dropna().tolist()
            if respostes:
                text_p = " ".join(respostes).lower()
                paraules = [w for w in text_p.split() if w not in STOPWORDS_CAT and len(w) > 4]
                temes = list(dict.fromkeys(pd.Series(paraules).value_counts().head(5).index.tolist()))
                st.markdown(f'<div class="resum-box" style="border-left:10px solid {COLORS_PREG[i]}"><b>Resum:</b> {", ".join(temes).upper()}</div>', unsafe_allow_html=True)
                for cita in sorted(respostes, key=len, reverse=True)[:3]:
                    st.markdown(f'<div class="quote-box">"{cita}"</div>', unsafe_allow_html=True)

    elif mode == "🏠 Comparativa":
        st.header("🏠 Comparativa")
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
        st.header("☁️ Núvols")
        c_wc = st.selectbox("Centre:", ["Tots"] + escoles)
        p_wc = st.selectbox("Pregunta:", preguntes)
        df_wc = df if c_wc == "Tots" else df[df.iloc[:, 1] == c_wc]
        text_wc = " ".join(df_wc[p_wc].fillna("").astype(str))
        if len(text_wc.strip()) > 20:
            wc = WordCloud(width=1000, height=500, background_color="white", stopwords=STOPWORDS_CAT).generate(text_wc.lower())
            st.image(wc.to_array(), use_container_width=True)

except Exception as e:
    st.error(f"❌ Error: {e}")
