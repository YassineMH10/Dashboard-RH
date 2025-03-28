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

# ────────────────────────────────────────────────
# 🔐 AUTHENTIFICATION – UI complète, pro & animée
# ────────────────────────────────────────────────
def login():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("""
        <style>
        html, body, [class*="css"] {
            height: 100%;
            margin: 0;
            padding: 0;
        }
        .page-wrapper {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            animation: fadeInTop 1.4s ease;
        }
        .banner {
            text-align: center;
            margin-bottom: 30px;
            animation: fadeInTop 1.2s ease;
        }
        .banner h1 {
            font-size: 36px;
            font-weight: bold;
            color: #00C0F2;
            margin-bottom: 5px;
        }
        .banner p {
            font-size: 16px;
            color: #ccc;
            font-style: italic;
        }
        .login-box {
            background-color: #1f1f1f;
            padding: 35px 30px;
            border-radius: 12px;
            width: 360px;
            box-shadow: 0 0 25px rgba(0,0,0,0.3);
            animation: fadeIn 1.6s ease;
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
        @keyframes fadeInTop {
            from { opacity: 0; transform: translateY(-30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<div class='page-wrapper'>", unsafe_allow_html=True)

        # 🔷 EN-TÊTE + SLOGAN
        st.markdown("""
        <div class='banner'>
            <h1>📊 Intelligent Dashboard TL – Intelcia</h1>
            <p>Prenez les bonnes décisions avec les bonnes données.</p>
        </div>
        """, unsafe_allow_html=True)

        # 🔐 FORMULAIRE LOGIN
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.image("https://img.icons8.com/color/96/lock--v1.png", width=50)

        with st.form("login_form"):
            st.markdown("<h3 style='text-align:center;'>🔐 Connexion sécurisée</h3>", unsafe_allow_html=True)
            username = st.text_input("👤 Nom d'utilisateur")
            password = st.text_input("🔑 Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")

            if submit:
                if username == "admin" and password == "intelcia2024":
                    st.session_state.auth = True
                    st.success("✅ Connexion réussie")
                else:
                    st.error("❌ Identifiants incorrects")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ✍️ SIGNATURE FOOTER
        st.markdown("""
        <div class='footer'>
            🔧 Developed by <b>Yassine Mahamid</b>
        </div>
        """, unsafe_allow_html=True)

        st.stop()

# ───────────────────────────────
# ⚙️ CONFIGURATION GLOBALE
# ───────────────────────────────
st.set_page_config(layout="wide", page_title="📊 TL Dashboard - Intelcia", page_icon="📈")

# 🔐 Auth
login()

# ───────────────────────────────
# 📊 DASHBOARD KPI – après login
# ───────────────────────────────
st.title("📊 Intelligent Dashboard TL – Suivi des Objectifs et Performances")

df_resultats, df_objectifs = uploader_fichier()

if df_resultats is not None and df_objectifs is not None:
    # 🧩 Paramètres utilisateur
    params = config_utilisateur(df_resultats)

    # 🔄 Calcul des écarts vs objectifs
    df_ecarts = calcul_ecarts_objectifs(df_resultats, df_objectifs, params)

    # 🌳 Treemaps par KPI
    afficher_treemaps_par_kpi(df_ecarts, params["kpi"])

    # 👤 Sélection Agent
    agent = st.selectbox("👤 Sélectionner un agent :", df_ecarts["Agent"].unique())

    afficher_courbe_evolution(df_ecarts, agent, params["kpi"])
    afficher_tableau_detail(df_ecarts, agent, params["kpi"])

    agent_row = df_ecarts[df_ecarts["Agent"] == agent].iloc[-1]
    afficher_radar_agent(agent_row, params["kpi"])

    # 🧠 Synthèse RH
    afficher_synthese_analytique(df_ecarts, params)

    # 📤 Exports
    st.markdown("### 📤 Export du rapport")
    st.download_button("📥 Télécharger Excel", data=export_excel(df_ecarts), file_name="rapport_kpi.xlsx")
    st.download_button("📄 Télécharger rapport Word", data=generer_rapport_rh(df_ecarts, agent, params), file_name=f"rapport_{agent}.docx")
