import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Configuració visual
st.set_page_config(page_title="Mur de Gestió PD3", layout="wide")

st.title("📊 Mur de Gestió: CALCULADORA ALGORÍTMICA")
st.markdown("---")

# 1. Connexió amb el Google Sheet (URL de visualització)
# Assegura't que el full estigui en "Qualsevol persona amb l'enllaç pot llegir"
sheet_url = "https://docs.google.com/spreadsheets/d/1vV0L8WqL1pGz0q9766VvFmU8o8pWc_X1T6O27Vl-x_M/edit#gid=0"

# Convertim la URL d'edició a URL de descàrrega directa CSV
def get_csv_url(url):
    if "/edit" in url:
        return url.split("/edit")[0] + "/export?format=csv"
    return url

csv_url = get_csv_url(sheet_url)

@st.cache_data(ttl=60) # Actualitza cada minut per veure respostes noves
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(csv_url)
    
    if df.empty:
        st.warning("⚠️ El full de càlcul està buit. Esperant la primera resposta...")
    else:
        # Netegem noms de columnes per si de cas
        df.columns = [c.strip() for c in df.columns]
        
        # BARRA LATERAL: Filtres
        st.sidebar.header("🔍 Filtres")
        # Suposem que la columna 1 és l'Escola
        col_escola = df.columns[1]
        llista_escoles = ["Totes"] + sorted(df[col_escola].unique().tolist())
        escola_seleccionada = st.sidebar.selectbox("Selecciona una Escola", llista_escoles)

        if escola_seleccionada != "Totes":
            df_filtrat = df[df[col_escola] == escola_seleccionada]
        else:
            df_filtrat = df

        # --- SECCIÓ 1: NÚVOL DE PARAULES ---
        st.header("☁️ Núvol de Paraules (Conceptes clau)")
        
        # Agafem només les columnes que semblen preguntes (de la 3 en endavant)
        preguntes_disponibles = df.columns[3:].tolist()
        pregunta_triada = st.selectbox("Tria la pregunta per analitzar:", preguntes_disponibles)

        text_total = " ".join(df_filtrat[pregunta_triada].astype(str).tolist())
        
        # Llista de paraules que volem ignorar (Stopwords)
        paraules_buides = ["que", "la", "el", "i", "a", "es", "en", "un", "una", "els", "les", "per", "perquè", "més", "molt", "nan", "si", "no"]

        if len(text_total) > 15:
            wc = WordCloud(
                width=1000, height=500, 
                background_color="white", 
                colormap="viridis",
                stopwords=paraules_buides
            ).generate(text_total)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.info("Encara no hi ha prou text en aquesta pregunta per generar un núvol.")

        st.markdown("---")

        # --- SECCIÓ 2: TARGETES DE RESPOSTES ---
        st.header("📝 Reflexions dels alumnes")
        
        col_nom = df.columns[2] # Suposem columna 2 = Nom

        for _, row in df_filtrat.iterrows():
            with st.expander(f"⭐ {row[col_nom]} | {row[col_escola]}"):
                for p in preguntes_disponibles:
                    st.markdown(f"**{p}**")
                    st.write(row[p])
                    st.markdown("---")

except Exception as e:
    st.error(f"Falta connexió o dades: Revisa que el Google Sheet tingui respostes i estigui compartit correctament.")
    st.info("Consell: Si acabes de crear el formulari, fes una resposta de prova tu mateix!")
