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
from modules.pda_generator import generer_pda


# ============================================================
# 🏷️ Branding
# ============================================================
APP_NAME = "PerformTrack 360"
APP_TAGLINE = "TL Command Center"
APP_CLIENT = "Intelcia"
APP_FULL_TITLE = f"{APP_NAME} | {APP_TAGLINE} — {APP_CLIENT}"
APP_PAGE_TITLE = APP_FULL_TITLE
APP_FOOTER = "Developed by Yassine Mahamid"


# ============================================================
# 🎨 Intelcia Logo Colors (clear/vivid, no extra)
# ============================================================
def inject_global_style():
    st.markdown(
        """
<style>
:root{
  /* Intelcia logo-like stops (bright) */
  --c1: #F6D086;   /* light yellow/peach */
  --c2: #F7A46D;   /* orange */
  --c3: #F36A7E;   /* coral pink */
  --c4: #E93C86;   /* intelcia pink */
  --c5: #C94AAE;   /* magenta */

  /* UI neutrals (dark text, light surfaces) */
  --text: rgba(17,24,39,.96);     /* slate-900 */
  --muted: rgba(17,24,39,.70);
  --muted2: rgba(17,24,39,.55);

  --surface: rgba(255,255,255,.72);
  --surface2: rgba(255,255,255,.82);
  --stroke: rgba(17,24,39,.14);

  --btn: #E93C86;
  --btn_hover: #D92F78;
}

/* ✅ Bright background like Intelcia image */
.stApp{
  background:
    radial-gradient(1200px 700px at 18% 12%, rgba(246,208,134,1) 0%, rgba(246,208,134,0) 62%),
    radial-gradient(1200px 700px at 45% 22%, rgba(247,164,109,0.95) 0%, rgba(247,164,109,0) 62%),
    radial-gradient(1200px 700px at 55% 60%, rgba(243,106,126,0.85) 0%, rgba(243,106,126,0) 60%),
    radial-gradient(1200px 700px at 30% 88%, rgba(233,60,134,0.95) 0%, rgba(233,60,134,0) 60%),
    radial-gradient(1200px 700px at 78% 88%, rgba(201,74,174,0.55) 0%, rgba(201,74,174,0) 62%),
    linear-gradient(135deg, var(--c1) 0%, var(--c2) 28%, var(--c4) 68%, var(--c5) 100%);
  color: var(--text);
}

/* ✅ keep sidebar toggle available */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Typography */
html, body, [class*="css"]{ color: var(--text); }
h1,h2,h3,h4{ color: var(--text); letter-spacing:.2px; }
small{ color: var(--muted2); }

/* Sidebar (light & readable) */
section[data-testid="stSidebar"]{
  background: rgba(255,255,255,.70);
  border-right: 1px solid var(--stroke);
}
section[data-testid="stSidebar"] *{
  color: var(--text) !important;
}

/* Hero (uses same logo gradient, but readable) */
.hero{
  border-radius: 22px;
  padding: 20px 22px;
  border: 1px solid var(--stroke);
  background: linear-gradient(135deg, rgba(246,208,134,.80), rgba(247,164,109,.75), rgba(233,60,134,.70), rgba(201,74,174,.55));
  box-shadow: 0 18px 55px rgba(0,0,0,.18);
}
.hero .kicker{
  font-size: .78rem;
  color: rgba(17,24,39,.70);
  letter-spacing: .14em;
  text-transform: uppercase;
  margin: 0 0 8px 0;
}
.hero .h-title{
  font-size: 1.65rem;
  font-weight: 950;
  margin: 0;
  color: rgba(17,24,39,.96);
}
.hero .h-sub{
  margin: 6px 0 0 0;
  color: rgba(17,24,39,.72);
  font-size: 1.02rem;
}
.hero .pill{
  display: inline-block;
  margin-top: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(17,24,39,.14);
  background: rgba(255,255,255,.55);
  font-size: .82rem;
  color: rgba(17,24,39,.82);
}

/* Cards */
.card{
  background: var(--surface);
  border: 1px solid var(--stroke);
  border-radius: 18px;
  padding: 16px 16px;
  box-shadow: 0 12px 35px rgba(0,0,0,.12);
}
.card .title{ font-weight: 800; font-size: .92rem; color: var(--muted); }
.card .value{ font-weight: 950; font-size: 1.60rem; margin-top: 2px; color: var(--text); }
.card .hint{ font-size: .86rem; color: var(--muted2); margin-top: 6px; }

/* Tabs */
.stTabs [data-baseweb="tab"]{
  background: rgba(255,255,255,.68);
  border: 1px solid var(--stroke);
  border-radius: 14px;
  padding: 10px 14px;
}
.stTabs [aria-selected="true"]{
  background: linear-gradient(135deg, rgba(233,60,134,.25), rgba(247,164,109,.22), rgba(255,255,255,.70));
  border: 1px solid rgba(233,60,134,.35);
}

/* Buttons (Intelcia pink) */
.stDownloadButton button, .stButton button{
  border-radius: 14px !important;
  border: 1px solid rgba(233,60,134,.55) !important;
  background: var(--btn) !important;
  color: white !important;
  font-weight: 950 !important;
}
.stDownloadButton button:hover, .stButton button:hover{
  background: var(--btn_hover) !important;
}

/* Inputs (light) */
.stTextInput input, .stSelectbox div, .stMultiSelect div{
  background: rgba(255,255,255,.85) !important;
  border: 1px solid var(--stroke) !important;
  color: var(--text) !important;
  border-radius: 12px !important;
}

/* DataFrame + Alerts */
div[data-testid="stDataFrame"]{
  border-radius: 18px;
  border: 1px solid var(--stroke);
  overflow: hidden;
  background: rgba(255,255,255,.75);
}
div[data-testid="stAlert"]{
  border-radius: 16px;
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,.78);
}
div[data-testid="stAlert"] *{ color: var(--text) !important; }

.footer{
  text-align:center;
  color: rgba(17,24,39,.55);
  font-size: .85rem;
  padding: 14px 0 8px 0;
}
hr{ border: none; border-top: 1px solid rgba(17,24,39,.14); }

/* AUTH (same colors, readable, no extra components) */
.auth-shell{
  max-width: 980px;
  margin: 60px auto 0 auto;
  display: grid;
  grid-template-columns: 1.2fr .9fr;
  gap: 18px;
}
.auth-left{
  border-radius: 22px;
  padding: 22px 22px;
  border: 1px solid rgba(17,24,39,.14);
  background: linear-gradient(135deg, rgba(246,208,134,.85), rgba(247,164,109,.78), rgba(233,60,134,.70), rgba(201,74,174,.55));
  box-shadow: 0 18px 55px rgba(0,0,0,.16);
}
.auth-right{
  border-radius: 22px;
  padding: 18px 18px;
  background: rgba(255,255,255,.90);
  color: var(--text);
  border: 1px solid rgba(17,24,39,.14);
  box-shadow: 0 18px 55px rgba(0,0,0,.14);
}
.auth-right .stTextInput input{
  background: rgba(255,255,255,.95) !important;
  border: 1px solid rgba(17,24,39,.18) !important;
  color: rgba(17,24,39,.96) !important;
}
.auth-right .stButton button{
  width: 100%;
  background: var(--btn) !important;
  border: 1px solid rgba(233,60,134,.65) !important;
}
.auth-right .stButton button:hover{
  background: var(--btn_hover) !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 🔐 Auth
# ============================================================
def login():
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if st.session_state.auth:
        return

    st.set_page_config(page_title=APP_PAGE_TITLE, page_icon="📊", layout="wide")
    inject_global_style()

    st.markdown(
        f"""
<div class="auth-shell">
  <div class="auth-left">
    <p style="margin:0 0 10px 0; letter-spacing:.14em; text-transform:uppercase; color:rgba(17,24,39,.75); font-size:.78rem;">
      {APP_NAME} — {APP_CLIENT}
    </p>
    <p style="margin:0; font-size:1.65rem; font-weight:950; color:rgba(17,24,39,.96);">
      📊 {APP_TAGLINE}
    </p>
    <p style="margin:8px 0 0 0; color:rgba(17,24,39,.72); font-size:1.02rem;">
      Pilotage KPI d’appels • Synthèse • PDA TL chiffré + timeline
    </p>
  </div>

  <div class="auth-right">
    <div style="font-weight:950;font-size:1.05rem;margin-bottom:4px;">Connexion</div>
    <div style="color:rgba(17,24,39,.62);font-size:.90rem;margin-bottom:12px;">
      Accès réservé — identifiants requis
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    colA, colB = st.columns([1.2, 0.9])
    with colB:
        with st.form("login_form", clear_on_submit=False):
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

    st.markdown(f"<div class='footer'>{APP_FOOTER}</div>", unsafe_allow_html=True)
    st.stop()


# ============================================================
# Helpers
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
# Main
# ============================================================
login()

st.set_page_config(page_title=APP_PAGE_TITLE, page_icon="📊", layout="wide")
inject_global_style()

st.markdown(
    f"""
<div class="hero">
  <p class="kicker">{APP_NAME} — {APP_CLIENT}</p>
  <p class="h-title">📊 {APP_TAGLINE}</p>
  <p class="h-sub">Analyse par objectifs • Visualisations • Synthèse • Génération PDA</p>
  <span class="pill">Version interne • KPI & RH</span>
</div>
""",
    unsafe_allow_html=True,
)
st.write("")

with st.sidebar:
    st.markdown("### 🧭 Workflow")
    st.caption("1) Importer les 2 fichiers\n\n2) Régler KPI + pondérations\n\n3) Explorer KPI / Agent / Synthèse\n\n4) Générer un PDA")
    st.divider()
    if st.button("🚪 Se déconnecter"):
        st.session_state.auth = False
        st.rerun()

df_resultats, df_objectifs = uploader_fichier()

if df_resultats is None or df_objectifs is None:
    st.info("Importe les deux fichiers depuis la sidebar (ou le bloc d'import dans la page) pour démarrer.")
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
        st.session_state["agent_for_word"] = agent
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
        st.markdown("#### 🧩 PDA — plan TL actionnable")
        st.caption("PDA chiffré + owners + timeline + management (centre d’appels Intelcia).")
        generer_pda(df_ecarts, params)

    st.write("")
    st.divider()

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

st.markdown(f"<hr/><div class='footer'>{APP_FOOTER}</div>", unsafe_allow_html=True)
