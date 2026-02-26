# modules/pda_generator.py
import streamlit as st
import pandas as pd

RULES = {
    "DMT (sec)": {
        "bad_threshold": -0.05,
        "diagnostic": "DMT au-dessus de l’objectif : impact direct sur l’expérience client et la fluidité du traitement.",
        "actions": [
            "Coaching 1:1 : after-call (ACW) + reformulation + maîtrise du script",
            "2 écoutes ciblées + débrief structuré (faits / causes / actions)",
            "Contrôle mise en attente + standardisation du traitement",
        ],
        "expected": "Réduction du DMT sur la prochaine période",
    },
    "Qualité (%)": {
        "bad_threshold": -0.02,
        "diagnostic": "Qualité sous objectif : risque conformité et dégradation de la satisfaction.",
        "actions": [
            "Calibration Qualité + rappel des critères KO",
            "Coaching sur 3 erreurs récurrentes (preuves à l’appui)",
            "Shadowing avec top performer (1 session) + débrief",
        ],
        "expected": "Remontée qualité au-dessus du seuil sur la prochaine période",
    },
    "Prod": {
        "bad_threshold": -0.05,
        "diagnostic": "Productivité sous objectif : risque backlog et rendement faible.",
        "actions": [
            "Analyse cause racine : outil / process / complexité / rythme",
            "Coaching time-management + standardisation des cas",
            "Plan 1 semaine : objectifs journaliers + suivi TL",
        ],
        "expected": "Gain de productivité sur la prochaine période",
    },
    "ABS (%)": {
        "bad_threshold": -0.05,
        "diagnostic": "Absentéisme au-dessus de la cible : risque staffing et instabilité d’équipe.",
        "actions": [
            "Entretien TL : cause + engagement + plan de stabilisation",
            "Suivi RH si nécessaire (selon politique interne)",
            "Points hebdo + objectifs présence",
        ],
        "expected": "Stabilisation de la présence / réduction ABS",
    },
    "TH prod (€)": {
        "bad_threshold": -0.05,
        "diagnostic": "TH prod sous objectif : rendement économique en baisse.",
        "actions": [
            "Identifier levier prioritaire : Prod / Qualité / DMT",
            "Coaching ciblé sur le KPI le plus impactant",
            "Plan court : 3 actions mesurables sur 7 jours",
        ],
        "expected": "Amélioration TH prod via leviers prioritaires",
    },
}


def _select_trigger_kpis(df_row: pd.Series, kpis: list[str]):
    ecarts = []
    for k in kpis:
        col = f"Ecart_{k}"
        if col in df_row:
            ecarts.append((k, float(df_row[col])))

    if not ecarts:
        return [], None

    negatives = [(k, e) for k, e in ecarts if e < 0]
    worst = min(ecarts, key=lambda x: x[1])
    return negatives, worst


def generer_pda(df_ecarts: pd.DataFrame, params: dict):
    st.subheader("🧩 PerformTrack 360 — PDA Generator (TL)")

    if df_ecarts is None or df_ecarts.empty:
        st.warning("Aucune donnée KPI disponible.")
        return

    c1, c2 = st.columns(2)
    with c1:
        agent = st.selectbox("Agent", sorted(df_ecarts["Agent"].unique()))
    with c2:
        mois_ref = st.selectbox("Mois de référence", sorted(df_ecarts["Mois"].unique()))

    df_sel = df_ecarts[(df_ecarts["Agent"] == agent) & (df_ecarts["Mois"] == mois_ref)]
    if df_sel.empty:
        st.warning("Aucune donnée pour cet Agent/Mois.")
        return

    row = df_sel.iloc[0]
    kpis = params["kpi"]

    negatives, worst = _select_trigger_kpis(row, kpis)

    if all(float(row.get(f"Ecart_{k}", 0)) >= 0 for k in kpis):
        st.success("Aucun écart négatif détecté : PDA non requis sur cette période.")
        return

    worst_kpi, worst_ecart = worst
    worst_pct = round(worst_ecart * 100, 2)

    st.markdown(f"### 🎯 PDA — {agent} | {mois_ref}")
    st.markdown(f"**Déclencheur principal** : **{worst_kpi}** (`{worst_pct}%`)")

    rule = RULES.get(worst_kpi)
    if rule is None:
        diagnostic = "Écart KPI négatif : analyser cause racine et définir un plan d’action ciblé."
        actions = [
            "Qualifier la cause (process, outil, connaissance, comportement)",
            "Coaching ciblé + suivi sur 1 semaine",
            "Mesurer l’effet sur la période suivante",
        ]
        expected = "Réduction de l’écart sur la prochaine période"
    else:
        diagnostic = rule["diagnostic"]
        actions = rule["actions"]
        expected = rule["expected"]

    st.markdown("#### 1) Diagnostic opérationnel")
    st.write(diagnostic)

    st.markdown("#### 2) Actions TL recommandées")
    for a in actions:
        st.write(f"- {a}")

    if negatives:
        st.markdown("#### 3) KPI secondaires à surveiller")
        for k, e in sorted(negatives, key=lambda x: x[1]):
            if k == worst_kpi:
                continue
            st.write(f"- {k} : {round(e*100, 2)}%")

    st.markdown("#### 4) Impact attendu")
    st.write(expected)

    st.markdown("#### 5) PDA prêt à copier (format TL)")
    lines = []
    lines.append("PerformTrack 360 | TL Command Center — PDA")
    lines.append(f"Agent: {agent} | Période: {mois_ref}")
    lines.append(f"Déclencheur principal: {worst_kpi} ({worst_pct}%)")
    lines.append(f"Diagnostic: {diagnostic}")
    lines.append("Actions:")
    for a in actions:
        lines.append(f"- {a}")
    if negatives:
        sec = [f"{k} ({round(e*100,2)}%)" for k, e in negatives if k != worst_kpi]
        if sec:
            lines.append("KPI secondaires: " + ", ".join(sec))
    lines.append("Impact attendu: " + expected)

    st.code("\n".join(lines), language="text")
