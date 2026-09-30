import streamlit as st
import plotly.io as pio

st.set_page_config(page_title="WorkforceAI", page_icon="◈", layout="wide")
pio.templates.default = "plotly_dark"

st.markdown("""
<style>
:root {
  color-scheme: dark;
  --canvas: #0b0f14;
  --sidebar: #10161e;
  --surface: #141c25;
  --surface-raised: #19232e;
  --line: #293542;
  --line-strong: #3b4b5c;
  --accent: #6fc6b3;
  --accent-hover: #8ad8c7;
  --text: #e8edf2;
  --muted: #9ba9b7;
  --success: #71c6a2;
  --warning: #e4bd76;
  --danger: #e58d8d;
}
html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.stApp { background: var(--canvas); color: var(--text); }
[data-testid="stHeader"] { background: rgba(11,15,20,.94); border-bottom: 1px solid rgba(41,53,66,.55); }
[data-testid="stToolbar"] { right: 1rem; }
.block-container { max-width: 1480px; padding: 2.35rem clamp(1.15rem, 3vw, 2.75rem) 3.5rem; }
h1, h2, h3, h4 { color: var(--text); letter-spacing: -.025em; line-height: 1.2; }
h1 { font-size: clamp(1.85rem, 3vw, 2.55rem); font-weight: 680; margin-bottom: .35rem; }
h2 { font-size: 1.35rem; font-weight: 640; margin-top: 1.5rem; }
h3 { font-size: 1.08rem; font-weight: 620; }
p, li, label, [data-testid="stCaptionContainer"] { color: var(--muted); line-height: 1.65; }
a { color: var(--accent); }
a:hover { color: var(--accent-hover); }
hr { border-color: var(--line); }
section[data-testid="stSidebar"] { background: var(--sidebar); border-right: 1px solid var(--line); }
section[data-testid="stSidebar"] > div { padding-top: 1.35rem; }
section[data-testid="stSidebar"] h1 { font-size: 1.25rem; letter-spacing: -.02em; color: var(--text); }
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { font-size: .82rem; }
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .55rem; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { margin-bottom: .35rem; }
[data-testid="stSidebarNav"] { padding-top: .6rem; }
[data-testid="stSidebarNav"] li { border-radius: 8px; margin: 2px 0; }
[data-testid="stSidebarNav"] a { border-radius: 8px; transition: background-color .15s ease, color .15s ease; }
[data-testid="stSidebarNav"] a:hover { background: var(--surface-raised); color: var(--text); }
[data-testid="stSidebarNav"] a[aria-current="page"] { background: #20332f; color: #a0e0d0; }
.wf-badge { display: inline-flex; align-items: center; gap: .4rem; padding: 5px 10px; border: 1px solid #33534f; border-radius: 999px; color: #a0d9cd; background: #172522; font-size: .74rem; font-weight: 650; letter-spacing: .045em; margin: 2px 5px 9px 0; }
.wf-card { height: 100%; background: var(--surface); border: 1px solid var(--line); border-radius: 13px; padding: 21px; min-height: 150px; transition: border-color .16s ease, background-color .16s ease, transform .16s ease; }
.wf-card:hover { background: var(--surface-raised); border-color: #49605f; transform: translateY(-2px); }
.wf-card h3 { margin: 0 0 9px; color: var(--text); }
.wf-card p { margin: 0; font-size: .93rem; }
div[data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 17px 18px; min-height: 112px; transition: border-color .16s ease, background-color .16s ease; }
div[data-testid="stMetric"]:hover { border-color: var(--line-strong); background: var(--surface-raised); }
div[data-testid="stMetricLabel"] { color: var(--muted); font-size: .82rem; }
div[data-testid="stMetricValue"] { color: var(--text); font-size: clamp(1.4rem, 2.3vw, 1.9rem); font-weight: 670; }
div[data-testid="stMetricDelta"] { font-size: .8rem; }
[data-testid="stPlotlyChart"] { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 8px; overflow: hidden; }
[data-testid="stDataFrame"], [data-testid="stTable"] { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
[data-testid="stExpander"] { background: var(--surface); border: 1px solid var(--line); border-radius: 11px; overflow: hidden; }
[data-testid="stExpander"] summary { color: var(--text); font-weight: 570; }
[data-testid="stForm"] { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 1.15rem; }
[data-testid="stTabs"] [role="tablist"] { gap: .45rem; border-bottom: 1px solid var(--line); }
[data-testid="stTabs"] button[role="tab"] { color: var(--muted); border-radius: 8px 8px 0 0; }
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color: var(--accent-hover); border-bottom-color: var(--accent); }
.stButton > button, .stDownloadButton > button, [data-testid="stPageLink"] a { min-height: 2.55rem; border-radius: 8px; border: 1px solid var(--line-strong); background: var(--surface-raised); color: var(--text); font-weight: 590; transition: background-color .15s ease, border-color .15s ease, transform .15s ease; }
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stPageLink"] a:hover { border-color: var(--accent); background: #20332f; color: #d8f4ed; transform: translateY(-1px); }
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible, input:focus-visible, textarea:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.stButton > button[kind="primary"] { background: #28574d; border-color: #39796b; color: #f1fffb; }
.stButton > button[kind="primary"]:hover { background: #326a5e; border-color: var(--accent); }
.stTextInput input, .stTextArea textarea, .stNumberInput input { background: #0e141b; color: var(--text); border: 1px solid var(--line-strong); border-radius: 8px; }
[data-baseweb="select"] > div, [data-baseweb="input"] > div { background: #0e141b; border-color: var(--line-strong); border-radius: 8px; }
[data-baseweb="tag"] { background: #24423b; border-color: #39675d; }
[data-testid="stFileUploader"] section { background: #111a22; border: 1px dashed var(--line-strong); border-radius: 10px; }
[data-testid="stAlert"] { border-radius: 10px; border-width: 1px; }
[data-testid="stStatusWidget"] { border-radius: 9px; }
[data-testid="stSpinner"] { color: var(--accent); }
[data-testid="stProgress"] > div > div { background: var(--accent); }
@media (max-width: 850px) {
  .block-container { padding: 1.5rem 1rem 2.25rem; }
  [data-testid="stPlotlyChart"] { padding: 3px; }
  div[data-testid="stMetric"] { padding: 14px; min-height: 98px; }
}
@media (max-width: 560px) {
  .block-container { padding: 1.1rem .8rem 1.75rem; }
  h1 { font-size: 1.7rem; }
  h2 { font-size: 1.2rem; }
  [data-testid="stHorizontalBlock"] { gap: .65rem; }
  .wf-card { padding: 16px; min-height: auto; }
  [data-testid="stSidebar"] { min-width: 0; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; animation-duration: .01ms !important; }
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("◈ WorkforceAI")
st.sidebar.caption("People analytics · decision support")
st.sidebar.selectbox(
    "Perspective",
    ["HR Manager", "Recruiter", "Interviewer", "Workforce Analyst"],
    key="user_perspective",
    help="Changes the label shown in the sidebar. All decisions remain with authorized humans.",
)
st.sidebar.markdown(
    '<span class="wf-badge">● Evidence mode</span><span class="wf-badge">● Human review</span>',
    unsafe_allow_html=True,
)

page = st.navigation([
    st.Page("pages/0_Home.py", title="WorkforceAI", icon="🏠"),
    st.Page("pages/5_Workforce_Dashboard.py", title="Dashboard", icon="📊"),
    st.Page("pages/1_Recruitment_Intelligence.py", title="Recruitment Intelligence", icon="📄"),
    st.Page("pages/2_Interview_Agent.py", title="Intelligent Interview Agent", icon="💬"),
    st.Page("pages/3_HR_Policy_Assistant.py", title="HR Policy Assistant", icon="📚"),
    st.Page("pages/4_Attrition_Intelligence.py", title="Attrition Intelligence", icon="🔎"),
    st.Page("pages/6_Skill_Graph.py", title="Workforce Skill Graph", icon="🔗"),
    st.Page("pages/7_Model_Performance.py", title="Model Performance", icon="📈"),
    st.Page("pages/8_Project_Information.py", title="Project Information", icon="ℹ️"),
])
page.run()
st.sidebar.divider()
st.sidebar.caption("Human decisions. Traceable evidence. No automated hiring, rejection, promotion or penalties.")
