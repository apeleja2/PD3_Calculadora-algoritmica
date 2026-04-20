import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. CONFIGURACIÓ DE LA PÀGINA
st.set_page_config(page_title="Mur de Gestió PD3", layout="wide")

st.title("📊 Mur de Gestió: CALCULADORA ALGORÍTMICA")
st.markdown("---")

# 2. CONNEXIÓ AMB EL GOOGLE SHEET
# L'enllaç directe per exportar CSV
sheet_id = "1srWD8f2oN_JeV4lwDYPe6ysLbRsXk9UZHE9vEmqVHlo"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=60) # S'actualitza cada minut
def load_data(url):
    # Forcem la lectura de columnes per evitar errors de format
    return pd.read_csv(url)

try:
    df = load_data(csv_url)
    
    if df.empty:
        st.warning("⚠️ El full de càlcul està buit. Esperant la primera resposta...")
    else:
        # Netegem noms de columnes
        df.columns = [c.strip() for c in df.columns]
        
        # Identificació de columnes per posició
        # Col 0: Marca temporal, Col 1: Escola, Col 2: Nom, Col 3: P1...
        col_escola = df.columns[1]
        col_nom = df.columns[2]
        preguntes_disponibles = df.columns[3:].tolist()

        # --- BARRA LATERAL: FILTRES I CERCA ---
        st.sidebar.header("🔍 Filtres i Cerca")
        
        # Filtre d'escola
        llista_escoles = ["Totes"] + sorted(df[col_escola].unique().tolist())
        escola_seleccionada = st.sidebar.selectbox("Selecciona una Escola", llista_escoles)

        # Cercador global
        text_cerca = st.sidebar.text_input("Cerca per paraula clau (ex: 'scratch')")

        # Aplicació de filtres
        df_filtrat = df.copy()
        if escola_seleccionada != "Totes":
            df_filtrat = df_filtrat[df_filtrat[col_escola] == escola_seleccionada]
        
        if text_cerca:
            # Busca a totes les columnes de text
            mask = df_filtrat.apply(lambda r: r.astype(str).str.contains(text_cerca, case=False).any(), axis=1)
            df_filtrat = df_filtrat[mask]

        st.sidebar.write(f"📈 Mostrant **{len(df_filtrat)}** respostes")

        # --- SECCIÓ 1: NÚVOL DE PARAULES ---
        st.header("☁️ Conceptes clau")
        pregunta_triada = st.selectbox("Analitza el que diuen a:", preguntes_disponibles)

        # Llista ampliada de paraules buides (Stopwords en català)
        paraules_buides = {
            "que", "què", "la", "el", "i", "a", "es", "és", "en", "un", "una", "els", "les", "per", "perquè", 
            "més", "molt", "nan", "si", "no", "del", "dels", "de", "d'", "amb", "sobre", "per", "tot", "tota", 
            "tots", "totes", "hi", "ha", "han", "va", "van", "però", "o", "com", "ens", "li", "als", "altre", 
            "altres", "ser", "fer", "fet", "estat", "està", "molt", "bastant", "només", "encara", "això"
        }

        text_total = " ".join(df_filtrat[pregunta_triada].fillna("").astype(str).tolist())

        if len(text_total.strip()) > 10:
            wc = WordCloud(
                width=1000, height=450, 
                background_color="white", 
                colormap="winter", # Color blau/verd professional
                stopwords=paraules_buides,
                collocations=False
            ).generate(text_total.lower())
            
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.info("No hi ha prou text per generar l'anàlisi visual.")

        st.markdown("---")

        # --- SECCIÓ 2: RESPOSTES DETALLADES ---
        st.header("📝 Reflexions dels alumnes")
        
        if df_filtrat.empty:
            st.info("No s'ha trobat cap resposta amb aquests criteris.")
        else:
            # Fem servir pestanyes per organitzar el contingut
            tab_cards, tab_table = st.tabs(["🗂️ Targetes", "📊 Taula de dades"])

            with tab_cards:
                # Per evitar que la pàgina es bloquegi amb 650 respostes, 
                # només mostrem les primeres 100 i avisem si n'hi ha més
                max_mostrades = 100
                for i, (_, row) in enumerate(df_filtrat.iterrows()):
                    if i >= max_mostrades:
                        st.warning(f"S'estan mostrant les primeres {max_mostrades} respostes. Utilitza els filtres per concretar.")
                        break
                    
                    with st.expander(f"👤 {row[col_nom]} | 🏫 {row[col_escola]}"):
                        for p in preguntes_disponibles:
                            st.markdown(f"**{p}**")
                            st.write(row[p] if pd.notna(row[p]) else "Sense resposta")
                            st.markdown("<br>", unsafe_allow_html=True)

            with tab_table:
                st.dataframe(df_filtrat, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error de connexió: {e}")
    st.info("Revisa que el Google Sheet estigui compartit (Fitxer > Comparteix > Publica a la web).")
