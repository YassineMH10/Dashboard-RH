# modules/uploader.py

import streamlit as st
import pandas as pd

def uploader_fichier():
    st.sidebar.header("📁 Import des fichiers")

    fichier_resultats = st.sidebar.file_uploader("📈 Résultats des agents (kpi_resultats.xlsx)", type=["xlsx"])
    fichier_objectifs = st.sidebar.file_uploader("🎯 Objectifs mensuels (kpi_objectifs.xlsx)", type=["xlsx"])

    if not fichier_resultats or not fichier_objectifs:
        st.warning("⏳ Veuillez importer les deux fichiers.")
        return None, None

    try:
        df_resultats = pd.read_excel(fichier_resultats)
        df_objectifs = pd.read_excel(fichier_objectifs)

        if "Type" not in df_objectifs["Mois"].values:
            st.error("❌ Le fichier d'objectifs doit contenir une ligne 'Type'.")
            return None, None

        return df_resultats, df_objectifs

    except Exception as e:
        st.error(f"Erreur lors du chargement des fichiers : {e}")
        return None, None
