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
    .resum-box { background-color: #f0f7ff; padding: 20px; border-radius: 12px; border-left: 10px solid #007bff; margin-bottom: 20px; font-size: 1.05rem; color: #1a1a1a; line-height: 1.6; }
    .quote-box { font-style: italic; color: #555; padding: 10px; border-left: 3px solid #eee; font-size: 0.85rem; background: #fafafa; margin-bottom: 5px; }
    .mural-postit { padding: 10px; border-radius: 0px 0px 10px 0px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; border-left: 5px solid rgba(0,0,0,0.1); color: #2c3e50; font-family: 'Comic Sans MS', cursive, sans-serif; font-size: 0.8rem; }
    .titol-pregunta { font-size: 1.1rem; font-weight: bold; margin-top: 20px; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓ IA DIRECTA
def generar_resum_ia(respostes, pregunta):
    if not respostes: return "No hi ha dades."
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        text_input = "\n- ".join([str(r) for r in respostes if len(str(r)) > 3])
        payload = {"contents": [{"parts": [{"text": f"Resumeix en català i en dues frases les idees clau de: '{pregunta}': {text_input}"}]}]}
        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except: return "La IA no ha pogut respondre ara."

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
    mode = st.sidebar.radio("Vés a:", ["🤖 Resum IA", "☁️ Núvols", "📮 Mural PDF"])

    if mode == "🤖 Resum IA":
        st.header("🤖 Resum Intel·ligent")
        c_res = st.selectbox("Centre:", escoles)
        df_c = df[df.iloc[:, 1] == c_res]
        if st.button("✨ Generar"):
            for i, p in enumerate(preguntes):
                res = df_c[p].dropna().tolist()
                if res:
                    st.markdown(f"**{ICONES[i]} {p}**")
                    st.markdown(f'<div class="resum-box">{generar_resum_ia(res, p)}</div>', unsafe_allow_html=True)

    elif mode == "☁️ Núvols":
        st.header("☁️ Núvols")
        p_sel = st.selectbox("Pregunta:", preguntes)
        txt = " ".join(df[p_sel].fillna("").astype(str))
        if len(txt) > 10:
            wc = WordCloud(width=800, height=400, background_color="white").generate(txt)
            fig, ax = plt.subplots(); ax.imshow(wc); ax.axis("off"); st.pyplot(fig)

    elif mode == "📮 Mural PDF":
        c_mural = st.selectbox("Selecciona Centre:", escoles)
        df_mural = df[df.iloc[:, 1] == c_mural]
        
        # --- GENERACIÓ HTML PER IMPRIMIR ---
        html_print = f"""
        <html><head><style>
            @media print {{ 
                .page-break {{ page-break-before: always; }} 
                body {{ margin: 0; padding: 0; }}
            }}
            body {{ font-family: 'Segoe UI', sans-serif; color: #333; }}
            .portada {{ 
                height: 95vh; /* Alçada reduïda per evitar el salt de pàgina extra */
                display: flex; 
                flex-direction: column; 
                justify-content: center; 
                text-align: center; 
                padding: 40px;
                page-break-after: avoid; /* Evitem el salt automàtic que genera la pàgina en blanc */
            }}
            .portada h1 {{ font-size: 55px; margin-bottom: 10px; color: #007bff; }}
            .portada h2 {{ font-size: 32px; color: #555; margin-top: 0; }}
            .titol-seccio {{ 
                font-size: 22px; 
                font-weight: bold; 
                margin: 0 0 15px 0; 
                padding-bottom: 8px; 
                border-bottom: 3px solid #333; 
                page-break-after: avoid; 
            }}
            .seccio-pregunta {{ padding: 40px; }}
            .mosaics {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-start; }}
            .mini-postit {{ 
                width: 23%; padding: 10px; border-radius: 4px; font-size: 10px; 
                line-height: 1.2; break-inside: avoid; border: 1px solid rgba(0,0,0,0.05);
                display: flex; flex-direction: column; justify-content: space-between;
                min-height: 60px;
            }}
            .autor {{ text-align: right; font-size: 8px; font-weight: bold; margin-top: 5px; opacity: 0.7; }}
        </style></head><body>
            <div class="portada">
                <p style="font-size: 16px; text-transform: uppercase; letter-spacing: 5px; color: #888;">Informe de Reflexions</p>
                <h1>{c_mural}</h1>
                <h2>Projecte PD3</h2>
                <div style="margin-top: 50px; border-top: 3px solid #007bff; width: 120px; margin-left: auto; margin-right: auto;"></div>
            </div>
        """
        
        for i, p in enumerate(preguntes):
            # El salt de pàgina es posa SEMPRE a cada pregunta (el navegador gestionarà el pas de P1 a P2)
            html_print += f"<div class='seccio-pregunta page-break'>"
            html_print += f"<div class='titol-seccio'>{ICONES[i]} {p}</div><div class='mosaics'>"
            
            res_p = df_mural[df_mural[p].notna()]
            
            st.markdown(f"**{ICONES[i]} {p}**")
            cols = st.columns(4)
            
            for idx, (_, row) in enumerate(res_p.iterrows()):
                txt_postit = row[p]
                autor = row.iloc[2]
                html_print += f"""
                <div class="mini-postit" style="background-color:{COLORS_PREG[i]};">
                    <div>"{txt_postit}"</div>
                    <div class="autor">— {autor}</div>
                </div>"""
                with cols[idx % 4]:
                    st.markdown(f'<div class="mural-postit" style="background-color:{COLORS_PREG[i]};">"{txt_postit}"<br><p style="text-align:right; font-size:0.6rem;">— {autor}</p></div>', unsafe_allow_html=True)
            html_print += "</div></div>"
        
        html_print += "</body></html>"
        
        st.sidebar.markdown("---")
        st.sidebar.download_button(
            label="📄 Descarregar PDF (Mural Compacte)",
            data=html_print,
            file_name=f"PD3_{c_mural}.html",
            mime="text/html"
        )
        st.sidebar.caption("💡 Prem Ctrl+P i activa 'Gràfics de fons' per veure els colors.")

except Exception as e:
    st.error(f"Error: {e}")
