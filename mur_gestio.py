import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Configuració de la pàgina
st.set_page_config(page_title="Mur de Gestió PD3", layout="wide")

st.title("📊 Mur de Gestió: CALCULADORA ALGORÍTMICA")
st.markdown("Anàlisi en temps real de les reflexions dels alumnes")

# 1. Connexió amb el Google Sheet
# Substitueix aquesta URL per la del teu full de càlcul (la que has copiat abans)
sheet_url = "https://docs.google.com/spreadsheets/d/1srWD8f2oN_JeV4lwDYPe6ysLbRsXk9UZHE9vEmqVHlo/edit?usp=sharing"
# Un truc per llegir el fitxer directament com a CSV
csv_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
if '/edit' in sheet_url:
    csv_url = sheet_url.split('/edit')[0] + '/export?format=csv'

@st.cache_data(ttl=600) # Actualitza les dades cada 10 minuts
def load_data():
    return pd.read_csv(csv_url)

try:
    df = load_data()
    
    # 2. Filtres a la barra lateral
    st.sidebar.header("Filtres")
    escola = st.sidebar.selectbox("Selecciona una Escola", ["Totes"] + list(df.iloc[:, 1].unique()))

    if escola != "Totes":
        df = df[df.iloc[:, 1] == escola]

    # 3. Secció de Núvols de Paraules
    st.header("☁️ Nuvol de Paraules (Conceptes clau)")
    col_pregunta = st.selectbox("Tria la pregunta per analitzar:", 
                                ["P1: Què t'ha agradat més?", 
                                 "P2: Què és més difícil?", 
                                 "P3: On cal tenir cura?", 
                                 "P4: Millores per la calculadora"])
    
    # Mapeig de columnes (ajusta segons l'ordre del teu Excel)
    mapa_cols = {"P1: Què t'ha agradat més?": 3, "P2: Què és més difícil?": 4, 
                 "P3: On cal tenir cura?": 5, "P4: Millores per la calculadora": 6}
    
    text_analitzat = " ".join(df.iloc[:, mapa_cols[col_pregunta]].astype(str))
    
    if len(text_analitzat) > 10:
        wordcloud = WordCloud(width=800, height=400, background_color="white", 
                              colormap="Blues", stopwords=["que", "la", "el", "i", "a", "es"]).generate(text_analitzat)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.warning("No hi ha prou text per generar un núvol de paraules.")

    # 4. Llistat de Reflexions (Targetes)
    st.header("📝 Reflexions dels alumnes")
    for index, row in df.iterrows():
        with st.expander(f"⭐ {row.iloc[:, 2]} ({row.iloc[:, 1]})"):
            st.write(f"**P1:** {row.iloc[:, 3]}")
            st.write(f"**P2:** {row.iloc[:, 4]}")
            st.write(f"**P3:** {row.iloc[:, 5]}")
            st.write(f"**P4:** {row.iloc[:, 6]}")

except Exception as e:
    st.error("Encara no s'han rebut respostes o la URL del Google Sheet no és correcta.")
