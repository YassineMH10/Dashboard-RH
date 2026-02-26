# app.py

import streamlit as st
from modules.uploader import uploader_fichier
from modules.settings import config_utilisateur
from modules.preprocessing import calcul_ecarts_objectifs
from modules.visualisations import (
    afficher_treemaps_par_kpi,
    afficher_radar_agent,
    afficher_courbe_evolution,
    afficher_tableau_detail
)
from modules.analytics import afficher_synthese_analytique
from modules.exports import export_excel
from modules.synthese_rh import generer_rapport_rh

# ✅ NEW
from modules.pda import afficher_pda


# 🔐 Authentification simple
def login():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("""
            <style>
                .intro {
                    text-align: center;
                    margin-top: 100px;
                    animation: fadeIn 1s ease-in-out;
                }
                .intro h1 {
                    font-size: 3em;
                    font-weight: 700;
                    color: #1f77b4;
                }
                .intro p {
                    font-size: 1.2em;
                    color: #444;
                }
                .footer {
                    position: fixed;
                    bottom: 15px;
                    left: 0;
                    width: 100%;
                    text-align: center;
                    font-size: 0.9em;
                    color: #888;
                }
                @keyframes fadeIn {
                    from {opacity: 0;}
                    to {opacity: 1;}
                }
            </style>

            <div class="intro">
                <h1>📊 Intelligent Dashboard TL – Intelcia</h1>
                <p>Prenez les bonnes décisions avec les bonnes données.</p>
            </div>

            <div class="footer">Developed by Yassine Mahamid</div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("### 🔐 Connexion requise")
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter")

            if submitted:
                if username == "admin" and password == "pass123":
                    st.session_state.auth = True
                    st.success("✅ Connexion réussie")
                else:
                    st.error("❌ Identifiants incorrects.")
        st.stop()


# ▶️ Configuration de la page
st.set_page_config(page_title="KPI Pro+", page_icon="📊", layout="wide")

# 🔐 Authentification
login()

# ✅ Page principale
st.title("📊 Tableau de bord – Analyse des KPI par objectifs")

# 1. Import des fichiers
df_resultats, df_objectifs = uploader_fichier()

if df_resultats is not None and df_objectifs is not None:
    # 2. Paramètres utilisateur
    params = config_utilisateur(df_resultats)

    # 3. Calculs
    df_ecarts = calcul_ecarts_objectifs(df_resultats, df_objectifs, params)

    # ✅ Onglets
    tab1, tab2, tab3, tab4 = st.tabs(["🌳 KPI", "👤 Agent", "🧠 Synthèse", "🧩 PDA"])

    with tab1:
        afficher_treemaps_par_kpi(df_ecarts, params["kpi"])

    with tab2:
        agent = st.selectbox("👤 Sélectionnez un agent :", df_ecarts["Agent"].unique())
        afficher_courbe_evolution(df_ecarts, agent, params["kpi"])
        afficher_tableau_detail(df_ecarts, agent, params["kpi"])
        agent_row = df_ecarts[df_ecarts["Agent"] == agent].iloc[-1]
        afficher_radar_agent(agent_row, params["kpi"])

    with tab3:
        afficher_synthese_analytique(df_ecarts, params)

    with tab4:
        afficher_pda(df_ecarts, params)

    # 7. Exports
    st.download_button(
        "📥 Télécharger les données Excel",
        data=export_excel(df_ecarts),
        file_name="rapport_kpi.xlsx"
    )

    # ⚠️ agent est défini dans tab2. Si user ne clique jamais tab2, ça peut planter.
    # Donc on fallback sur 1er agent si nécessaire.
    default_agent = df_ecarts["Agent"].unique()[0]
    agent_for_word = st.session_state.get("agent_for_word", default_agent)

    st.download_button(
        "📄 Télécharger le rapport Word",
        data=generer_rapport_rh(df_ecarts, agent_for_word, params),
        file_name=f"rapport_{agent_for_word}.docx"
    )

# ✅ Signature bas de page (après login)
st.markdown("""
    <hr style="margin-top: 30px;">
    <div style="text-align: center; font-size: 0.9em; color: #888;">
        Developed by Yassine Mahamid
    </div>
""", unsafe_allow_html=True)
