# app.py

import streamlit as st

from modules.uploader import uploader_fichier
from modules.settings import config_utilisateur
from modules.preprocessing import calcul_ecarts_objectifs
from modules.visualisations import (
    afficher_treemaps_par_kpi,
    afficher_radar_agent,
    afficher_courbe_evolution,
    afficher_tableau_detail,
)
from modules.analytics import afficher_synthese_analytique
from modules.exports import export_excel
from modules.synthese_rh import generer_rapport_rh

# ✅ PDA generator (only generates, no storage)
from modules.pda_generator import generer_pda


# ============================================================
# 🏷️ Branding
# ============================================================
APP_NAME = "PerformTrack 360"
APP_TAGLINE = "TL Command Center"
APP_FULL_TITLE = f"{APP_NAME} | {APP_TAGLINE}"
APP_PAGE_TITLE = APP_FULL_TITLE  # used in browser tab
APP_FOOTER = "Developed by Yassine Mahamid"


# ============================================================
# 🎨 Global Style (pro, coherent, clean)
# ============================================================
def inject_global_style():
    st.markdown(
        """
<style>
:root{
  --bg1:#050814;
  --bg2:#0b1220;
  --card: rgba(255,255,255,.06);
  --stroke: rgba(255,255,255,.12);
  --text: rgba(255,255,255,.92);
  --muted: rgba(255,255,255,.72);
  --muted2: rgba(255,255,255,.56);
  --accent:#7c3aed;
  --accent2:#22c55e;
}

/* App background */
.stApp{
  background:
    radial-gradient(1200px 600px at 12% 10%, rgba(124,58,237,.30), transparent 55%),
    radial-gradient(1000px 500px at 88% 18%, rgba(34,197,94,.16), transparent 60%),
    radial-gradient(900px 700px at 70% 90%, rgba(59,130,246,.12), transparent 65%),
    linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 60%, var(--bg1) 100%);
  color: var(--text);
}

/* Hide Streamlit header */
header { visibility: hidden; }
section[data-testid="stSidebar"] > div { padding-top: 1.0rem; }

/* Sidebar */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
  border-right: 1px solid var(--stroke);
}

/* Typography */
h1,h2,h3,h4 { letter-spacing: .2px; }
small, .muted { color: var(--muted2); }

/* Hero */
.hero{
  border-radius: 22px;
  padding: 20px 22px;
  border: 1px solid var(--stroke);
  background: linear-gradient(135deg, rgba(124,58,237,.22), rgba(255,255,255,.04));
  box-shadow: 0 14px 40px rgba(0,0,0,.25);
}
.hero .kicker{
  font-size: .78rem;
  color: var(--muted2);
  letter-spacing: .14em;
  text-transform: uppercase;
  margin: 0 0 8px 0;
}
.hero .h-title{
  font-size: 1.55rem;
  font-weight: 850;
  margin: 0;
}
.hero .h-sub{
  margin: 6px 0 0 0;
  color: var(--muted);
  font-size: .98rem;
}
.hero .pill{
  display: inline-block;
  margin-top: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,.06);
  font-size: .82rem;
  color: var(--muted);
}

/* Cards */
.card{
  background: rgba(255,255,255,.06);
  border: 1px solid var(--stroke);
  border-radius: 18px;
  padding: 16px 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,.20);
}
.card .title{ font-weight: 700; font-size: .92rem; color: var(--muted); }
.card .value{ font-weight: 900; font-size: 1.55rem; margin-top: 2px; }
.card .hint{ font-size: .84rem; color: var(--muted2); margin-top: 6px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"]{ gap: 6px; }
.stTabs [data-baseweb="tab"]{
  background: rgba(255,255,255,.05);
  border: 1px solid var(--stroke);
  border-radius: 14px;
  padding: 10px 14px;
}
.stTabs [aria-selected="true"]{
  background: linear-gradient(135deg, rgba(124,58,237,.18), rgba(255,255,255,.06));
  border: 1px solid rgba(124,58,237,.35);
}

/* Buttons */
.stDownloadButton button, .stButton button{
  border-radius: 14px !important;
  border: 1px solid var(--stroke) !important;
  background: rgba(255,255,255,.06) !important;
}
.stDownloadButton button:hover, .stButton button:hover{
  border: 1px solid rgba(124,58,237,.45) !important;
  background: rgba(124,58,237,.12) !important;
}

/* DataFrame */
div[data-testid="stDataFrame"]{
  border-radius: 18px;
  border: 1px solid var(--stroke);
  overflow: hidden;
}

.footer{
  text-align:center;
  color: var(--muted2);
  font-size: .85rem;
  padding: 14px 0 8px 0;
}
hr{ border: none; border-top: 1px solid var(--stroke); }
</style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 🔐 Auth (clean)
# ============================================================
def login():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if st.session_state.auth:
        return

    # page config + theme before rendering login
    st.set_page_config(page_title=APP_PAGE_TITLE, page_icon="📊", layout="wide")
    inject_global_style()

    colL, colC, colR = st.columns([1.2, 1.4, 1.2])
    with colC:
        st.markdown(
            f"""
<div class="hero">
  <p class="kicker">{APP_NAME}</p>
  <p class="h-title">📊 {APP_TAGLINE}</p>
  <p class="h-sub">Pilotage KPI • Analyse • PDA généré (TL)</p>
  <span class="pill">Internal use • Secure access</span>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")

        with st.form("login_form", clear_on_submit=False):
            st.markdown("#### 🔐 Connexion")
            username = st.text_input("Nom d'utilisateur", placeholder="ex: admin")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Se connecter")

            if submitted:
                if username == "admin" and password == "pass123":
                    st.session_state.auth = True
                    st.success("Connexion réussie.")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")

        st.markdown(f'<div class="footer">{APP_FOOTER}</div>', unsafe_allow_html=True)

    st.stop()


# ============================================================
# 🧠 Helpers
# ============================================================
def kpi_summary_cards(df_ecarts):
    score_moy = round(df_ecarts["Score_Global"].mean() * 100, 2) if "Score_Global" in df_ecarts.columns else 0.0
    agents_total = df_ecarts["Agent"].nunique() if "Agent" in df_ecarts.columns else 0
    mois_total = df_ecarts["Mois"].nunique() if "Mois" in df_ecarts.columns else 0

    best_agent, worst_agent = "-", "-"
    if "Agent" in df_ecarts.columns and "Score_Global" in df_ecarts.columns:
        g = df_ecarts.groupby("Agent")["Score_Global"].mean().sort_values(ascending=False)
        if len(g) > 0:
            best_agent = f"{g.index[0]} ({round(g.iloc[0]*100,2)}%)"
            worst_agent = f"{g.index[-1]} ({round(g.iloc[-1]*100,2)}%)"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
<div class="card">
  <div class="title">Score global moyen</div>
  <div class="value">{score_moy:.2f}%</div>
  <div class="hint">Synthèse pondérée (KPI sélectionnés)</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
<div class="card">
  <div class="title">Agents analysés</div>
  <div class="value">{agents_total}</div>
  <div class="hint">Périmètre actuel</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
<div class="card">
  <div class="title">Mois couverts</div>
  <div class="value">{mois_total}</div>
  <div class="hint">Période incluse</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
<div class="card">
  <div class="title">Best / Worst (Score)</div>
  <div class="value">📈 / 📉</div>
  <div class="hint">{best_agent}<br/>{worst_agent}</div>
</div>
""",
            unsafe_allow_html=True,
        )


# ============================================================
# ✅ Main
# ============================================================
login()

st.set_page_config(page_title=APP_PAGE_TITLE, page_icon="📊", layout="wide")
inject_global_style()

# Hero top
st.markdown(
    f"""
<div class="hero">
  <p class="kicker">{APP_NAME}</p>
  <p class="h-title">📊 {APP_TAGLINE}</p>
  <p class="h-sub">Analyse par objectifs • Visualisations • Synthèse • Génération PDA</p>
  <span class="pill">Version interne • KPI & RH</span>
</div>
""",
    unsafe_allow_html=True,
)
st.write("")

# Sidebar quick ops
with st.sidebar:
    st.markdown("### 🧭 Workflow")
    st.caption("1) Importer les 2 fichiers\n\n2) Régler KPI + pondérations\n\n3) Explorer KPI / Agent / Synthèse\n\n4) Générer un PDA")
    st.divider()
    if st.button("🚪 Se déconnecter"):
        st.session_state.auth = False
        st.rerun()

# Import
df_resultats, df_objectifs = uploader_fichier()

if df_resultats is None or df_objectifs is None:
    st.info("Importe les deux fichiers depuis le menu à gauche pour démarrer.")
else:
    params = config_utilisateur(df_resultats)
    df_ecarts = calcul_ecarts_objectifs(df_resultats, df_objectifs, params)

    kpi_summary_cards(df_ecarts)
    st.write("")

    tab1, tab2, tab3, tab4 = st.tabs(["🌳 KPI", "👤 Agent", "🧠 Synthèse", "🧩 PDA"])

    with tab1:
        st.markdown("#### 🌳 Vue KPI — distribution des écarts")
        st.caption("Taille = magnitude d’écart | Couleur = direction/valeur")
        afficher_treemaps_par_kpi(df_ecarts, params["kpi"])

    with tab2:
        st.markdown("#### 👤 Focus Agent — évolution & détail")
        agent = st.selectbox("Sélectionner un agent", df_ecarts["Agent"].unique())
        st.session_state["agent_for_word"] = agent  # ✅ used by Word export

        afficher_courbe_evolution(df_ecarts, agent, params["kpi"])
        afficher_tableau_detail(df_ecarts, agent, params["kpi"])

        try:
            agent_row = df_ecarts[df_ecarts["Agent"] == agent].iloc[-1]
            afficher_radar_agent(agent_row, params["kpi"])
        except Exception:
            st.warning("Radar indisponible (données insuffisantes).")

    with tab3:
        st.markdown("#### 🧠 Synthèse — lecture RH / TL")
        afficher_synthese_analytique(df_ecarts, params)

    with tab4:
        st.markdown("#### 🧩 PDA — génération automatique (sans suivi)")
        st.caption("PDA prêt à copier/coller (mail, Teams, coaching).")
        generer_pda(df_ecarts, params)

    st.write("")
    st.divider()

    # Exports
    left, right = st.columns([1, 1])
    with left:
        st.download_button(
            "📥 Export Excel",
            data=export_excel(df_ecarts),
            file_name="PerformTrack360_rapport_kpi.xlsx",
            use_container_width=True,
        )

    with right:
        default_agent = df_ecarts["Agent"].unique()[0]
        agent_for_word = st.session_state.get("agent_for_word", default_agent)
        st.download_button(
            "📄 Export Word (Agent)",
            data=generer_rapport_rh(df_ecarts, agent_for_word, params),
            file_name=f"PerformTrack360_rapport_{agent_for_word}.docx",
            use_container_width=True,
        )

# Footer
st.markdown(f"<hr/><div class='footer'>{APP_FOOTER}</div>", unsafe_allow_html=True)
