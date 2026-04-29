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
        padding: 15px; border-radius: 0px 0px 15px 0px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
        margin-bottom: 15px; border-left: 5px solid rgba(0,0,0,0.1); color: #2c3e50; 
        min-height: 100px; font-family: 'Comic Sans MS', cursive, sans-serif; font-size: 0.9rem;
    }
    .titol-pregunta { font-size: 1.2rem; font-weight: bold; margin-top: 25px; color: #333; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓ IA DIRECTA (v1beta ESTABLE)
def generar_resum_ia(respostes, pregunta):
    if not respostes or len(respostes) < 1:
        return "No hi ha prou dades."
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        text_input = "\n- ".join([str(r) for r in respostes if len(str(r)) > 3])
        payload = {
            "contents": [{"parts": [{"text": f"Ets un expert en educació. Analitza aquestes reflexions d'alumnes i resumeix en català i en dues frases les idees clau de: '{pregunta}'. Respostes: {text_input}"}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 400}
        }
        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        res_json = response.json()
        if "candidates" in res_json:
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        return "La IA està ocupada, torna-ho a provar."
    except Exception:
        return "Error de connexió amb la IA."

# 3. FILTRE STOPWORDS
STOP_WORDS_ESTRICTE = {"a", "al", "als", "el", "els", "la", "les", "un", "una", "uns", "unes", "del", "dels", "de", "d'", "l'", "n'", "s'", "m'", "t'", "amb", "i", "que", "per", "què", "com", "si", "no", "o", "perquè", "però", "doncs", "en", "ha", "hi", "he", "fet", "fer", "puc", "vull", "molt", "bastant"}

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

    # --- SECCIÓ 1: RESUM IA ---
    if mode == "🤖 Resum IA":
        st.header("🤖 Resum Intel·ligent")
        c_res = st.selectbox("Selecciona Centre:", escoles)
        df_c = df[df.iloc[:, 1] == c_res]
        if st.button("✨ Generar anàlisi"):
            for i, p in enumerate(preguntes):
                res = df_c[p].dropna().tolist()
                if res:
                    st.markdown(f"<div class='titol-pregunta'>{ICONES[i]} {p}</div>", unsafe_allow_html=True)
                    with st.spinner('Analitzant...'):
                        st.markdown(f'<div class="resum-box">{generar_resum_ia(res, p)}</div>', unsafe_allow_html=True)
                    with st.expander("📌 Veure cites"):
                        for cita in sorted(res, key=len, reverse=True)[:5]:
                            st.markdown(f'<div class="quote-box">"{cita}"</div>', unsafe_allow_html=True)

    # --- SECCIÓ 2: NÚVOLS ---
    elif mode == "☁️ Núvols":
        st.header("☁️ Núvols de Paraules")
        p_sel = st.selectbox("Tria pregunta:", preguntes)
        txt = " ".join(df[p_sel].fillna("").astype(str)).lower()
        txt = re.sub(r"\b[lmdnstn]'|'s\b", " ", txt)
        paraules = [w for w in txt.split() if w not in STOP_WORDS_ESTRICTE and len(w) > 3]
        if len(paraules) > 5:
            wc = WordCloud(width=800, height=400, background_color="white", colormap="Dark2").generate(" ".join(paraules))
            fig, ax = plt.subplots(); ax.imshow(wc); ax.axis("off"); st.pyplot(fig)

    # --- SECCIÓ 3: MURAL + EXPORTAR PDF ---
    elif mode == "📮 Mural PDF":
        c_mural = st.selectbox("Selecciona Centre:", escoles)
        df_mural = df[df.iloc[:, 1] == c_mural]
        
        # --- GENERACIÓ DE L'HTML PER IMPRIMIR ---
        html_print = f"""
        <html><head><style>
            @media print {{ .pb {{ page-break-before: always; }} }}
            body {{ font-family: sans-serif; padding: 20px; }}
            .postit {{ padding: 15px; border-radius: 10px; margin: 10px; display: inline-block; width: 40%; vertical-align: top; min-height: 100px; box-shadow: 2px 2px 5px #ccc; }}
            .titol {{ font-size: 1.5rem; font-weight: bold; color: #333; margin-top: 30px; border-bottom: 2px solid #333; }}
        </style></head><body>
        <h1>Mural de Reflexions: {c_mural}</h1>
        """
        
        for i, p in enumerate(preguntes):
            html_print += f"<div class='pb'></div><div class='titol'>{ICONES[i]} {p}</div>"
            res_p = df_mural[df_mural[p].notna()]
            
            st.markdown(f"<div class='titol-pregunta'>{ICONES[i]} {p}</div>", unsafe_allow_html=True)
            cols = st.columns(3)
            for idx, (_, row) in enumerate(res_p.iterrows()):
                txt_postit = row[p]
                autor = row.iloc[2]
                html_print += f"<div class='postit' style='background-color:{COLORS_PREG[i]};'>\"{txt_postit}\"<br><small>— {autor}</small></div>"
                with cols[idx % 3]:
                    st.markdown(f'<div class="mural-postit" style="background-color:{COLORS_PREG[i]};">"{txt_postit}"<br><p style="text-align:right; font-size:0.7rem;">— {autor}</p></div>', unsafe_allow_html=True)
        
        html_print += "</body></html>"
        
        # Botó per descarregar/imprimir
        st.sidebar.markdown("---")
        st.sidebar.download_button(
            label="📄 Descarregar Mural (HTML/PDF)",
            data=html_print,
            file_name=f"Mural_{c_mural}.html",
            mime="text/html"
        )
        st.sidebar.info("Un cop s'obri el fitxer descarregat, prem Ctrl+P (o Imprimir) i selecciona 'Guardar com a PDF'. Cada pregunta anirà a una pàgina.")

except Exception as e:
    st.error(f"Error: {e}")
