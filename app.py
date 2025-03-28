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

# ─────────────────────────────────────
# 🔐 AUTHENTIFICATION + PAGE STYLÉE
# ─────────────────────────────────────
def login():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("""
        <style>
        .main-container {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 30px 40px;
        }
        .left-panel {
            width: 55%;
            color: #eee;
            animation: fadeIn 1.2s ease-in-out;
        }
        .left-panel h1 {
            font-size: 32px;
            color: #00C0F2;
            margin-bottom: 10px;
        }
        .left-panel p {
            font-size: 15px;
            line-height: 1.8;
            color: #ccc;
        }
        .right-login {
            width: 35%;
            background-color: #1f1f1f;
            padding: 40px 30px;
            border-radius: 12px;
            box-shadow: 0 0 25px rgba(0,0,0,0.3);
        }
        .right-login h3 {
            text-align: center;
            margin-bottom: 20px;
        }
        .footer {
            position: fixed;
            bottom: 15px;
            width: 100%;
            text-align: center;
            color: #888;
            font-size: 0.85em;
        }
        .footer b {
            color: #00bfff;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<div class='main-container'>", unsafe_allow_html=True)

        # 🧠 Partie gauche
        st.markdown("""
        <div class='left-panel'>
            <h1>📊 Intelligent Dashboard TL – Intelcia</h1>
            <p><i>Prenez les bonnes décisions avec les bonnes données.</i></p>
            <p>
                ✅ Pilotage stratégique des KPI agents<br>
                📈 Visualisations claires et dynamiques<br>
                🧠 Suivi des écarts par rapport aux objectifs<br>
                📤 Export Word / Excel en un clic<br>
                👤 Détail multi-KPI par agent (radar, courbe)<br>
                🧾 Synthèse managériale automatique
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 🔐 Partie droite (login)
        st.markdown("<div class='right-login'>", unsafe_allow_html=True)
        st.image("https://img.icons8.com/color/96/lock--v1.png", width=60)
        st.markdown("<h3>🔐 Connexion sécurisée</h3>", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 Nom d'utilisateur")
            password = st.text_input("🔑 Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")

            if submit:
                if username == "admin" and password == "intelcia2024":
                    st.session_state.auth = True
                    st.success("✅ Connexion réussie")
                else:
                    st.error("❌ Identifiants incorrects")

        st.markdown("</div></div>", unsafe_allow_html=True)

        # ✍️ Signature
        st.markdown("""
        <div class='footer'>
            🔧 Developed by <b>Yassine Mahamid</b>
        </div>
        """, unsafe_allow_html=True)

        st.stop()

# ─────────────────────────────────────
# 🚀 CONFIGURATION GÉNÉRALE
# ─────────────────────────────────────
st.set_page_config(layout="wide", page_title="📊 TL Dashboard - Intelcia", page_icon="📈")

# 🔐 Lancement Auth
login()

# ─────────────────────────────────────
# 📊 CONTENU PRINCIPAL DU DASHBOARD
# ─────────────────────────────────────
st.title("📊 Intelligent Dashboard TL – Suivi des Objectifs")

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
