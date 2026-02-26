# modules/pda_generator.py
import streamlit as st
import pandas as pd
from datetime import date, timedelta

APP_BRAND_LINE = "PerformTrack 360 | TL Command Center — Intelcia"

# ------------------------------------------------------------
# Management playbook (call center oriented)
# ------------------------------------------------------------
MANAGEMENT_MODES = {
    "Coaching (GROW)": {
        "when": "Si l’agent a la base mais manque de méthode / structure.",
        "rituals": [
            "1:1 30 min (GROW) : Goal → Reality → Options → Will",
            "Micro-feedback quotidien (5 min) : 1 fait + 1 action + 1 objectif",
            "Proof: 2 écoutes + score + note de coaching",
        ],
        "cadence": "Daily 5 min + 2 checkpoints (J+2, J+5).",
    },
    "Management directif (S1)": {
        "when": "Si l’agent est junior ou en dérive forte : besoin d’instructions claires.",
        "rituals": [
            "Brief 10 min : règles non négociables + script + timing",
            "Check-list de traitement (étapes fixes) affichée",
            "Contrôle 1 appel/jour + correction immédiate",
        ],
        "cadence": "Daily + contrôle systématique 5 jours.",
    },
    "Situational Leadership (S2/S3)": {
        "when": "Si l’agent sait faire mais n’est pas régulier (motivation/rigueur).",
        "rituals": [
            "S2 (coach) : expliquer + faire pratiquer + feedback",
            "S3 (support) : laisser faire + enlever les blocages",
            "Points de suivi : J+3 puis S2",
        ],
        "cadence": "2 à 3 points/semaine + 1 shadow.",
    },
    "Routine de pilotage (Management by numbers)": {
        "when": "Si le problème est surtout de discipline de process / suivi KPI.",
        "rituals": [
            "Objectif chiffré + trajectoire (ex: DMT 220→190→170→158)",
            "Daily KPI check (2 min) + action corrective immédiate",
            "Tableau de bord TL : 1 KPI driver + 1 KPI garde-fou (Qualité)",
        ],
        "cadence": "Daily tracking + revue hebdo.",
    },
}

