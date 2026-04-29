import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

# 1. CONFIGURACIÓ I ESTILS
st.set_page_config(page_title="Analitzador PD3", layout="wide")

COLORS_PREG = ["#feff9c", "#ffccf9", "#7afcff", "#c0ff8a"]
ICONES = ["✨", "🧠", "🚧", "🚀"]

st.markdown("""
    <style>
    .resum-box { 
        background-color: #ffffff; padding: 18px; border-radius: 12px; 
        border: 1px solid #e0e0e0; border-left: 10px solid #3498db; 
        margin-bottom: 20px; font-size: 1rem; line-height: 1.5; color: #333;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.02);
    }
    .quote-box { 
        font-style: italic; color: #555; padding: 8px 15px; 
        border-left: 3px solid #eee; margin-bottom: 10px; font-size: 0.85rem; 
        background: #fdfdfd;
    }
    .titol-pregunta-app { font-size: 1rem !important; color: #2c3e50 !important; font-weight: bold; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FILTRE DE NETEJA ULTRA-ESTRICTE (DICCIONARI AMPLIAT)
STOP_WORDS_ESTRICTE = {
    "a", "al", "als", "el", "els", "la", "les", "un", "una", "uns", "unes", "del", "dels", "de", "d'", "l'", "n'", "s'", "m'", "t'",
    "amb", "i", "que", "per", "què", "com", "si", "no", "o", "perquè", "perque", "però", "pero", "doncs", "en", "na",
    "m'ha", "agradat", "sigut", "era", "estat", "va", "ha", "hi", "he", "fet", "fer", "puc", "vull", "dir", "crec", "sembla",
    "compte", "vigila", "ves", "jo", "tu", "ell", "ella", "nosaltres", "vosaltres", "ells", "elles", "meva", "meu", "teu",
    "això", "aixo", "aquí", "aqui", "tot", "tota", "tots", "totes", "cada", "més", "mes", "quan", "també", "només", "és", "són",
    "activitats", "hem", "repte", "cartes", "descobrir", "multiplicaven", "antigament", "programar", "calculadora", "scratch",
    "quina", "perquè", "difícil", "aprendre", "multiplicar", "maneres", "diferents", "maria", "pol", "aina", "ensenyar",
    "ordinador", "imagina", "company", "companya", "comença", "moment", "diries", "complicat", "poguessis", "afegiries",
    "xula", "equivoqués", "mai", "aurora", "quico", "molt", "molta", "molts", "moltes", "bastant", "una", "un", "altre", "altres"
}

# 3. LÒGICA DE RESUM DINÀMIC (Sense plantilles)
def generar_resum_inteligent(respostes):
    if not respostes or len(respostes) < 2: return "No hi ha prou respostes per generar una anàlisi significativa."
    
    # Unim tot el text i el netegem
    text_complet = " ".join(respostes).lower()
    # Busquem les frases més llargues i riques en contingut (que no siguin "m'ha agradat")
    frases = [f.strip() for f in re.split(r'[.!?]', text_complet) if len(f.split()) > 6]
    
    # Extreure paraules amb més pes (no stop words)
    paraules_clau = [w for w in text_complet.replace(",", "").replace(".", "").split() if w not in STOP_WORDS_ESTRICTE and len(w) > 4]
    tops = pd.Series(paraules_clau).value_counts().head(5).index.tolist()
    
    if not frases: 
        return f"L'alumnat s'ha expressat de forma breu, posant el focus principal en conceptes com {', '.join(tops).upper()}."

    # Seleccionem idees clau basant-nos en les paraules més usades
    resum = f"L'anàlisi de les respostes indica una forta incidència en **{tops[0].upper()}** i **{tops[1].upper()}**. "
    resum += f"En general, les reflexions giren al voltant de la idea que {frases[0].strip()}. "
    if len(frases) > 1:
        resum += f"A més, es destaca que {frases[-1].strip()}."
    
    return resum

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

    # --- NÚVOLS DE PARAULES (Amb neteja extra) ---
    if mode == "☁️ Núvols":
        st.header("☁️ Núvols de paraules (P1, P3, P4)")
        p_sel = st.selectbox("Tria pregunta:", [preguntes[0], preguntes[2], preguntes[3]])
        txt = " ".join(df[p_sel].fillna("").astype(str)).lower()
        # Neteja de prefixes i apòstrofs
        txt = re.sub(r"\b[lmdnstn]'|'s\b", " ", txt)
        # Neteja de paraules curtes i stop words
        paraules_netes = [w for w in txt.split() if w not in STOP_WORDS_ESTRICTE and len(w) > 3]
        
        if len(paraules_netes) > 10:
            wc = WordCloud(width=900, height=500, background_color="white", colormap="tab10").generate(" ".join(paraules_netes))
            fig, ax = plt.subplots(); ax.imshow(wc, interpolation="bilinear"); ax.axis("off"); st.pyplot(fig)
        else:
            st.warning("No hi ha prou paraules significatives per generar un núvol útil.")

    # --- RESUM INTEL·LIGENT DINÀMIC ---
    elif mode == "🤖 Resum":
        st.header("🤖 Resum Dinàmic de la Veu de l'Alumnat")
        c_res = st.selectbox("Selecciona Centre:", escoles)
        df_c = df[df.iloc[:, 1] == c_res]
        
        for i, p in enumerate(preguntes):
            st.markdown(f"<div class='titol-pregunta-app'>{ICONES[i]} {p}</div>", unsafe_allow_html=True)
            res = df_c[p].dropna().tolist()
            if res:
                # El resum ara es construeix llegint les frases reals
                text_resum = generar_resum_inteligent(res)
                st.markdown(f'<div class="resum-box">{text_resum}</div>', unsafe_allow_html=True)
                
                # Selecció de les 5 cites més rellevants
                st.markdown("<b>Cites literals destacades:</b>", unsafe_allow_html=True)
                for cita in sorted(res, key=len, reverse=True)[:5]:
                    st.markdown(f'<div class="quote-box">"{cita}"</div>', unsafe_allow_html=True)

    # --- MURAL PDF (Sense canvis, mides reduïdes) ---
    elif mode == "📮 Mural PDF":
        c_mural = st.selectbox("Centre Mural:", escoles)
        df_mural = df[df.iloc[:, 1] == c_mural]
        # (Aquí es manté la teva lògica de mural que ja funciona bé)
        for i, p in enumerate(preguntes):
            st.markdown(f"<div class='titol-pregunta-app'>{ICONES[i]} {p}</div>", unsafe_allow_html=True)
            cols = st.columns(3)
            res_p = df_mural[df_mural[p].notna()]
            for idx, (_, row) in enumerate(res_p.iterrows()):
                with cols[idx % 3]:
                    st.markdown(f'<div class="mural-postit" style="background-color:{COLORS_PREG[i]}; font-size:0.8rem;">"{row[p]}"<br><small>({row.iloc[2]})</small></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Error: {e}")
