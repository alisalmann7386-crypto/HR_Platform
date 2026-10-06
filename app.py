import streamlit as st
from src.utils.theme import apply_theme
from src.utils.access import require_access, allowed_page

st.set_page_config(page_title='WorkforceAI · People workspace',page_icon='◈',layout='wide',initial_sidebar_state='auto')
apply_theme()
role=require_access()
st.session_state['access_role']=role
st.sidebar.markdown('<div class="wf-brand"><span class="wf-brand-mark">◈</span><div><b>WorkforceAI</b><small>The people workspace</small></div></div>',unsafe_allow_html=True)
st.sidebar.caption('A thoughtful workspace for people decisions.')
st.sidebar.markdown('<span class="wf-badge">Demo workspace</span><span class="wf-badge">Human-led</span>',unsafe_allow_html=True)
nav={
    'Your workspace':[('pages/0_Home.py','Overview',':material/home:'),('pages/5_Workforce_Dashboard.py','Workforce dashboard',':material/bar_chart:')],
    'Hiring & interviews':[('pages/1_Recruitment_Intelligence.py','Candidate review',':material/person_search:'),('pages/2_Interview_Agent.py','Interview workspace',':material/forum:')],
    'People & development':[('pages/3_HR_Policy_Assistant.py','Policy library',':material/menu_book:'),('pages/4_Attrition_Intelligence.py','Retention review',':material/insights:'),('pages/6_Skill_Graph.py','Skills & capability',':material/hub:')],
    'Trust & transparency':[('pages/7_Model_Performance.py','Model performance',':material/query_stats:'),('pages/8_Project_Information.py','About this workspace',':material/info:')],
}
pages={group:[st.Page(path,title=label,icon=icon) for path,label,icon in entries if allowed_page(role,path)] for group,entries in nav.items()}
st.navigation({group:entries for group,entries in pages.items() if entries}).run()
st.sidebar.divider()
st.sidebar.caption('Evidence informs. People decide. No automated hiring, rejection, promotion or penalties.')
