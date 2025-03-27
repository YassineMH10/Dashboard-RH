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

# 🎨 Configuration
st.set_page_config(layout="wide", page_title="KPI RH Pro+", page_icon="📊")
st.title("📊 Dashboard RH – Analyse KPI par objectifs")

# 1. Upload fichiers
df_resultats, df_objectifs = uploader_fichier()

if df_resultats is not None and df_objectifs is not None:
    # 2. Paramètres
    params = config_utilisateur(df_resultats)

    # 3. Traitement
    df_ecarts = calcul_ecarts_objectifs(df_resultats, df_objectifs, params)

    # 4. Treemaps
    afficher_treemaps_par_kpi(df_ecarts, params["kpi"])

    # 5. Agent sélectionné
    agent = st.selectbox("👤 Choisir un agent :", df_ecarts["Agent"].unique())

    afficher_courbe_evolution(df_ecarts, agent, params["kpi"])
    afficher_tableau_detail(df_ecarts, agent, params["kpi"])
    agent_row = df_ecarts[df_ecarts["Agent"] == agent].iloc[-1]
    afficher_radar_agent(agent_row, params["kpi"])

    # 6. Synthèse RH
    afficher_synthese_analytique(df_ecarts, params)

    # 7. Exports
    st.download_button("📥 Télécharger Excel", data=export_excel(df_ecarts), file_name="rapport_kpi.xlsx")
    st.download_button("📄 Télécharger rapport RH Word", data=generer_rapport_rh(df_ecarts, agent, params), file_name=f"rapport_{agent}.docx")
