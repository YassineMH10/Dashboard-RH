# modules/pda.py
import streamlit as st
import pandas as pd
from datetime import date

from modules.pda_store import load_actions, add_action, update_action, delete_action

ACTION_TYPES = [
    "Coaching 1:1 (écoute ciblée)",
    "Rappel process / script",
    "Shadowing / double écoute",
    "Plan de montée en compétence",
    "Calibration Qualité",
    "Réglage organisation (pause, after-call, etc.)",
    "Escalade OPS (blocage outil / flux / knowledge)",
]

STATUSES = ["À faire", "En cours", "Fait", "Bloqué"]
PRIORITIES = ["P1", "P2", "P3"]


def _kpi_blocking_rules(kpi: str, ecart: float):
    """
    ecart en fraction: -0.08 = -8%
    """
    if "Qualité" in kpi and ecart < -0.02:
        return "KPI critique : Qualité en baisse → action immédiate."
    if "ABS" in kpi and ecart < -0.05:
        return "Risque staffing : ABS dégradée → plan d’action RH."
    if "DMT" in kpi and ecart < -0.05:
        return "Risque CX : DMT dégradée → coaching + quick wins."
    return None


def afficher_pda(df_ecarts: pd.DataFrame, params: dict):
    st.subheader("🧩 PDA – Plan d’Action TL (création, suivi, mesure)")

    if df_ecarts is None or df_ecarts.empty:
        st.warning("Aucune donnée KPI disponible.")
        return

    # --- Contexte ---
    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        agent = st.selectbox("Agent", sorted(df_ecarts["Agent"].unique()))
    with c2:
        kpi = st.selectbox("KPI", params["kpi"])
    with c3:
        mois_ref = st.selectbox("Mois de référence", sorted(df_ecarts["Mois"].unique()))

    df_sel = df_ecarts[(df_ecarts["Agent"] == agent) & (df_ecarts["Mois"] == mois_ref)]
    if df_sel.empty:
        st.warning("Aucune donnée KPI pour ce couple Agent/Mois.")
        return

    ecart = float(df_sel.iloc[0][f"Ecart_{kpi}"])
    ecart_pct = round(ecart * 100, 2)

    hint = _kpi_blocking_rules(kpi, ecart)
    if hint:
        st.error(hint)
    else:
        st.info("Crée une action avec owner + deadline + preuve attendue (sinon ça ne sert à rien).")

    st.markdown(f"**Écart actuel ({kpi})** : `{ecart_pct}%` (référence: {mois_ref})")

    # --- Création ---
    with st.expander("➕ Créer une action PDA", expanded=True):
        with st.form("pda_create"):
            a1, a2, a3 = st.columns(3)
            with a1:
                action_type = st.selectbox("Type d’action", ACTION_TYPES)
            with a2:
                owner = st.text_input("Owner", value="TL")
            with a3:
                due = st.date_input("Deadline", value=date.today())

            b1, b2, b3 = st.columns(3)
            with b1:
                priority = st.selectbox("Priorité", PRIORITIES, index=0)
            with b2:
                status = st.selectbox("Statut", STATUSES, index=0)
            with b3:
                expected = st.text_input("Impact attendu", value="")

            description = st.text_area(
                "Description (plan concret)",
                height=100,
                placeholder="Ex: 2 écoutes ciblées + débrief, focus: reformulation + after-call.",
            )

            submitted = st.form_submit_button("Créer l’action")
            if submitted:
                payload = {
                    "agent": agent,
                    "kpi": kpi,
                    "mois_ref": mois_ref,
                    "ecart_pct": ecart_pct,
                    "action_type": action_type,
                    "description": description.strip(),
                    "owner": owner.strip(),
                    "due_date": str(due),
                    "priority": priority,
                    "status": status,
                    "preuve": "",
                    "expected_impact": expected.strip(),
                    "tags": [],
                }
                add_action(payload)
                st.success("Action PDA créée.")

    # --- Suivi ---
    st.markdown("### 📌 Suivi des actions")
    actions = load_actions()
    df_actions = pd.DataFrame(actions) if actions else pd.DataFrame()

    if df_actions.empty:
        st.warning("Aucune action enregistrée pour le moment.")
        return

    # Filtres
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        flt_agent = st.selectbox("Filtre Agent", ["Tous"] + sorted(df_actions["agent"].unique().tolist()))
    with f2:
        flt_status = st.selectbox("Filtre Statut", ["Tous"] + STATUSES)
    with f3:
        flt_kpi = st.selectbox("Filtre KPI", ["Tous"] + sorted(df_actions["kpi"].unique().tolist()))
    with f4:
        flt_prio = st.selectbox("Filtre Priorité", ["Tous"] + PRIORITIES)

    view = df_actions.copy()
    if flt_agent != "Tous":
        view = view[view["agent"] == flt_agent]
    if flt_status != "Tous":
        view = view[view["status"] == flt_status]
    if flt_kpi != "Tous":
        view = view[view["kpi"] == flt_kpi]
    if flt_prio != "Tous":
        view = view[view["priority"] == flt_prio]

    cols = [
        "id",
        "created_at",
        "agent",
        "kpi",
        "mois_ref",
        "ecart_pct",
        "priority",
        "status",
        "owner",
        "due_date",
        "expected_impact",
        "description",
        "preuve",
    ]
    view = view[[c for c in cols if c in view.columns]]

    st.dataframe(
        view.sort_values(["priority", "due_date"], ascending=[True, True]),
        use_container_width=True,
    )

    st.markdown("### ✏️ Mettre à jour une action")
    action_ids = view["id"].tolist()
    if not action_ids:
        st.info("Aucune action dans ce filtre.")
        return

    selected_id = st.selectbox("Sélectionner une action (id)", action_ids)
    row = df_actions[df_actions["id"] == selected_id].iloc[0].to_dict()

    u1, u2, u3 = st.columns(3)
    with u1:
        new_status = st.selectbox(
            "Nouveau statut",
            STATUSES,
            index=STATUSES.index(row.get("status", "À faire")) if row.get("status") in STATUSES else 0,
        )
    with u2:
        new_owner = st.text_input("Owner (maj)", value=row.get("owner", "TL"))
    with u3:
        new_prio = st.selectbox(
            "Priorité (maj)",
            PRIORITIES,
            index=PRIORITIES.index(row.get("priority", "P2")) if row.get("priority") in PRIORITIES else 1,
        )

    new_preuve = st.text_input("Preuve / lien / note", value=row.get("preuve", ""))
    new_expected = st.text_input("Impact attendu (maj)", value=row.get("expected_impact", ""))

    b1, b2 = st.columns([1, 1])
    with b1:
        if st.button("✅ Enregistrer la mise à jour"):
            ok = update_action(
                selected_id,
                {
                    "status": new_status,
                    "owner": new_owner.strip(),
                    "priority": new_prio,
                    "preuve": new_preuve.strip(),
                    "expected_impact": new_expected.strip(),
                },
            )
            if ok:
                st.success("Action mise à jour.")
            else:
                st.error("Impossible de mettre à jour l’action (id introuvable).")

    with b2:
        if st.button("🗑️ Supprimer l’action"):
            ok = delete_action(selected_id)
            if ok:
                st.warning("Action supprimée.")
            else:
                st.error("Impossible de supprimer (id introuvable).")
