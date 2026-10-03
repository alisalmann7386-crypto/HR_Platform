import streamlit as st
from src.utils.ui import title
from src.utils.config import MODELS, INDEX

title('WorkforceAI', 'AI-Driven Intelligent Workforce Management and HR Decision Support Platform')
st.markdown('### Understand people. Detect risks. Discover skills. Support better HR decisions.')
st.write('A connected workspace for evidence-based recruitment, interviews, HR policy retrieval, attrition analytics and capability planning.')
st.markdown('<span class="wf-badge">6 connected modules</span><span class="wf-badge">Fictional policy pack</span><span class="wf-badge">Human review required</span>',unsafe_allow_html=True)
modules=[('📄','Recruitment Intelligence','Structured JD and resume comparison','pages/1_Recruitment_Intelligence.py'),
         ('💬','Interview Assistance','Questions grounded in candidate and job evidence','pages/2_Interview_Agent.py'),
         ('📚','Policy Reasoning','Page and section citations from uploaded PDFs','pages/3_HR_Policy_Assistant.py'),
         ('🔎','Attrition Analytics','Saved model estimates and SHAP contributions','pages/4_Attrition_Intelligence.py'),
         ('🔗','Skill Intelligence','Employee–skill–role graph and capacity gaps','pages/6_Skill_Graph.py'),
         ('📊','Workforce Analytics','Joined department summaries and insights','pages/5_Workforce_Dashboard.py')]
st.subheader('Explore the platform')
for start in (0,3):
    for col,(icon,name,desc,path) in zip(st.columns(3),modules[start:start+3]):
        with col:
            st.markdown(f'<div class="wf-card"><h3>{icon} {name}</h3><p>{desc}</p></div>',unsafe_allow_html=True)
            st.page_link(path,label='Open module →')
start_tab, demo_tab = st.tabs(['Start here','7-minute demo'])
with start_tab:
    st.subheader('Choose your workflow')
    paths=[('📊','Explore workforce','See department signals, skills and capacity gaps together.','pages/5_Workforce_Dashboard.py'),
           ('📄','Compare candidates','Load a role and resumes, then inspect matched and missing evidence.','pages/1_Recruitment_Intelligence.py'),
           ('📚','Check a policy','Find the exact document, page and section behind an answer.','pages/3_HR_Policy_Assistant.py')]
    for col,(icon,name,desc,path) in zip(st.columns(3),paths):
        with col:
            st.markdown(f'<div class="wf-card"><h3>{icon} {name}</h3><p>{desc}</p></div>',unsafe_allow_html=True)
            st.page_link(path,label='Open →')
    a,b=st.columns(2)
    a.metric('Trained model','Ready' if (MODELS/'attrition_model.joblib').exists() else 'Run training')
    b.metric('Policy evidence','Ready' if (INDEX/'metadata.json').exists() else 'Builds on first visit')
with demo_tab:
    st.write('Dashboard → Recruitment → Interview → Policy Assistant → Attrition → Model Performance → Skill Graph → Dashboard')
    st.info('This prototype supports human decisions. Records, policies and auxiliary workforce data are synthetic or fictional.')
st.subheader('How information moves through WorkforceAI')
st.caption('Professional source data are validated, analyzed and shown with evidence before human review.')
for col,label in zip(st.columns(5),['1 · Resumes, jobs, policies and employee data','2 · Validation and Employee_ID joins','3 · ML, RAG and skill graph','4 · Workforce intelligence dashboard','5 · Human HR review']):
    with col:st.markdown(f'<div class="wf-card"><h3>{label}</h3></div>',unsafe_allow_html=True)
