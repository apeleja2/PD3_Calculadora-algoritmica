import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io

# 1. CONFIGURACIÓ I ESTILS
st.set_page_config(page_title="Analitzador de Veu PD3", layout="wide")

st.markdown("""
    <style>
    .comparison-card { background-color: #f1f3f5; border-radius: 10px; padding: 15px; border-top: 5px solid #3498db; }
    .quote-box { background-color: #ffffff; border-left: 5px solid #e67e22; padding: 10px; margin: 10px 0; font-style: italic; }
    .export-slide { background-color: #1e1e1e; color: #ffffff; padding: 40px; border-radius: 15px; text-align: center; margin-bottom: 20px; border: 2px solid #e67e22; }
    </style>
    """, unsafe_allow_html=True)

# 2. CÀRREGA I NETEJA DE DADES
sheet_id = "1srWD8f2oN_JeV4lwDYPe6ysLbRsXk9UZHE9vEmqVHlo"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

# Diccionari de paraules buides (Stopwords) molt complet en català
STOPWORDS_CAT = {
    "a", "amb", "de", "del", "dels", "la", "les", "el", "els", "un", "una", "unes", "uns", "i", "o", "que", "què", "per", "perquè", "però",
    "és", "ser", "estar", "són", "era", "eren", "fent", "fet", "fer", "va", "van", "hi", "ha", "han", "si", "no", "com", "ens", "et", "em",
    "tot", "tots", "tota", "totes", "molt", "més", "bastant", "només", "encara", "això", "aquell", "aquella", "meu", "teu", "seu", "nostre",
    "na", "n", "l", "s", "d", "aquesta", "aquest", "pels", "pel", "als", "al", "també", "sempre", "ara", "on", "quan", "estic", "estava",
    "maria", "pol", "aina" # Noms propis que surten a l'enunciat
}

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(csv_url)
    df.columns = [c.strip() for c in df.columns]
    return df

def generar_wc(text):
    if len(text) < 10: return None
    wc = WordCloud(
        width=800, height=400, background_color="white",
        stopwords=STOPWORDS_CAT, colormap="viridis", collocations=False
    ).generate(text.lower())
    return wc

try:
    df = load_data()
    escoles = sorted(df.iloc[:, 1].unique().tolist())
    preguntes = df.columns[3:7].tolist()

    # --- SIDEBAR ---
    st.sidebar.title("📊 Panell de Control")
    mode = st.sidebar.radio("Secció:", ["🏠 Comparativa de Centres", "☁️ Núvols per Pregunta", "🤖 Resum i Cites", "🎬 Exportació Visual"])
    
    # --- 1. COMPARATIVA DE CENTRES ---
    if mode == "🏠 Comparativa de Centres":
        st.header("🏠 Comparativa entre Centres")
        centres_sel = st.multiselect("Tria els centres a comparar:", escoles, default=escoles[:2])
        
        if centres_sel:
            cols = st.columns(len(centres_sel))
            for i, centre in enumerate(centres_sel):
                df_c = df[df.iloc[:, 1] == centre]
                with cols[i]:
                    st.markdown(f"<div class='comparison-card'><h3>🏫 {centre}</h3>", unsafe_allow_html=True)
                    st.metric("Total Respostes", len(df_c))
                    
                    # Núvol general del centre (totes les respostes juntes)
                    text_c = " ".join(df_c[preguntes].fillna("").astype(str).values.flatten())
                    wc = generar_wc(text_c)
                    if wc:
                        fig, ax = plt.subplots()
                        ax.imshow(wc)
                        ax.axis("off")
                        st.pyplot(fig)
                    st.markdown("</div>", unsafe_allow_html=True)

    # --- 2. NÚVOLS PER PREGUNTA ---
    elif mode == "☁️ Núvols per Pregunta":
        st.header("☁️ Anàlisi per Pregunta")
        centre_wc = st.selectbox("Tria un centre (o 'Tots'):", ["Tots"] + escoles)
        pregunta_wc = st.selectbox("Tria la pregunta:", preguntes)
        
        df_wc = df if centre_wc == "Tots" else df[df.iloc[:, 1] == centre_wc]
        text_wc = " ".join(df_wc[pregunta_wc].fillna("").astype(str))
        
        wc = generar_wc(text_wc)
        if wc:
            st.image(wc.to_array(), use_column_width=True)
        else:
            st.info("No hi ha prou dades per generar aquest núvol.")

    # --- 3. RESUM I CITES ---
    elif mode == "🤖 Resum i Cites":
        st.header("🤖 Resum Significatiu")
        centre_res = st.selectbox("Selecciona Centre:", escoles)
        df_res = df[df.iloc[:, 1] == centre_res]
        
        for p in preguntes:
            st.subheader(f"📌 {p}")
            respostes = df_res[p].dropna().tolist()
            
            # Lògica de "Punts Clau" basada en paraules més freqüents (no buides)
            text_p = " ".join(respostes).lower()
            paraules = [w for w in text_p.split() if w not in STOPWORDS_CAT and len(w) > 3]
            freq = pd.Series(paraules).value_counts().head(3).index.tolist()
            
            st.markdown(f"**Temes detectats:** {', '.join(freq).upper()}")
            
            # Cites literals significatives (les més llargues solen ser les més explicatives)
            respostes_ordenades = sorted(respostes, key=len, reverse=True)
            st.markdown("**Cites significatives:**")
            for cita in respostes_ordenades[:2]:
                st.markdown(f"<div class='quote-box'>\"{cita}\"</div>", unsafe_allow_html=True)

    # --- 4. EXPORTACIÓ VISUAL ---
    elif mode == "🎬 Exportació Visual":
        st.header("🎬 Exportació per a Presentacions")
        st.write("Aquesta secció genera una visió compacta del centre. Pots capturar-la o imprimir-la com a PDF.")
        centre_exp = st.selectbox("Centre a exportar:", escoles)
        df_exp = df[df.iloc[:, 1] == centre_exp]
        
        # Filtre per pregunta per no saturar el PDF/Captura
        p_exp = st.selectbox("De quina pregunta vols la veu de l'alumnat?", preguntes)

        for _, row in df_exp.iterrows():
            st.markdown(f"""
                <div class="export-slide">
                    <h1 style="color: #e67e22; font-size: 2.5rem;">"{row[p_exp]}"</h1>
                    <hr style="border: 1px solid #444">
                    <p style="font-size: 1.5rem;">👤 {row.iloc[2]} | 🏫 {row.iloc[1]}</p>
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error de dades: {e}")
