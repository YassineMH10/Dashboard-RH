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

# 🧪 Authentification simple
def login():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("""
            <style>
            .main {
                background-color: #f4f6f8;
            }
            .intro {
                text-align: center;
                margin-top: 100px;
                animation: fadeIn 2s ease-in-out;
            }
            .intro h1 {
                font-size: 3em;
                font-weight: 700;
                color: #1f77b4;
            }
            .intro p {
                font-size: 1.3em;
                color: #333;
            }
            .footer {
                position: fixed;
                bottom: 20px;
                width: 100%;
                text-align: center;
                color: #888;
                font-size: 0.9em;
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
                    st.experimental_rerun()
                else:
                    st.error("❌ Identifiants incorrects.")
        st.stop()

# ⚙️ Configuration de la page
st.set_page_config(page_title="KPI RH Pro+", page_icon="📊", layout="wide")

# 🔐 Login obligatoire
login()

# ✅ CONTENU PRINCIPAL DU DASHBOARD
st.title("📊 Tableau de bord RH – Performance des Agents par Objectifs")

# 1. Upload fichiers
df_resultats, df_objectifs = uploader_fichier()

if df_resultats is not None and df_objectifs is not None:
    # 2. Paramètres utilisateur
    params = config_utilisateur(df_resultats)

    # 3. Traitement des écarts
    df_ecarts = calcul_ecarts_objectifs(df_resultats, df_objectifs, params)

    # 4. Treemaps pro par KPI
    afficher_treemaps_par_kpi(df_ecarts, params["kpi"])

    # 5. Choix d’un agent pour analyse détaillée
    agent = st.selectbox("👤 Sélectionner un agent :", df_ecarts["Agent"].unique())

    # 6. Visualisations
    afficher_courbe_evolution(df_ecarts, agent, params["kpi"])
    afficher_tableau_detail(df_ecarts, agent, params["kpi"])
    agent_row = df_ecarts[df_ecarts["Agent"] == agent].iloc[-1]
    afficher_radar_agent(agent_row, params["kpi"])

    # 7. Synthèse RH intelligente
    afficher_synthese_analytique(df_ecarts, params)

    # 8. Exports
    st.download_button("📥 Télécharger les données Excel", data=export_excel(df_ecarts), file_name="rapport_kpi.xlsx")
    st.download_button("📄 Télécharger rapport RH Word", data=generer_rapport_rh(df_ecarts, agent, params), file_name=f"rapport_{agent}.docx")
