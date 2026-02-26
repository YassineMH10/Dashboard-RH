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
APP_CLIENT = "Intelcia"
APP_FULL_TITLE = f"{APP_NAME} | {APP_TAGLINE} — {APP_CLIENT}"
APP_PAGE_TITLE = APP_FULL_TITLE
APP_FOOTER = "Developed by Yassine Mahamid"


# ============================================================
# 🎨 Global Style (premium + readable)
# ============================================================
def inject_global_style():
    st.markdown(
        """
<style>
:root{
  /* Background */
  --bg0:#070A12;
  --bg1:#0B1220;

  /* Surfaces */
  --surface: rgba(255,255,255,.08);
  --surface2: rgba(255,255,255,.10);
  --stroke: rgba(255,255,255,.16);

  /* Text */
  --text: rgba(255,255,255,.94);
  --muted: rgba(255,255,255,.78);
  --muted2: rgba(255,255,255,.62);

  /* Accents */
  --accent:#8B5CF6;   /* violet */
  --accent2:#22C55E;  /* green */
  --info:#38BDF8;     /* sky */
  --warn:#FBBF24;     /* amber */
  --danger:#FB7185;   /* rose */
}

/* App background: keep premium but less dark */
.stApp{
  background:
    radial-gradient(1300px 650px at 12% 12%, rgba(139,92,246,.28), transparent 55%),
    radial-gradient(1100px 600px at 88% 18%, rgba(34,197,94,.14), transparent 60%),
    radial-gradient(1000px 800px at 72% 92%, rgba(56,189,248,.12), transparent 65%),
    linear-gradient(180deg, var(--bg0) 0%, var(--bg1) 60%, var(--bg0) 100%);
  color: var(--text);
}

/* Hide Streamlit header */
header { visibility: hidden; }
section[data-testid="stSidebar"] > div { padding-top: 1.0rem; }

/* Sidebar: increase readability */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
  border-right: 1px solid var(--stroke);
}
section[data-testid="stSidebar"] *{
  color: var(--text) !important;
}
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label{
  color: var(--muted) !important;
}

/* Typography */
h1,h2,h3,h4 { letter-spacing: .2px; }
small, .muted { color: var(--muted2); }

/* Hero (top banner) */
.hero{
  border-radius: 22px;
  padding: 20px 22px;
  border: 1px solid var(--stroke);
  background:
    linear-gradient(135deg, rgba(139,92,246,.22), rgba(255,255,255,.06));
  box-shadow: 0 18px 55px rgba(0,0,0,.30);
}
.hero .kicker{
  font-size: .78rem;
  color: var(--muted2);
  letter-spacing: .14em;
  text-transform: uppercase;
  margin: 0 0 8px 0;
}
.hero .h-title{
  font-size: 1.65rem;
  font-weight: 900;
  margin: 0;
}
.hero .h-sub{
  margin: 6px 0 0 0;
  color: var(--muted);
  font-size: 1.02rem;
}
.hero .pill{
  display: inline-block;
  margin-top: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,.10);
  font-size: .82rem;
  color: var(--text);
}

/* Cards */
.card{
  background: var(--surface);
  border: 1px solid var(--stroke);
  border-radius: 18px;
  padding: 16px 16px;
  box-shadow: 0 12px 35px rgba(0,0,0,.22);
}
.card .title{ font-weight: 750; font-size: .92rem; color: var(--muted); }
.card .value{ font-weight: 950; font-size: 1.60rem; margin-top: 2px; color: var(--text); }
.card .hint{ font-size: .86rem; color: var(--muted2); margin-top: 6px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"]{ gap: 8px; }
.stTabs [data-baseweb="tab"]{
  background: rgba(255,255,255,.08);
  border: 1px solid var(--stroke);
  border-radius: 14px;
  padding: 10px 14px;
  color: var(--text);
}
.stTabs [aria-selected="true"]{
  background: linear-gradient(135deg, rgba(139,92,246,.22), rgba(255,255,255,.08));
  border: 1px solid rgba(139,92,246,.50);
}

/* Buttons */
.stDownloadButton button, .stButton button{
  border-radius: 14px !important;
  border: 1px solid var(--stroke) !important;
  background: rgba(255,255,255,.10) !important;
  color: var(--text) !important;
  font-weight: 700 !important;
}
.stDownloadButton button:hover, .stButton button:hover{
  border: 1px solid rgba(139,92,246,.70) !important;
  background: rgba(139,92,246,.18) !important;
}

/* Input components */
.stTextInput input, .stSelectbox div, .stMultiSelect div{
  background: rgba(255,255,255,.08) !important;
  border: 1px solid var(--stroke) !important;
  color: var(--text) !important;
  border-radius: 12px !important;
}
.stSlider{
  color: var(--text) !important;
}

/* DataFrame */
div[data-testid="stDataFrame"]{
  border-radius: 18px;
  border: 1px solid var(--stroke);
  overflow: hidden;
}

/* Make Streamlit alert boxes more readable */
div[data-testid="stAlert"]{
  border-radius: 16px;
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,.08);
}
div[data-testid="stAlert"] *{
  color: var(--text) !important;
}

/* Footer */
.footer{
  text-align:center;
  color: var(--muted2);
  font-size: .85rem;
  padding: 14px 0 8px 0;
}
hr{ border: none; border-top: 1px solid var(--stroke); }

/* Small helper badges */
.badge{
  display:inline-block;
  padding:6px 10px;
  border-radius:999px;
  border:1px solid var(--stroke);
  background: rgba(255,255,255,.10);
  color: var(--text);
  font-size:.82rem;
}
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

    st.set_page_config(page_title=APP_PAGE_TITLE, page_icon="📊", layout="wide")
    inject_global_style()

    colL, colC, colR = st.columns([1.15, 1.50, 1.15])
    with colC:
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

# Sidebar
with st.sidebar:
    st.markdown("### 🧭 Workflow")
    st.markdown(
        """
<span class="badge">1</span> Importer les 2 fichiers<br>
<span class="badge">2</span> Régler KPI + pondérations<br>
<span class="badge">3</span> Explorer KPI / Agent / Synthèse<br>
<span class="badge">4</span> Générer un PDA
        """,
        unsafe_allow_html=True,
    )
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

st.markdown(f"<hr/><div class='footer'>{APP_FOOTER}</div>", unsafe_allow_html=True)
