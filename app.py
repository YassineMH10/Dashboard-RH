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
# 🎨 Intelcia Pink Theme (high-contrast, readable)
# ============================================================
def inject_global_style():
    st.markdown(
        """
<style>
:root{
  /* Intelcia Pink accents (approx from logo) */
  --pink:#EC4899;        /* primary */
  --pink2:#F472B6;       /* hover */
  --orange:#FB923C;      /* warm highlight */
  --violet:#A78BFA;      /* subtle secondary */

  /* Background */
  --bg0:#070A14;
  --bg1:#0B1220;

  /* Surfaces */
  --surface: rgba(255,255,255,.10);
  --surface2: rgba(255,255,255,.14);
  --stroke: rgba(255,255,255,.18);

  /* Text */
  --text: rgba(255,255,255,.95);
  --muted: rgba(255,255,255,.80);
  --muted2: rgba(255,255,255,.65);

  /* Auth paper (very readable) */
  --paper: rgba(255,255,255,.96);
  --paperText: rgba(15,23,42,.95);
  --paperMuted: rgba(15,23,42,.62);
  --paperStroke: rgba(15,23,42,.14);
}

/* App background: pink/orange gradient like logo, but still dark for contrast */
.stApp{
  background:
    radial-gradient(1200px 650px at 18% 12%, rgba(236,72,153,.26), transparent 58%),
    radial-gradient(1000px 650px at 72% 18%, rgba(251,146,60,.18), transparent 62%),
    radial-gradient(900px 650px at 85% 88%, rgba(167,139,250,.10), transparent 60%),
    linear-gradient(180deg, var(--bg0) 0%, var(--bg1) 55%, var(--bg0) 100%);
  color: var(--text);
}

/* Hide Streamlit header */
header { visibility: hidden; }
section[data-testid="stSidebar"] > div { padding-top: 1.0rem; }

/* Sidebar (readable) */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(255,255,255,.07), rgba(255,255,255,.03));
  border-right: 1px solid var(--stroke);
}
section[data-testid="stSidebar"] *{ color: var(--text) !important; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] label{
  color: var(--muted) !important;
}

/* Hero (top banner) */
.hero{
  border-radius: 22px;
  padding: 20px 22px;
  border: 1px solid var(--stroke);
  background: linear-gradient(135deg, rgba(236,72,153,.22), rgba(251,146,60,.10), rgba(255,255,255,.06));
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
  font-weight: 950;
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

/* KPI cards */
.card{
  background: var(--surface);
  border: 1px solid var(--stroke);
  border-radius: 18px;
  padding: 16px 16px;
  box-shadow: 0 12px 35px rgba(0,0,0,.22);
}
.card .title{ font-weight: 800; font-size: .92rem; color: var(--muted); }
.card .value{ font-weight: 950; font-size: 1.60rem; margin-top: 2px; color: var(--text); }
.card .hint{ font-size: .86rem; color: var(--muted2); margin-top: 6px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"]{ gap: 8px; }
.stTabs [data-baseweb="tab"]{
  background: rgba(255,255,255,.09);
  border: 1px solid var(--stroke);
  border-radius: 14px;
  padding: 10px 14px;
}
.stTabs [aria-selected="true"]{
  background: linear-gradient(135deg, rgba(236,72,153,.22), rgba(251,146,60,.12), rgba(255,255,255,.10));
  border: 1px solid rgba(244,114,182,.70);
}

/* Buttons (pink primary) */
.stDownloadButton button, .stButton button{
  border-radius: 14px !important;
  border: 1px solid rgba(244,114,182,.75) !important;
  background: rgba(236,72,153,.22) !important;
  color: var(--text) !important;
  font-weight: 900 !important;
}
.stDownloadButton button:hover, .stButton button:hover{
  border: 1px solid rgba(244,114,182,1) !important;
  background: rgba(236,72,153,.34) !important;
}

/* Inputs (app) */
.stTextInput input, .stSelectbox div, .stMultiSelect div{
  background: rgba(255,255,255,.10) !important;
  border: 1px solid var(--stroke) !important;
  color: var(--text) !important;
  border-radius: 12px !important;
}

/* DataFrame */
div[data-testid="stDataFrame"]{
  border-radius: 18px;
  border: 1px solid var(--stroke);
  overflow: hidden;
}

/* Alerts more readable */
div[data-testid="stAlert"]{
  border-radius: 16px;
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,.10);
}
div[data-testid="stAlert"] *{ color: var(--text) !important; }

/* Footer */
.footer{
  text-align:center;
  color: var(--muted2);
  font-size: .85rem;
  padding: 14px 0 8px 0;
}
hr{ border: none; border-top: 1px solid var(--stroke); }

/* --------------------------------
   AUTH (very readable + pink CTA)
--------------------------------- */
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
  border: 1px solid var(--stroke);
  background: linear-gradient(135deg, rgba(236,72,153,.26), rgba(251,146,60,.14), rgba(255,255,255,.06));
  box-shadow: 0 18px 55px rgba(0,0,0,.28);
}
.auth-right{
  border-radius: 22px;
  padding: 18px 18px;
  background: var(--paper);
  color: var(--paperText);
  border: 1px solid var(--paperStroke);
  box-shadow: 0 18px 55px rgba(0,0,0,.30);
}
.auth-title{
  font-size: 1.65rem;
  font-weight: 950;
  margin: 0;
  color: var(--text);
}
.auth-sub{
  margin: 8px 0 0 0;
  color: var(--muted);
  font-size: 1.02rem;
}
.auth-kicker{
  font-size: .78rem;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--muted2);
  margin: 0 0 10px 0;
}
.auth-chip{
  display:inline-block;
  margin-top: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,.10);
  color: var(--text);
  font-size: .82rem;
}

/* Light inputs on auth card */
.auth-right .stTextInput input{
  background: rgba(255,255,255,.98) !important;
  border: 1px solid rgba(15,23,42,.18) !important;
  color: rgba(15,23,42,.95) !important;
}
.auth-right label, .auth-right p, .auth-right span{
  color: rgba(15,23,42,.80) !important;
}

/* Pink CTA button */
.auth-right .stButton button{
  width: 100%;
  border-radius: 14px !important;
  border: 1px solid rgba(236,72,153,.85) !important;
  background: rgba(236,72,153,.95) !important;
  color: white !important;
  font-weight: 950 !important;
}
.auth-right .stButton button:hover{
  background: rgba(236,72,153,1) !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 🔐 Auth (very readable)
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
    <p class="auth-kicker">{APP_NAME} — {APP_CLIENT}</p>
    <p class="auth-title">📊 {APP_TAGLINE}</p>
    <p class="auth-sub">Pilotage KPI d’appels • Synthèse • PDA TL chiffré + timeline</p>
    <span class="auth-chip">Version interne • KPI & RH</span>
    <div style="margin-top:16px;color:rgba(255,255,255,.80);line-height:1.55;">
      <b>Usage TL (centre d’appels) :</b><br/>
      • Importer KPI + objectifs<br/>
      • Identifier le KPI driver<br/>
      • Générer un PDA actionnable (owners + checkpoints + style management)<br/>
      • Exporter Excel/Word
    </div>
  </div>

  <div class="auth-right">
    <div style="font-weight:950;font-size:1.05rem;margin-bottom:4px;">Connexion</div>
    <div style="color:rgba(15,23,42,.62);font-size:.90rem;margin-bottom:12px;">
      Accès réservé — identifiants requis
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    # Layout that aligns with auth-shell proportions
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

with st.sidebar:
    st.markdown("### 🧭 Workflow")
    st.caption("1) Importer les 2 fichiers\n\n2) Régler KPI + pondérations\n\n3) Explorer KPI / Agent / Synthèse\n\n4) Générer un PDA")
    st.divider()
    if st.button("🚪 Se déconnecter"):
        st.session_state.auth = False
        st.rerun()

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
        st.markdown("#### 🧩 PDA — plan TL actionnable")
        st.caption("PDA chiffré + owners + timeline + management (centre d’appels).")
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
