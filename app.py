import streamlit as st
st.set_page_config(page_title='WorkforceAI',page_icon='◈',layout='wide')
st.markdown("<style>.stApp{background:#fff}h1,h2,h3{color:#10233f}div[data-testid='stMetric']{background:#f1f5f9;padding:18px;border-radius:10px;border:1px solid #e2e8f0}section[data-testid='stSidebar']{background:#f8fafc}</style>",unsafe_allow_html=True)
st.sidebar.title('◈ WorkforceAI')
st.sidebar.caption('Intelligent HR decision support')
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
