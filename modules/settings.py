# modules/settings.py

import streamlit as st

def config_utilisateur(df_resultats):
    st.sidebar.header("⚙️ Paramètres")

    mois_dispo = df_resultats["Mois"].unique().tolist()
    agents_dispo = df_resultats["Agent"].unique().tolist()

    kpi_choisis = st.sidebar.multiselect(
        "📌 KPI à analyser",
        ["ABS (%)", "Prod", "Qualité (%)", "DMT (sec)", "TH prod (€)"],
        default=["ABS (%)", "Prod", "Qualité (%)", "DMT (sec)", "TH prod (€)"]
    )

    mois_selection = st.sidebar.multiselect("📅 Mois à inclure", mois_dispo, default=mois_dispo)
    agents_selection = st.sidebar.multiselect("👤 Agents", agents_dispo, default=agents_dispo)

    st.sidebar.markdown("### ⚖️ Pondérations des KPI")
    pond = {}
    for kpi in kpi_choisis:
        pond[kpi] = st.sidebar.slider(kpi, 0, 100, 20)

    total = sum(pond.values())
    if total != 100:
        st.sidebar.warning(f"⚠️ Pondérations = {total}%. Elles seront normalisées.")
    for k in pond:
        pond[k] = pond[k] / total

    return {
        "kpi": kpi_choisis,
        "mois": mois_selection,
        "agents": agents_selection,
        "pondérations": pond
    }