# ------------------------------------------------------------
# KPI playbooks (Intelcia / call center)
# ------------------------------------------------------------
PLAYBOOK = {
    "DMT (sec)": {
        "theme": "DMT",
        "root_causes": [
            "Manque d’écoute active (mauvaise qualification → rework)",
            "Manque de directivité (l’appel s’étire)",
            "Manque de concentration / prise de notes inefficace",
            "Complexité demandes / knowledge peu maîtrisée",
            "Manque d’autonomie (sollicitation excessive)",
            "After-call (ACW) trop long / non standardisé",
            "Mise en attente excessive (recherche, validation tardive)",
        ],
        "actions_bank": [
            "Débrief 1:1 basé sur 2 écoutes (faits → causes → actions)",
            "Rappel méthode : qualification courte + questions fermées + reformulation",
            "Template notes ACW (standard) + objectif ACW",
            "Challenge : réduire le temps moyen par palier (trajectoire)",
            "Suivi quotidien fin de shift (2 minutes) + correction immédiate",
        ],
        "default_owners": ["TL", "CQ", "FORMATEURS"],
        "guardrail": "Qualité (%)",
    },
    "Qualité (%)": {
        "theme": "Qualité",
        "root_causes": [
            "Non-respect script / étapes obligatoires",
            "Erreurs KO récurrentes (vérifs manquantes / mauvaise info)",
            "Connaissance produit/process insuffisante",
            "Vitesse qui dégrade la conformité (pression DMT)",
        ],
        "actions_bank": [
            "Calibration qualité + rappel KO (exemples concrets)",
            "Coaching sur 3 erreurs récurrentes (preuves à l’appui)",
            "Simulation 10 min/jour sur cas KO",
            "Shadowing 1 session avec top performer",
            "Validation : 2 écoutes de contrôle (objectif : 0 KO)",
        ],
        "default_owners": ["TL", "CQ", "FORMATEURS"],
        "guardrail": "DMT (sec)",
    },
    "Prod": {
        "theme": "Productivité",
        "root_causes": [
            "Rythme faible / organisation",
            "Maîtrise outil/process insuffisante",
            "Trop de temps sur cas non standard",
            "Dépendance forte (aide fréquente)",
        ],
        "actions_bank": [
            "Identifier 2 tâches répétitives → standardiser (phrases type / templates)",
            "Mini-objectifs journaliers + suivi TL",
            "Accompagnement live 30 min (priorités + méthode)",
            "Shadowing avec agent performant",
            "Check garde-fou : Qualité stable",
        ],
        "default_owners": ["TL", "FORMATEURS", "OPS"],
        "guardrail": "Qualité (%)",
    },
    "ABS (%)": {
        "theme": "Absentéisme",
        "root_causes": [
            "Problèmes personnels/transport",
            "Démotivation / climat",
            "Problème planning / fatigue",
            "Non-respect règles",
        ],
        "actions_bank": [
            "Entretien TL : cause + engagement + plan concret",
            "Ajustement planning si possible / plan transport",
            "Point de présence (pré-shift) si nécessaire",
            "Escalade RH si répétition selon procédure",
        ],
        "default_owners": ["TL", "OPS", "RH"],
        "guardrail": None,
    },
    "TH prod (€)": {
        "theme": "TH Prod",
        "root_causes": [
            "Levier Prod insuffisant",
            "Qualité génère retours/rework",
            "DMT trop long",
        ],
        "actions_bank": [
            "Choisir 1 levier prioritaire (Prod ou Qualité ou DMT) — pas 3",
            "Appliquer le playbook du levier prioritaire",
            "Contrôle résultat S2 : levier + TH prod",
        ],
        "default_owners": ["TL", "OPS"],
        "guardrail": "Qualité (%)",
    },
}


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _fmt_value(kpi: str, v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "-"
    try:
        x = float(v)
        if "sec" in kpi.lower() or "dmt" in kpi.lower():
            return f"{x:.0f} sec"
        if "%" in kpi:
            return f"{x:.2f}%"
        if "€" in kpi or "eur" in kpi.lower():
            return f"{x:.2f} €"
        return f"{x:.2f}"
    except Exception:
        return str(v)


def _kpi_type(row: pd.Series, kpi: str) -> str:
    return str(row.get(f"Type_{kpi}", "")).lower().strip()


def _is_bad(ecart: float, t: str) -> bool:
    # Interprétation cohérente avec ton calcul :
    # - min : ecart > 0 => mauvais (val > obj)
    # - max : ecart < 0 => mauvais (val < obj)
    # - target : |écart| > 3% => à traiter
    if t == "min":
        return ecart > 0
    if t == "max":
        return ecart < 0
    return abs(ecart) > 0.03


def _select_driver(row: pd.Series, kpis: list[str]):
    bads = []
    for k in kpis:
        e = float(row.get(f"Ecart_{k}", 0))
        t = _kpi_type(row, k)
        if _is_bad(e, t):
            bads.append((k, e, t))
    if not bads:
        return None, []
    # driver = plus gros écart en magnitude
    driver = max(bads, key=lambda x: abs(x[1]))
    return driver, sorted(bads, key=lambda x: abs(x[1]), reverse=True)


def _trajectory(val, obj, days=10, steps=3):
    """
    Trajectoire simple en paliers (utile pour TL).
    Exemple DMT 220 -> 158 en 10j: palier1, palier2, target
    """
    try:
        v = float(val)
        o = float(obj)
        if v == o:
            return [o]
        # 3 paliers (Semaine 1)
        p1 = v + (o - v) * (1 / steps)
        p2 = v + (o - v) * (2 / steps)
        return [round(p1, 1), round(p2, 1), round(o, 1)]
    except Exception:
        return []


def _timeline_dates(start: date):
    # call center: J0, J+2, J+5, J+10 (typique)
    return {
        "J0": start,
        "J+2": start + timedelta(days=2),
        "J+5": start + timedelta(days=5),
        "J+10": start + timedelta(days=10),
    }


def _pda_card_css():
    st.markdown(
        """
<style>
.pda-grid{
  display:grid;
  grid-template-columns: 1.0fr 2.2fr 2.2fr 1.0fr;
  gap:14px;
}
.pda-col{
  background: rgba(255,255,255,.08);
  border: 1px solid rgba(255,255,255,.16);
  border-radius: 18px;
  padding: 14px 14px;
  min-height: 260px;
}
.pda-head{
  font-weight: 900;
  letter-spacing: .08em;
  text-transform: uppercase;
  font-size: .75rem;
  color: rgba(255,255,255,.92);
  margin-bottom: 10px;
}
.pda-pill{
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.18);
  background: rgba(255,255,255,.10);
  font-weight: 850;
}
.pda-kpi{
  margin-top:10px;
  font-size: .95rem;
  color: rgba(255,255,255,.88);
  line-height: 1.4;
}
.pda-ul{
  margin: 0;
  padding-left: 18px;
  color: rgba(255,255,255,.88);
  line-height: 1.55;
}
.pda-ul li{ margin-bottom: 6px; }
.pda-owner{
  font-weight: 900;
  margin-bottom: 10px;
}
.pda-small{
  color: rgba(255,255,255,.70);
  font-size: .85rem;
}
.pda-mgmt{
  background: rgba(255,255,255,.07);
  border: 1px solid rgba(255,255,255,.14);
  border-radius: 18px;
  padding: 14px 14px;
}
</style>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# Main generator
# ------------------------------------------------------------
def generer_pda(df_ecarts: pd.DataFrame, params: dict):
    st.subheader("🧩 PDA TL — Intelcia (chiffré + actions + timeline + management)")

    if df_ecarts is None or df_ecarts.empty:
        st.warning("Aucune donnée KPI disponible.")
        return

    _pda_card_css()

    # Scope
    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        agent = st.selectbox("Agent", sorted(df_ecarts["Agent"].unique()))
    with c2:
        mois_ref = st.selectbox("Mois de référence", sorted(df_ecarts["Mois"].unique()))
    with c3:
        start = st.date_input("Démarrage PDA", value=date.today())

    df_sel = df_ecarts[(df_ecarts["Agent"] == agent) & (df_ecarts["Mois"] == mois_ref)]
    if df_sel.empty:
        st.warning("Aucune donnée pour cet Agent/Mois.")
        return

    row = df_sel.iloc[0]
    kpis = params["kpi"]

    driver, bads = _select_driver(row, kpis)
    if driver is None:
        st.success("Aucune dérive significative : PDA non requis.")
        return

    driver_kpi, driver_ecart, driver_type = driver

    # Owners
    owners_default = PLAYBOOK.get(driver_kpi, {}).get("default_owners", ["TL"])
    owner = st.multiselect("Owners (responsables)", options=["TL", "CQ", "FORMATEURS", "OPS", "RH"], default=[o for o in owners_default if o in ["TL", "CQ", "FORMATEURS", "OPS", "RH"]])

    # Management style
    mgmt_style = st.selectbox("Type de management à appliquer", list(MANAGEMENT_MODES.keys()), index=0)
    mgmt = MANAGEMENT_MODES[mgmt_style]

    # Values & objective
    val = row.get(f"Val_{driver_kpi}", None)
    obj = row.get(f"Obj_{driver_kpi}", None)
    val_txt = _fmt_value(driver_kpi, val)
    obj_txt = _fmt_value(driver_kpi, obj)
    ecart_pct = round(float(driver_ecart) * 100, 2)

    # Delta + trajectory
    delta_txt = ""
    traj_txt = ""
    traj = []
    try:
        if val is not None and obj not in (None, 0, "-"):
            dv = float(val) - float(obj)
            if driver_type == "min":
                delta_txt = f"Δ = +{_fmt_value(driver_kpi, abs(dv))} au-dessus de l’objectif"
            elif driver_type == "max":
                delta_txt = f"Δ = -{_fmt_value(driver_kpi, abs(dv))} sous l’objectif"
            else:
                delta_txt = f"Δ = {_fmt_value(driver_kpi, dv)} vs cible"

            traj = _trajectory(val, obj, days=10, steps=3)
            if traj:
                # e.g. 220 → 190 → 170 → 158
                if "sec" in driver_kpi.lower() or "dmt" in driver_kpi.lower():
                    traj_txt = " → ".join([f"{x:.0f}s" for x in traj])
                else:
                    traj_txt = " → ".join([str(x) for x in traj])
    except Exception:
        pass

    # Build content
    play = PLAYBOOK.get(driver_kpi, None)
    theme = play["theme"] if play else driver_kpi
    causes = play["root_causes"] if play else ["Cause à qualifier (process / outil / connaissance / comportement)."]
    actions_bank = play["actions_bank"] if play else ["Diagnostic J0 → Coaching J1 → Checkpoint J+5 → Ajustement."]

    # Timeline datée (simple, TL friendly)
    tl_dates = _timeline_dates(start)
    # action lines with dates
    action_lines = [
        f"({tl_dates['J0'].isoformat()}) Diagnostic sur 5 interactions + identification du goulot (ACW / hold / qualification)",
        f"({tl_dates['J+2'].isoformat()}) Coaching ciblé + 2 écoutes + plan correctif écrit",
        f"({tl_dates['J+5'].isoformat()}) Checkpoint #1 : mesure KPI + correction immédiate",
        f"({tl_dates['J+10'].isoformat()}) Checkpoint #2 : validation trajectoire + décision (maintenir / escalader)",
    ]

    # Add KPI-specific actions (max 3) in addition
    for a in actions_bank[:3]:
        action_lines.insert(1, f"- {a}")

    # Guardrail KPI
    guard = play.get("guardrail") if play else None
    guard_line = ""
    if guard and f"Val_{guard}" in row and f"Obj_{guard}" in row:
        guard_line = f"Garde-fou: {guard} (réel {_fmt_value(guard, row.get(f'Val_{guard}'))} vs obj {_fmt_value(guard, row.get(f'Obj_{guard}'))}) — ne pas sacrifier ce KPI."

    # ------------------------------------------------------------
    # Render: 4 columns like your template
    # ------------------------------------------------------------
    st.markdown(f"### 🎯 {APP_BRAND_LINE}")
    st.markdown(f"**Agent**: `{agent}` • **Période**: `{mois_ref}` • **Driver**: **{driver_kpi}** (`{ecart_pct}%`)")

    kpi_block = f"""
<span class="pda-pill">{theme}</span>
<div class="pda-kpi">
<b>Réel</b>: {val_txt}<br/>
<b>Objectif</b>: {obj_txt}<br/>
<b>Écart</b>: {ecart_pct}%<br/>
<b>{delta_txt}</b><br/>
{f"<span class='pda-small'><b>Trajectoire (10j):</b> {traj_txt}</span>" if traj_txt else ""}
</div>
    """

    causes_html = "<ul class='pda-ul'>" + "".join([f"<li>{c}</li>" for c in causes]) + "</ul>"

    actions_html = "<ul class='pda-ul'>" + "".join([f"<li>{x}</li>" for x in action_lines]) + "</ul>"
    if guard_line:
        actions_html += f"<div class='pda-small' style='margin-top:10px;'>⚠️ {guard_line}</div>"

    owners_html = "<div class='pda-owner'>" + "<br/>".join(owner) + "</div>"
    owners_html += "<div class='pda-small'>Rôles:<br/>TL=pilotage<br/>CQ=qualité<br/>Formateurs=montée compétence<br/>OPS=organisation</div>"

    st.markdown(
        f"""
<div class="pda-grid">
  <div class="pda-col">
    <div class="pda-head">Theme</div>
    {kpi_block}
  </div>
  <div class="pda-col">
    <div class="pda-head">Causes racines</div>
    {causes_html}
  </div>
  <div class="pda-col">
    <div class="pda-head">Action</div>
    {actions_html}
  </div>
  <div class="pda-col">
    <div class="pda-head">Owner</div>
    {owners_html}
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------
    # Management block (the "how")
    # ------------------------------------------------------------
    st.write("")
    st.markdown("#### 🧭 Management à suivre (call center)")
    st.markdown(
        f"""
<div class="pda-mgmt">
  <b>Style :</b> {mgmt_style}<br/>
  <b>Quand l’utiliser :</b> {mgmt["when"]}<br/>
  <b>Cadence :</b> {mgmt["cadence"]}<br/><br/>
  <b>Rituels :</b>
  <ul class="pda-ul">
    {''.join([f"<li>{r}</li>" for r in mgmt["rituals"]])}
  </ul>
</div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------
    # Copy-paste block (Teams/Mail)
    # ------------------------------------------------------------
    st.write("")
    st.markdown("#### 📌 PDA prêt à copier (Teams / Mail)")
    text = []
    text.append(APP_BRAND_LINE)
    text.append(f"PDA TL — Agent: {agent} | Période: {mois_ref}")
    text.append(f"Driver: {driver_kpi} | Réel: {val_txt} | Obj: {obj_txt} | Écart: {ecart_pct}% | {delta_txt}".strip())
    if traj_txt:
        text.append(f"Trajectoire 10j: {traj_txt}")
    text.append(f"Owners: {', '.join(owner) if owner else 'TL'}")
    text.append("Causes racines (à vérifier):")
    for c in causes[:6]:
        text.append(f"- {c}")
    text.append("Actions (timeline):")
    for a in action_lines[:10]:
        text.append(f"- {a}")
    if guard_line:
        text.append(f"⚠️ {guard_line}")
    text.append("Management:")
    text.append(f"- Style: {mgmt_style}")
    text.append(f"- Cadence: {mgmt['cadence']}")
    for r in mgmt["rituals"]:
        text.append(f"  - {r}")

    st.code("\n".join(text), language="text")
