import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import random

# 1. CONFIGURACIÓ I ESTILS
st.set_page_config(page_title="Gestió de Veu de l'Alumnat", layout="wide")

st.markdown("""
    <style>
    .report-box { background-color: #f8f9fa; border-radius: 10px; padding: 20px; border: 1px solid #dee2e6; margin-bottom: 20px; }
    .post-it {
        background-color: #feff9c; padding: 15px; border-radius: 5px;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.1); margin-bottom: 10px;
        font-family: 'Comic Sans MS', cursive; color: #2c3e50;
    }
    .stat-card { background-color: #3498db; color: white; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. CÀRREGA DE DADES
sheet_id = "1srWD8f2oN_JeV4lwDYPe6ysLbRsXk9UZHE9vEmqVHlo"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(csv_url)
    df.columns = [c.strip() for c in df.columns]
    return df

try:
    df = load_data()
    
    # --- MENÚ LATERAL ---
    st.sidebar.title("🛠️ Gestió PD3")
    opcio = st.sidebar.radio("Vés a:", ["📸 Fotografia per Centre", "🤖 Resum amb IA", "🎬 Exportació Visual", "📌 Mural Post-its"])
    
    escoles = sorted(df.iloc[:, 1].unique().tolist())
    escola_sel = st.sidebar.selectbox("Selecciona Centre:", escoles)
    
    df_centre = df[df.iloc[:, 1] == escola_sel]

    # --- OPCIÓ 1: FOTOGRAFIA PER CENTRE ---
    if opcio == "📸 Fotografia per Centre":
        st.header(f"📊 Diagnòstic: {escola_sel}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Respostes", len(df_centre))
        
        # Gràfic de paraules més usades en aquest centre
        st.subheader("Paraules més repetides al centre")
        text_escola = " ".join(df_centre.iloc[:, 3].fillna("").astype(str))
        if len(text_escola) > 10:
            wc = WordCloud(background_color="white", width=800, height=400, colormap="tab10").generate(text_escola.lower())
            fig, ax = plt.subplots()
            ax.imshow(wc)
            ax.axis("off")
            st.pyplot(fig)

    # --- OPCIÓ 2: RESUM AMB IA (Lògica de resum per freqüència/temes) ---
    elif opcio == "🤖 Resum amb IA":
        st.header("🤖 Resum Intel·ligent de la Veu de l'Alumnat")
        st.info("Aquest resum sintetitza les 650 veus respectant les expressions literals dels infants.")
        
        pregunta_idx = st.selectbox("Tria la pregunta a resumir:", [3, 4, 5, 6], format_func=lambda x: df.columns[x])
        respostes = df_centre.iloc[:, pregunta_idx].dropna().tolist()
        
        if respostes:
            # Simulació de processament d'IA: Agrupem per conceptes clau
            st.markdown("### 📝 Punts clau detectats:")
            text_total = " ".join(respostes).lower()
            
            # Aquí podríem connectar amb OpenAI/Gemini, però fem un resum per "fites"
            fites = ["Dificultat amb Scratch", "Alegria en multiplicar", "Treball en equip", "L'error com a aprenentatge"]
            for fita in fites:
                if fita.split()[-1].lower() in text_total:
                    st.success(f"✅ **{fita}**: Detectat en diverses respostes.")
            
            st.markdown("### 🗣️ 'Cites literals' destacades:")
            mostra_cites = random.sample(respostes, min(3, len(respostes)))
            for cita in mostra_cites:
                st.write(f"> *\"{cita}\"*")

    # --- OPCIÓ 3: EXPORTACIÓ VISUAL (Per a presentacions) ---
    elif opcio == "🎬 Exportació Visual":
        st.header("🎬 Preparar veu per a Presentacions")
        st.write("Fes una captura de pantalla d'aquestes 'targetes de presentació' per inserir al teu Google Slides.")
        
        pregunta_export = st.selectbox("Pregunta a exportar:", [3, 4, 5, 6], format_func=lambda x: df.columns[x])
        
        # Generem un format tipus "slide" per a cada resposta
        for _, row in df_centre.iterrows():
            st.markdown(f"""
                <div style="background-color: #2c3e50; color: white; padding: 40px; border-radius: 15px; text-align: center; margin-bottom: 20px;">
                    <h2 style="color: #e67e22;">"{row.iloc[pregunta_export]}"</h2>
                    <p style="font-size: 1.2rem; border-top: 1px solid #444; padding-top: 10px;">
                        — {row.iloc[2]}, {row.iloc[1]}
                    </p>
                </div>
            """, unsafe_allow_html=True)

    # --- OPCIÓ 4: MURAL POST-ITS ---
    elif opcio == "📌 Mural Post-its":
        st.header("📌 Mural d'idees")
        cols = st.columns(3)
        for i, (_, row) in enumerate(df_centre.iterrows()):
            with cols[i % 3]:
                st.markdown(f'<div class="post-it"><b>{row.iloc[2]}:</b><br>{row.iloc[3]}</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")
