import streamlit as st
import plotly.io as pio
st.set_page_config(page_title='WorkforceAI',page_icon='◈',layout='wide')
pio.templates.default='plotly_dark'
st.markdown("""
<style>
:root{--navy:#08111F;--panel:#101D31;--line:#263A56;--cyan:#38BDF8;--text:#E6EEF8;--muted:#9DB0C9}
.stApp{background:radial-gradient(circle at 90% 0%,#142B49 0%,var(--navy) 35%);color:var(--text)}
[data-testid="stHeader"]{background:rgba(8,17,31,.86)}
h1,h2,h3{color:var(--text);letter-spacing:-.02em}h4{color:#B9DDF8}
p,li,label,.stCaption{color:var(--muted)}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0B1728 0%,#091321 100%);border-right:1px solid var(--line)}
section[data-testid="stSidebar"] h1{color:var(--cyan)}
div[data-testid="stMetric"]{background:linear-gradient(135deg,#132A46,#101D31);padding:18px;border-radius:14px;border:1px solid #2D5277;box-shadow:0 8px 24px rgba(0,0,0,.18)}
div[data-testid="stMetricLabel"]{color:#9DB0C9}div[data-testid="stMetricValue"]{color:#F7FBFF}
div[data-testid="stExpander"]{background:#101D31;border:1px solid var(--line);border-radius:12px}
div[data-testid="stForm"]{background:#0E1B2E;border:1px solid var(--line);padding:1rem;border-radius:14px}
.stButton>button,.stDownloadButton>button{border-radius:9px;border:1px solid #3187B9;background:#123552;color:#E6F7FF;font-weight:600}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--cyan);color:white;background:#194A6A}
.stTextInput input,.stTextArea textarea,.stNumberInput input{background:#0B1728;color:var(--text);border-color:var(--line);border-radius:8px}
.stSelectbox>div>div,.stMultiSelect>div>div{background:#0B1728;border-color:var(--line);color:var(--text)}
div[data-testid="stAlert"]{border-radius:10px}
.wf-badge{display:inline-block;padding:5px 10px;border:1px solid #2D5277;border-radius:99px;color:#8FE4FF;background:#0D263B;font-size:.78rem;font-weight:600;margin:2px 4px 10px 0}
.wf-card{background:linear-gradient(145deg,#13243A,#0E1B2E);border:1px solid #284663;border-radius:14px;padding:20px;min-height:145px;box-shadow:0 8px 28px rgba(0,0,0,.16)}
.wf-card h3{margin:0 0 8px;color:#DDF5FF}.wf-card p{margin-bottom:0;color:#AFC1D6}
</style>
""",unsafe_allow_html=True)
st.sidebar.title('◈ WorkforceAI')
st.sidebar.caption('Intelligent HR decision support')
st.sidebar.selectbox('Perspective', ['HR Manager','Recruiter','Interviewer','Workforce Analyst'], key='user_perspective', help='Changes the label shown in the sidebar. All decisions remain with authorized humans.')
st.sidebar.markdown('<span class="wf-badge">● Evidence mode</span><span class="wf-badge">● Human review</span>',unsafe_allow_html=True)
page=st.navigation([
 st.Page('pages/0_Home.py',title='WorkforceAI',icon='🏠'),
 st.Page('pages/5_Workforce_Dashboard.py',title='Dashboard',icon='📊'),
 st.Page('pages/1_Recruitment_Intelligence.py',title='Recruitment Intelligence',icon='📄'),
 st.Page('pages/2_Interview_Agent.py',title='Intelligent Interview Agent',icon='💬'),
 st.Page('pages/3_HR_Policy_Assistant.py',title='HR Policy Assistant',icon='📚'),
 st.Page('pages/4_Attrition_Intelligence.py',title='Attrition Intelligence',icon='🔎'),
 st.Page('pages/6_Skill_Graph.py',title='Workforce Skill Graph',icon='🔗'),
 st.Page('pages/7_Model_Performance.py',title='Model Performance',icon='📈'),
 st.Page('pages/8_Project_Information.py',title='Project Information',icon='ℹ️')])
page.run()
st.sidebar.divider();st.sidebar.caption('Human decisions. Traceable evidence. No automated hiring, rejection, promotion or penalties.')
