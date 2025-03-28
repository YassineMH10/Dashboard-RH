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

# ───────────────────────────────────────
# 🔐 Authentification simple & stylée
# ───────────────────────────────────────
def login():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("""
        <style>
            .login-box {
                background-color: #ffffff11;
                border-radius: 10px;
                padding: 40px 30px;
                max-width: 400px;
                margin: auto;
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
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

        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.image("https://img.icons8.com/fluency/96/lock.png", width=70)
        st.markdown("<h3 style='text-align:center'>🔐 Connexion sécurisée</h3>", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 Nom d'utilisateur")
            password = st.text_input("🔑 Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")

            if submit:
                if username == "admin" and password == "pass123":
                    st.session_state.auth = True
                    st.success("✅ Connexion réussie")
                else:
                    st.error("❌ Identifiants incorrects")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class='footer'>
            🔧 Developed by <b>Yassine Mahamid</b>
        </div>
        """, unsafe_allow_html=True)

        st.stop()

# ───────────────────────────────────────
# 🔧 Configuration générale
# ───────────────────────────────────────
st.set_page_config(layout="wide", page_title="📊 KPI Strategic Dashboard", page_icon="📈")

# 🔐 Auth
login()

st.title("📊 KPI Strategic Dashboard – Pilotage des Objectifs")

# ───────────────────────────────────────
# 1. Import fichiers
# ───────────────────────────────────────
df_resultats, df_objectifs = uploader_fichier()

if df_resultats is not None and df_objectifs is not None:
    # 2. Paramètres
    params = config_utilisateur(df_resultats)

    # 3. Pré-traitement
    df_ecarts = calcul_ecarts_objectifs(df_resultats, df_objectifs, params)

    # 4. Visualisations
    afficher_treemaps_par_kpi(df_ecarts, params["kpi"])

    agent = st.selectbox("👤 Sélectionner un agent :", df_ecarts["Agent"].unique())

    afficher_courbe_evolution(df_ecarts, agent, params["kpi"])
    afficher_tableau_detail(df_ecarts, agent, params["kpi"])

    agent_row = df_ecarts[df_ecarts["Agent"] == agent].iloc[-1]
    afficher_radar_agent(agent_row, params["kpi"])

    # 5. Synthèse RH
    afficher_synthese_analytique(df_ecarts, params)

    # 6. Exports
    st.markdown("### 📤 Export du rapport")
    st.download_button("📥 Télécharger Excel", data=export_excel(df_ecarts), file_name="rapport_kpi.xlsx")
    st.download_button("📄 Télécharger rapport RH (Word)", data=generer_rapport_rh(df_ecarts, agent, params), file_name=f"rapport_{agent}.docx")
