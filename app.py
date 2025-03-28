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

# ────────────────────────────────
# 🔐 AUTHENTIFICATION UI PRO
# ────────────────────────────────
def login():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("""
        <style>
        /* Supprime tout le padding par défaut */
        .block-container {
            padding: 0rem 2rem 2rem 2rem;
        }

        /* Construit une page 100% hauteur */
        .login-fullscreen {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            animation: fadeIn 1s ease-in-out;
        }

        .login-title {
            text-align: center;
            margin-bottom: 30px;
        }

        .login-title h1 {
            font-size: 38px;
            font-weight: bold;
            color: #00C0F2;
            margin-bottom: 5px;
        }

        .login-title p {
            font-size: 15px;
            color: #cccccc;
            font-style: italic;
        }

        .login-box {
            background-color: #1e1e1e;
            padding: 35px 30px;
            border-radius: 14px;
            width: 350px;
            box-shadow: 0 0 25px rgba(0,0,0,0.3);
        }

        .login-box h3 {
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }

        .footer {
            position: fixed;
            bottom: 12px;
            width: 100%;
            text-align: center;
            color: #888;
            font-size: 0.85em;
        }

        .footer b {
            color: #00bfff;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<div class='login-fullscreen'>", unsafe_allow_html=True)

        # 🔷 Titre en haut
        st.markdown("""
        <div class='login-title'>
            <h1>📊 Intelligent Dashboard TL – Intelcia</h1>
            <p>Prenez les bonnes décisions avec les bonnes données.</p>
        </div>
        """, unsafe_allow_html=True)

        # 🔐 Formulaire de login
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.image("https://img.icons8.com/color/96/lock--v1.png", width=50)

        with st.form("login_form"):
            st.markdown("<h3>🔐 Connexion sécurisée</h3>", unsafe_allow_html=True)
            username = st.text_input("👤 Nom d'utilisateur")
            password = st.text_input("🔑 Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")

            if submit:
                if username == "admin" and password == "intelcia2024":
                    st.session_state.auth = True
                    st.success("✅ Connexion réussie")
                else:
                    st.error("❌ Identifiants incorrects")

        st.markdown("</div>", unsafe_allow_html=True)  # login-box
        st.markdown("</div>", unsafe_allow_html=True)  # login-fullscreen

        # ✍️ Signature bas de page
        st.markdown("""
        <div class='footer'>
            🔧 Developed by <b>Yassine Mahamid</b>
        </div>
        """, unsafe_allow_html=True)

        st.stop()

# ───────────────────────────────
# ⚙️ CONFIGURATION GÉNÉRALE
# ───────────────────────────────
st.set_page_config(layout="wide", page_title="📊 TL Dashboard - Intelcia", page_icon="📈")

# 🔐 Auth
login()

# ───────────────────────────────
# 📊 CONTENU PRINCIPAL
# ───────────────────────────────
st.title("📊 Intelligent Dashboard TL – Suivi des Objectifs et Performances")

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
