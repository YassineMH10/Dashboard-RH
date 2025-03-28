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

# 🔐 AUTHENTIFICATION AVEC PAGE DYNAMIQUE
def login():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("""
        <style>
            .login-container {
                display: flex;
                justify-content: space-between;
                margin-top: 30px;
                padding: 20px;
            }
            .left-info {
                width: 55%;
                padding: 20px;
            }
            .right-login {
                width: 40%;
                background-color: #1f1f1f;
                padding: 40px 30px;
                border-radius: 12px;
                box-shadow: 0 0 20px rgba(0,0,0,0.2);
            }
            .app-title {
                font-size: 32px;
                font-weight: bold;
                color: #00C0F2;
                margin-bottom: 5px;
            }
            .app-subtitle {
                font-size: 16px;
                color: #ccc;
                margin-bottom: 25px;
                font-style: italic;
            }
            .info-points {
                font-size: 15px;
                line-height: 1.6;
                color: #ddd;
                margin-top: 20px;
                animation: fadein 2s ease-in-out;
            }
            .footer {
                position: fixed;
                bottom: 15px;
                width: 100%;
                text-align: center;
                font-size: 0.85em;
                color: #888;
            }
            .footer b {
                color: #00bfff;
            }
            @keyframes fadein {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<div class='login-container'>", unsafe_allow_html=True)

        # ➤ GAUCHE - Description de l’app
        st.markdown("""
        <div class='left-info'>
            <div class='app-title'>📊 Intelligent Dashboard TL – Intelcia</div>
            <div class='app-subtitle'>Prenez les bonnes décisions avec les bonnes données.</div>
            <div class='info-points'>
                📈 Analyse intelligente des <b>KPI agents</b><br>
                📊 Visualisations interactives & évolutives<br>
                🧠 Écarts par rapport aux <b>objectifs définis</b><br>
                📤 Exportation <b>Word / Excel</b> personnalisée<br>
                🔍 Détail mensuel par agent, avec radar<br>
                🧾 Synthèse analytique automatique
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ➤ DROITE - Login
        st.markdown("<div class='right-login'>", unsafe_allow_html=True)
        st.image("https://img.icons8.com/color/96/lock--v1.png", width=60)
        st.markdown("<h3 style='text-align:center;'>🔐 Connexion sécurisée</h3>", unsafe_allow_html=True)

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

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class='footer'>
            🔧 Developed by <b>Yassine Mahamid</b>
        </div>
        """, unsafe_allow_html=True)

        st.stop()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎯 DÉMARRAGE DU DASHBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(layout="wide", page_title="📊 TL Dashboard Intelcia", page_icon="📈")

# 🔐 Auth
login()

# ✅ Accès au dashboard après login
st.title("📊 Intelligent Dashboard TL – Suivi des Objectifs & Performance")

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
