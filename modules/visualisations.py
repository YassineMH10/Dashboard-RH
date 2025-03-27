# modules/visualisations.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def afficher_treemaps_par_kpi(df, kpis):
    st.subheader("🌳 **Treemaps par KPI – Performance des agents**")

    for kpi in kpis:
        taille = df[f"Ecart_{kpi}"].abs() + 0.0001
        couleur = df[f"Ecart_{kpi}"].round(2)
        labels = df.apply(lambda r: f"{r['Agent']}<br>{r[f'Ecart_{kpi}']*100:.2f}%", axis=1)

        moyenne = round(couleur.mean() * 100, 2)
        titre = f"📊 <b>{kpi}</b> — Moyenne : {moyenne:.2f}%"

        fig = px.treemap(
            df,
            path=[px.Constant(kpi), "Agent"],
            values=taille,
            color=couleur,
            color_continuous_scale=["#a50026", "#d73027", "#fdae61", "#ffffbf", "#a6d96a", "#1a9850"],
            custom_data=["Agent", f"Ecart_{kpi}"]
        )
        fig.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>Écart : %{customdata[1]:.2%}<extra></extra>",
            texttemplate=labels
        )
        fig.update_layout(margin=dict(t=40, l=0, r=0, b=10), title=titre)
        st.plotly_chart(fig, use_container_width=True)

def afficher_courbe_evolution(df, agent, kpis):
    st.subheader(f"📈 **Évolution des écarts – {agent}**")

    df_agent = df[df["Agent"] == agent]
    df_melt = pd.melt(df_agent, id_vars=["Mois"], value_vars=[f"Ecart_{k}" for k in kpis],
                      var_name="KPI", value_name="Écart")
    df_melt["Écart"] = df_melt["Écart"] * 100
    df_melt["KPI"] = df_melt["KPI"].str.replace("Ecart_", "")

    fig = px.line(df_melt, x="Mois", y="Écart", color="KPI", markers=True,
                  color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)

def afficher_radar_agent(agent_row, kpis):
    st.subheader("🧭 **Radar de performance multi-KPI**")
    st.markdown("🎯 Plus la surface est grande, plus les objectifs sont atteints ou dépassés.")

    valeurs = [agent_row[f"Ecart_{k}"] * 100 for k in kpis]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=valeurs,
        theta=kpis,
        fill='toself',
        name='Écart (%)',
        marker=dict(color='deepskyblue')
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def afficher_tableau_detail(df, agent, kpis):
    st.subheader("📋 **Détails chiffrés par KPI et par mois**")
    df_agent = df[df["Agent"] == agent].copy()
    df_agent = df_agent[["Mois"] + [f"Ecart_{k}" for k in kpis] + ["Score_Global"]]
    df_agent = df_agent.sort_values("Mois")
    df_agent[[c for c in df_agent.columns if "Ecart_" in c or "Score" in c]] *= 100
    df_agent = df_agent.round(2)
    st.dataframe(df_agent)
