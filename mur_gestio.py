import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import requests
import json
import re

# 1. CONFIGURACIÓ DE PÀGINA I ESTILS
st.set_page_config(page_title="Analitzador PD3", layout="wide")

COLORS_PREG = ["#feff9c", "#ffccf9", "#7afcff", "#c0ff8a"]
ICONES = ["✨", "🧠", "🚧", "🚀"]

st.markdown("""
    <style>
    .resum-box { 
        background-color: #f0f7ff; padding: 20px; border-radius: 12px; 
        border-left: 10px solid #007bff; margin-bottom: 20px; 
        font-size: 1.05rem; color: #1a1a1a; line-height: 1.6;
    }
    .quote-box { 
        font-style: italic; color: #555; padding: 10px; border-left: 3px solid #eee; 
        font-size: 0.85rem; background: #fafafa; margin-bottom: 5px;
    }
    .mural-postit {
        padding: 10px; border-radius: 0px 0px 10px 0px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
        margin-bottom: 10px; border-left: 5px solid rgba(0,0,0,0.1); color: #2c3e50; 
        min-height: 80px; font-family: 'Comic Sans MS', cursive, sans-serif; font-size: 0.85rem;
    }
    .titol-pregunta { font-size: 1.1rem; font-weight: bold; margin-top: 20px; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓ IA DIRECTA (CONFIGURACIÓ v1beta ESTABLE)
def generar_resum_ia(respostes, pregunta):
    if not respostes or len(respostes) < 1:
        return "No hi ha prou dades."
    
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        # Fem servir v1beta per assegurar compatibilitat amb Gemini 1.5 a Europa
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        text_input = "\n- ".join([str(r) for r in respostes if len(str(r)) > 3])
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Ets un expert en educació. Analitza aquestes reflexions d'alumnes i resumeix en català i en exactament dues frases les idees clau de: '{pregunta}'. Respostes: {text_input}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 400,
            }
        }
        
        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        res_json = response.json()
        
        # Intent de seguretat si el model Flash no respon
        if "error" in res_json:
            url_alt = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            response = requests.post(url_alt, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
            res_json = response.json()

        if "candidates" in res_json:
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "La IA està processant altres peticions. Torna a provar-ho en uns segons."
            
    except Exception as e:
        return f"Error de connexió: {str(e)}"

# 3. FILTRE STOPWORDS (Per al Núvol)
STOP_WORDS_ESTRICTE = {
    "a", "al", "als", "el", "els", "la", "les", "un", "una", "uns", "unes", "del", "dels", "de", "d'", "l'", "n'", "s'", "m'", "t'",
    "amb", "i", "que", "per", "què", "com", "si", "no", "o", "perquè", "perque", "però", "pero", "doncs", "en", "na",
    "m'ha", "agradat", "sigut", "era", "estat", "va", "ha", "hi", "he", "fet", "fer", "puc", "vull", "dir", "crec", "sembla",
    "molt", "molta", "molts", "moltes", "bastant", "això", "aixo", "aquí", "aqui", "tot", "tota", "cada", "més", "mes",
    "activitats", "hem", "repte", "cartes", "descobrir", "multiplicaven", "programar", "calculadora", "scratch"
}

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
    mode = st.sidebar.radio("Vés a:", ["🤖 Resum IA", "☁️ Núvols", "📮 Mural PDF"])

    # --- SECCIÓ 1: RESUM AMB IA + CITES ---
    if mode == "🤖 Resum IA":
        st.header("🤖 Resum Intel·ligent i Cites Destacades")
        c_res = st.selectbox("Selecciona Centre:", escoles)
        df_c = df[df.iloc[:, 1] == c_res]
        
        if st.button("✨ Generar anàlisi"):
            for i, p in enumerate(preguntes):
                res = df_c[p].dropna().tolist()
                if len(res) > 0:
                    st.markdown(f"<div class='titol-pregunta'>{ICONES[i]} {p}</div>", unsafe_allow_html=True)
                    
                    with st.spinner('Analitzant dades...'):
                        resultat_ia = generar_resum_ia(res, p)
                        st.markdown(f'<div class="resum-box">{resultat_ia}</div>', unsafe_allow_html=True)
                    
                    # --- AQUÍ RECUPEREM LES CITES ---
                    with st.expander("📌 Veure les cites més rellevants"):
                        # Ordenem per longitud per mostrar les frases més completes
                        cites_destacades = sorted(res, key=len, reverse=True)[:5]
                        for cita in cites_destacades:
                            st.markdown(f'<div class="quote-box">"{cita}"</div>', unsafe_allow_html=True)
                else:
                    st.info(f"Sense dades per a la pregunta: {p}")

    # --- SECCIÓ 2: NÚVOLS ---
    elif mode == "☁️ Núvols":
        st.header("☁️ Núvols de Paraules")
        p_sel = st.selectbox("Tria pregunta:", preguntes)
        txt = " ".join(df[p_sel].fillna("").astype(str)).lower()
        txt = re.sub(r"\b[lmdnstn]'|'s\b", " ", txt)
        paraules_netes = [w for w in txt.split() if w not in STOP_WORDS_ESTRICTE and len(w) > 3]
        if len(paraules_netes) > 5:
            wc = WordCloud(width=800, height=400, background_color="white", colormap="Dark2").generate(" ".join(paraules_netes))
            fig, ax = plt.subplots(); ax.imshow(wc); ax.axis("off"); st.pyplot(fig)

    # --- SECCIÓ 3: MURAL ---
    elif mode == "📮 Mural PDF":
        c_mural = st.selectbox("Centre:", escoles)
        df_mural = df[df.iloc[:, 1] == c_mural]
        for i, p in enumerate(preguntes):
            st.markdown(f"<div class='titol-pregunta'>{ICONES[i]} {p}</div>", unsafe_allow_html=True)
            cols = st.columns(3)
            res_p = df_mural[df_mural[p].notna()]
            for idx, (_, row) in enumerate(res_p.iterrows()):
                with cols[idx % 3]:
                    st.markdown(f'<div class="mural-postit" style="background-color:{COLORS_PREG[i]};">"{row[p]}"<br><small>— {row.iloc[2]}</small></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")
