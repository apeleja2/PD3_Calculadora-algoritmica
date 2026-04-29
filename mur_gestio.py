import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓ I ESTILS
st.set_page_config(page_title="Analitzador PD3", layout="wide")

COLORS_PREG = ["#feff9c", "#ffccf9", "#7afcff", "#c0ff8a"]
ICONES = ["✨", "🧠", "🚧", "🚀"]
TEMES = ["Activitats Preferides", "Reflexió de l'Aprenentatge", "Dificultats Detectades", "Propostes de Millora"]

st.markdown("""
    <style>
    .resum-box { 
        background-color: #f0f4f7; padding: 15px; border-radius: 10px; 
        border-left: 8px solid #3498db; margin-bottom: 15px; font-size: 0.95rem; line-height: 1.4;
    }
    .quote-box { 
        font-style: italic; color: #555; padding: 5px 15px; 
        border-left: 3px solid #ddd; margin-bottom: 8px; font-size: 0.85rem; 
    }
    .mural-postit {
        padding: 8px; border-radius: 0px 0px 10px 0px; box-shadow: 1px 1px 3px rgba(0,0,0,0.05); 
        margin-bottom: 6px; border-left: 4px solid rgba(0,0,0,0.1); color: #2c3e50; 
        min-height: 60px; font-family: 'Comic Sans MS', cursive, sans-serif; font-size: 0.8rem;
    }
    .nom-infant { font-size: 0.7rem; color: #888; font-style: italic; margin-top: 2px; display: block; text-align: right; }
    .titol-pregunta-app { font-size: 0.9rem !important; color: #333 !important; font-weight: bold; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FILTRE DE NETEJA ULTRA-ESTRICTE
STOP_WORDS = {
    "a", "al", "als", "el", "els", "la", "les", "un", "una", "uns", "unes", "del", "dels", "de", "d'", "l'", "n'", "s'", "m'", "t'",
    "amb", "i", "que", "per", "què", "com", "si", "no", "o", "perquè", "perque", "però", "pero", "doncs", "en", "na",
    "m'ha", "agradat", "sigut", "era", "estat", "va", "ha", "hi", "he", "fet", "fer", "puc", "vull", "dir", "crec", "sembla",
    "compte", "vigila", "ves", "jo", "tu", "ell", "ella", "nosaltres", "vosaltres", "ells", "elles", "meva", "meu", "teu",
    "això", "aixo", "aquí", "aqui", "tot", "tota", "tots", "totes", "cada", "més", "mes", "quan", "també", "només", "és", "són",
    "activitats", "hem", "repte", "cartes", "descobrir", "multiplicaven", "antigament", "programar", "calculadora", "scratch",
    "quina", "perquè", "difícil", "aprendre", "multiplicar", "maneres", "diferents", "maria", "pol", "aina", "ensenyar",
    "ordinador", "imagina", "company", "companya", "comença", "moment", "diries", "complicat", "poguessis", "afegiries",
    "xula", "equivoqués", "mai", "aurora", "quico"
}

# 3. FUNCIÓ PER GENERAR EL RESUM DE DUES FRASES (Lògica basada en paraules clau)
def generar_resum_narratiu(respostes, index_pregunta):
    if not respostes: return "Sense prou dades per generar un resum."
    
    # Neteja i freqüència
    text_total = " ".join(respostes).lower().replace("l'", " ").replace("m'", " ")
    paraules = [w for w in text_total.split() if w not in STOP_WORDS and len(w) > 4]
    claus = pd.Series(paraules).value_counts().head(3).index.tolist()
    claus_txt = ", ".join(claus).upper()
    
    # Estructures de frases segons el tema
    if index_pregunta == 0: # Preferides
        return f"L'alumnat destaca majoritàriament l'interès per conceptes com {claus_txt}, valorant positivament la part pràctica de l'activitat. La percepció general és de satisfacció i descoberta d'eines que no coneixien prèviament."
    elif index_pregunta == 1: # Reflexió
        return f"En el procés d'aprenentatge, el grup identifica que ha integrat millor elements relacionats amb {claus_txt}. Es percep una evolució en la comprensió del càlcul algorítmic i la seva aplicació en el context actual."
    elif index_pregunta == 2: # Dificultats
        return f"Les principals barreres detectades se centren en {claus_txt}, requerint un esforç extra en la lògica de programació. Malgrat els obstacles, la majoria ha trobat estratègies per superar els errors de codi."
    else: # Millores
        return f"Com a propostes de futur, els infants suggereixen ampliar les funcionalitats sobre {claus_txt} per fer l'eina més intuïtiva. L'enfocament es decanta cap a una major personalització i interacció amb el programa."

# 4. CÀRREGA DE DADES
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

    # --- NÚVOLS (Amb la neteja de la darrera proposta) ---
    if mode == "☁️ Núvols":
        st.header("☁️ Núvols de paraules netejats (P1, P3, P4)")
        p_sel = st.selectbox("Tria pregunta:", [preguntes[0], preguntes[2], preguntes[3]])
        txt = " ".join(df[p_sel].fillna("").astype(str)).lower()
        clean = txt.replace("l'", " ").replace("d'", " ").replace("m'", " ").replace("s'", " ").replace("t'", " ")
        if len(clean.strip()) > 5:
            wc = WordCloud(width=800, height=400, background_color="white", stopwords=STOP_WORDS, colormap="Dark2", min_word_length=3).generate(clean)
            fig, ax = plt.subplots(); ax.imshow(wc, interpolation="bilinear"); ax.axis("off"); st.pyplot(fig)

    # --- RESUM NARRATIU PER A PRESENTACIONS ---
    elif mode == "🤖 Resum":
        st.header("🤖 Resum Executiu per a Presentacions")
        c_res = st.selectbox("Selecciona Centre:", escoles)
        df_c = df[df.iloc[:, 1] == c_res]
        
        for i, p in enumerate(preguntes):
            st.markdown(f"<div class='titol-pregunta-app'>{ICONES[i]} {p}</div>", unsafe_allow_html=True)
            res = df_c[p].dropna().tolist()
            if res:
                # Generem el resum narratiu de dues frases
                resum_narratiu = generar_resum_narratiu(res, i)
                st.markdown(f'<div class="resum-box"><b>Resum per a presentació:</b><br>{resum_narratiu}</div>', unsafe_allow_html=True)
                
                # Cites destacades
                st.markdown("<b>Cites literals destacades:</b>", unsafe_allow_html=True)
                for cita in sorted(res, key=len, reverse=True)[:5]:
                    st.markdown(f'<div class="quote-box">"{cita}"</div>', unsafe_allow_html=True)

    # --- MURAL PDF ---
    elif mode == "📮 Mural PDF":
        c_mural = st.selectbox("Centre Mural:", escoles)
        df_mural = df[df.iloc[:, 1] == c_mural]
        html_exp = f"<html><head><meta charset='UTF-8'><style>body{{font-family:sans-serif;padding:20px}}.grid{{display:flex;flex-wrap:wrap;gap:10px}}.postit{{width:30%;padding:10px;border-radius:0 0 10px 0;margin-bottom:10px;border-left:5px solid #ccc;page-break-inside:avoid;font-family:'Comic Sans MS';font-size:0.8rem;border:1px solid #eee}}.nom{{font-size:0.7rem;text-align:right;display:block;font-style:italic}}.page-break{{page-break-before:always}}h2{{font-size:1rem;color:#444}}</style></head><body><h1>Mural: {c_mural}</h1>"
        for i, p in enumerate(preguntes):
            salt = "page-break" if i > 0 else ""
            html_exp += f"<div class='{salt}'><h2>{ICONES[i]} {p}</h2><div class='grid'>"
            for _, row in df_mural[df_mural[p].notna()].iterrows():
                html_exp += f"<div class='postit' style='background-color:{COLORS_PREG[i]};'>\"{row[p]}\"<span class='nom'>({row.iloc[2]})</span></div>"
            html_exp += "</div></div>"
        html_exp += "</body></html>"
        st.download_button("📥 DESCARREGAR MURAL NET", data=html_exp, file_name=f"Mural_{c_mural}.html", mime="text/html")
        for i, p in enumerate(preguntes):
            st.markdown(f"<div class='titol-pregunta-app'>{ICONES[i]} {p}</div>", unsafe_allow_html=True)
            cols = st.columns(3)
            res_p = df_mural[df_mural[p].notna()]
            for idx, (_, row) in enumerate(res_p.iterrows()):
                with cols[idx % 3]:
                    st.markdown(f'<div class="mural-postit" style="background-color:{COLORS_PREG[i]};">"{row[p]}"<span class="nom-infant">({row.iloc[2]})</span></div>', unsafe_allow_html=True)

    elif mode == "🏠 Comparativa":
        st.header("🏠 Comparativa")
        c_sel = st.multiselect("Centres:", escoles, default=escoles[:1])
        if c_sel: st.info(f"Anàlisi de {len(c_sel)} centres.")

except Exception as e:
    st.error(f"❌ Error: {e}")
