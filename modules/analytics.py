# modules/analytics.py

import streamlit as st

def afficher_synthese_analytique(df, params):
    st.subheader("🧠 **Synthèse analytique RH**")

    agents_up = df[df["Score_Global"] > 0.05]["Agent"].unique()
    agents_down = df[df["Score_Global"] < -0.05]["Agent"].unique()
    agents_stable = df[(df["Score_Global"] >= -0.05) & (df["Score_Global"] <= 0.05)]["Agent"].unique()

    score_moyen = round(df["Score_Global"].mean() * 100, 2)
    total = len(df["Agent"].unique())

    st.markdown(f"""
- 🟢 **Amélioration** : {len(agents_up)} agents
- 🟡 **Stables** : {len(agents_stable)} agents
- 🔴 **En baisse** : {len(agents_down)} agents

📊 **Score moyen global** : `{score_moyen:.2f}%` sur {total} agent(s)
""")

    if score_moyen > 5:
        st.success("✅ Tendance très positive.")
    elif score_moyen > 0:
        st.info("📈 Légère amélioration.")
    elif score_moyen > -5:
        st.warning("⚠️ Baisse modérée à surveiller.")
    else:
        st.error("🚨 Baisse significative : action recommandée.")
