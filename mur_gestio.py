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
    .resum-box { background-color: #e8f4f8; padding: 20px; border-radius: 10px; border: 1px solid #3498db; margin-bottom: 25px; }
    
    /* Estil del mural a l'app */
    .mural-postit {
        padding: 15px; border-radius: 0px 0px 15px 0px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-bottom: 12px;
        border-left: 5px solid rgba(0,0,0,0.1); color: #2c3e50; min-height: 100px;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    .nom-infant { font-size: 0.8rem; color: #555; font-style: italic; margin-top: 8px; display: block; text-align: right; }
    
    /* Títol de pregunta discret en gris fosc */
    .titol-pregunta-app {
        font-size: 1.05rem !important;
        color: #444 !important;
        font-weight: bold;
        border-bottom: 1px solid #eee;
        margin-top: 20px;
        padding-bottom: 5px;
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
        c_mural = st.selectbox("Selecciona el centre:", escoles)
        df_mural = df[df.iloc[:, 1] == c_mural]
        
        # --- GENERACIÓ DE FITXER HTML PER A IMPRESSIÓ NETA ---
        html_export = f"""
        <html><head><meta charset="UTF-8"><title>Mural {c_mural}</title>
        <style>
            body {{ font-family: sans-serif; padding: 40px; background: white; }}
            .grid {{ display: flex; flex-wrap: wrap; gap: 15px; }}
            .postit {{ 
                width: 30%; padding: 15px; border-radius: 0 0 15px 0; 
                margin-bottom: 10px; border-left: 5px solid rgba(0,0,0,0.1);
                page-break-inside: avoid; font-family: 'Comic Sans MS', cursive;
                border: 1px solid #eee;
            }}
            .nom {{ font-size: 0.8rem; text-align: right; display: block; font-style: italic; margin-top: 5px; color: #555; }}
            .page-break {{ page-break-before: always; }}
            h1 {{ text-align: center; color: #2c3e50; font-size: 1.4rem; margin-bottom: 30px; }}
            h2 {{ color: #444; border-bottom: 1px solid #ccc; padding-top: 10px; font-size: 1.1rem; margin-bottom: 20px; }}
        </style></head><body>
        <h1>Resultats: {c_mural}</h1>
        """
        
        for i, p in enumerate(preguntes):
            salt = "page-break" if i > 0 else ""
            html_export += f"<div class='{salt}'><h2>{ICONES[i]} Pregunta {i+1}: {p}</h2><div class='grid'>"
            for _, row in df_mural.iterrows():
                if pd.notna(row[p]):
                    html_export += f"""
                    <div class="postit" style="background-color: {COLORS_PREG[i]};">
                        "{row[p]}"
                        <span class="nom">({row.iloc[2]})</span>
                    </div>"""
            html_export += "</div></div>"
        html_export += "</body></html>"

        # Botó de descàrrega fitxer HTML
        st.download_button(
            label="📥 DESCARREGAR MURAL PER A PDF",
            data=html_export,
            file_name=f"Mural_{c_mural.replace(' ', '_')}.html",
            mime="text/html"
        )
        st.info("Un cop baixis el fitxer, obre'l i prem Ctrl+P per desar-lo com a PDF net.")

        # Visualització App
        st.divider()
        st.markdown(f"<h2 style='text-align:center; color:#2c3e50;'>🏫 {c_mural}</h2>", unsafe_allow_html=True)
        for i, p in enumerate(preguntes):
            st.markdown(f"<div class='titol-pregunta-app'>{ICONES[i]} Pregunta {i+1}: {p}</div>", unsafe_allow_html=True)
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

    elif mode == "🤖 Resum":
        st.header("🤖 Anàlisi de la Veu")
        c_res = st.selectbox("Centre:", escoles)
        df_res = df[df.iloc[:, 1] == c_res]
        for i, p in enumerate(preguntes):
            st.subheader(f"{ICONES[i]} {p}")
            respostes = df_res[p].dropna().tolist()
            if respostes:
                text_p = " ".join(respostes).lower()
                paraules = [w for w in text_p.split() if w not in STOPWORDS_CAT and len(w) > 4]
                temes = list(dict.fromkeys(pd.Series(paraules).value_counts().head(5).index.tolist()))
                st.markdown(f'<div class="resum-box" style="border-left:10px solid {COLORS_PREG[i]}"><b>{TEMES[i]}</b><br>Paraules clau: {", ".join(temes).upper()}</div>', unsafe_allow_html=True)

    # Altres seccions (Comparativa, Núvols) es mantenen igual...
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
        st.header("☁️ Núvols de paraules")
        p_wc = st.selectbox("Pregunta:", preguntes)
        text_wc = " ".join(df[p_wc].fillna("").astype(str))
        if len(text_wc.strip()) > 20:
            wc = WordCloud(width=800, height=400, background_color="white", stopwords=STOPWORDS_CAT).generate(text_wc.lower())
            st.image(wc.to_array(), use_container_width=True)

except Exception as e:
    st.error(f"❌ Error: {e}")
