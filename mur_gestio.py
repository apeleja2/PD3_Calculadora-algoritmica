import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓ I ESTILS
st.set_page_config(page_title="Analitzador PD3", layout="wide")

COLORS_PREG = ["#feff9c", "#ffccf9", "#7afcff", "#c0ff8a"]
ICONES = ["✨", "🧠", "🚧", "🚀"]
TEMES = ["Preferides", "Reflexió", "Dificultats", "Millores"]

st.markdown("""
    <style>
    .resum-box { background-color: #f9f9f9; padding: 10px; border-radius: 8px; border: 1px solid #eee; margin-bottom: 10px; }
    .quote-box { font-style: italic; color: #444; padding: 2px 10px; border-left: 2px solid #ddd; margin-bottom: 4px; font-size: 0.8rem; }
    .mural-postit {
        padding: 8px; border-radius: 0px 0px 10px 0px; box-shadow: 1px 1px 3px rgba(0,0,0,0.05); 
        margin-bottom: 6px; border-left: 4px solid rgba(0,0,0,0.1); color: #2c3e50; 
        min-height: 60px; font-family: 'Comic Sans MS', cursive, sans-serif; font-size: 0.8rem;
    }
    .nom-infant { font-size: 0.7rem; color: #888; font-style: italic; margin-top: 2px; display: block; text-align: right; }
    .titol-pregunta-app { font-size: 0.85rem !important; color: #444 !important; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. FILTRE ESTRICTE (Noms i Paraules Buides)
STOP_WORDS = {
    "a", "amb", "de", "del", "dels", "la", "les", "el", "els", "un", "una", "i", "que", "per", "què", "com",
    "és", "són", "va", "ha", "hi", "si", "no", "tot", "molt", "més", "altre", "altres", "això", "aquí", "està",
    "maria", "pol", "aina", "aurora", "quico", "vull", "puc", "fer", "fet", "dir", "ser", "anar", "veure",
    "crec", "sembla", "tenir", "només", "també", "però", "perque", "perquè", "li", "ens", "tots", "cada", "molta"
}

# 3. DADES
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

    st.sidebar.title("🛠️ PD3")
    mode = st.sidebar.radio("Secció:", ["🏠 Comparativa", "☁️ Núvols", "🤖 Resum", "📮 Mural PDF"])

    if mode == "☁️ Núvols":
        st.header("☁️ Núvols de paraules (P1, P3, P4)")
        p_sel = st.selectbox("Tria:", [preguntes[0], preguntes[2], preguntes[3]])
        txt = " ".join(df[p_sel].fillna("").astype(str))
        if len(txt.strip()) > 5:
            wc = WordCloud(width=800, height=400, background_color="white", stopwords=STOP_WORDS).generate(txt.lower())
            fig, ax = plt.subplots(); ax.imshow(wc); ax.axis("off"); st.pyplot(fig)

    elif mode == "🤖 Resum":
        st.header("🤖 Resum i Cites Literals")
        c_res = st.selectbox("Centre:", escoles)
        df_c = df[df.iloc[:, 1] == c_res]
        for i, p in enumerate(preguntes):
            st.markdown(f"<div class='titol-pregunta-app'>{ICONES[i]} {p}</div>", unsafe_allow_html=True)
            res = df_c[p].dropna().tolist()
            if res:
                p_netes = [w for w in " ".join(res).lower().split() if w not in STOP_WORDS and len(w)>4]
                conc = list(dict.fromkeys(pd.Series(p_netes).value_counts().head(6).index.tolist()))
                st.markdown(f'<div class="resum-box" style="border-left:5px solid {COLORS_PREG[i]}"><b>{TEMES[i]}</b>: {", ".join(conc).upper()}</div>', unsafe_allow_html=True)
                for cita in sorted(res, key=len, reverse=True)[:5]:
                    st.markdown(f'<div class="quote-box">"{cita}"</div>', unsafe_allow_html=True)

    elif mode == "📮 Mural PDF":
        c_mural = st.selectbox("Centre:", escoles)
        df_mural = df[df.iloc[:, 1] == c_mural]
        
        # Generació del contingut HTML real per a la descàrrega
        html_export = f"""
        <html><head><meta charset='UTF-8'><style>
            body {{ font-family: sans-serif; padding: 20px; }}
            .grid {{ display: flex; flex-wrap: wrap; gap: 10px; }}
            .postit {{ width: 30%; padding: 10px; border-radius: 0 0 10px 0; margin-bottom: 10px; border-left: 5px solid #ccc; page-break-inside: avoid; font-family: 'Comic Sans MS'; font-size: 0.8rem; border: 1px solid #eee; }}
            .nom {{ font-size: 0.7rem; text-align: right; display: block; font-style: italic; }}
            .page-break {{ page-break-before: always; }}
            h2 {{ font-size: 1rem; color: #444; }}
        </style></head><body><h1>Mural: {c_mural}</h1>"""
        
        for i, p in enumerate(preguntes):
            salt = "page-break" if i > 0 else ""
            html_export += f"<div class='{salt}'><h2>{ICONES[i]} {p}</h2><div class='grid'>"
            res_p = df_mural[df_mural[p].notna()]
            for _, row in res_p.iterrows():
                html_export += f"<div class='postit' style='background-color:{COLORS_PREG[i]};'>\"{row[p]}\"<span class='nom'>({row.iloc[2]})</span></div>"
            html_export += "</div></div>"
        html_export += "</body></html>"

        st.download_button(
            label="📥 DESCARREGAR MURAL NET",
            data=html_export,
            file_name=f"Mural_{c_mural}.html",
            mime="text/html"
        )
        
        st.divider()
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
        if c_sel: st.write(f"S'està analitzant: {len(c_sel)} centres.")

except Exception as e:
    st.error(f"❌ Error: {e}")
