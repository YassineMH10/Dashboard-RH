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

# ─────────────────────────────────────────────
# 🔐 Page de Connexion avec Infos & Design Pro
# ─────────────────────────────────────────────
def login():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("""
        <style>
        .container-login {
            display: flex;
            justify-content: center;
            align-items: flex-start;
            margin-top: 50px;
        }
        .login-box {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 40px 30px;
            width: 400px;
            box-shadow: 0 0 15px rgba(0,0,0,0.3);
        }
        .info-box {
            padding-left: 60px;
            max-width: 500px;
            color: #cfcfcf;
        }
        .footer {
            position: fixed;
            bottom: 20px;
            width: 100%;
            text-align: center;
            color: #888;
            font-size: 0.9em;
        }
        .footer b {
            color: #00bfff;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<div class='container-login'>", unsafe_allow_html=True)

        # LOGIN
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.image("https://img.icons8.com/color/96/lock--v1.png", width=70)
        st.markdown("<h3 style='text-align:center'>🔐 Connexion sécurisée</h3>", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 Nom d'utilisateur")
            password = st.text_input("🔑 Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")

            if submit:
                if username == "admin" and password == "intelcia2024":
                    st.session_state.auth = True
                    st.success("✅ Connexion réussie !")
                else:
                    st.error("❌ Identifiants incorrects")
        st.markdown("</div>", unsafe_allow_html=True)

        # INFOS APP
        st.markdown("""
        <div class='info-box'>
            <h2>📊 Intelligent Dashboard TL – Intelcia</h2>
            <p>
            Un outil de pilotage stratégique conçu pour les Team Leaders chez Intelcia.<br><br>
            🎯 Suivi intelligent des <b>KPI agents</b><br>
            📈 Visualisations dynamiques et comparatives<br>
            ✅ Export Word / Excel<br>
            🧠 Analyse automatique des tendances & performances<br><br>
            <i>"Prenez les bonnes décisions avec les bonnes données."</i>
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # FOOTER
        st.markdown("""
        <div class='footer'>
            🔧 Developed by <b>Yassine Mahamid</b>
        </div>
        """, unsafe_allow_html=True)

        st.stop()

# ─────────────────────────────────────────────
# ⚙️ Configuration globale
# ─────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="📊 TL Dashboard - Intelcia", page_icon="📈")

# 🔐 Authentification
login()

# ─────────────────────────────────────────────
# 🧠 Accès au Dashboard
# ─────────────────────────────────────────────
st.title("📊 Intelligent Dashboard TL – Suivi des KPI Objectifs")

df_resultats, df_objectifs = uploader_fichier()

if df_resultats is not None and df_objectifs is not None:
    params = config_utilisateur(df_resultats)
    df_ecarts = calcul_ecarts_objectifs(df_resultats, df_objectifs, params)

    afficher_treemaps_par_kpi(df_ecarts, params["kpi"])

    agent = st.selectbox("👤 Sélectionner un agent :", df_ecarts["Agent"].unique())

    afficher_courbe_evolution(df_ecarts, agent, params["kpi"])
    afficher_tableau_detail(df_ecarts, agent, params["kpi"])

    agent_row = df_ecarts[df_ecarts["Agent"] == agent].iloc[-1]
    afficher_radar_agent(agent_row, params["kpi"])

    afficher_synthese_analytique(df_ecarts, params)

    st.markdown("### 📤 Export du rapport")
    st.download_button("📥 Télécharger Excel", data=export_excel(df_ecarts), file_name="rapport_kpi.xlsx")
    st.download_button("📄 Télécharger rapport Word", data=generer_rapport_rh(df_ecarts, agent, params), file_name=f"rapport_{agent}.docx")
