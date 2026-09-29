import streamlit as st
from src.utils.ui import title
from src.utils.config import MODELS,INDEX

title('WorkforceAI','AI-Driven Intelligent Workforce Management and HR Decision Support Platform')
st.markdown('### Understand people. Detect risks. Discover skills. Support better HR decisions.')
st.write('A single workspace for recruitment evidence, interview preparation, policy retrieval, attrition analysis and workforce capability planning.')
st.markdown('<span class="wf-badge">6 connected modules</span><span class="wf-badge">IBM attrition dataset</span><span class="wf-badge">MiniLM + FAISS RAG</span><span class="wf-badge">SHAP explanations</span>',unsafe_allow_html=True)
start_tab,modules_tab,demo_tab=st.tabs(['Start here','Explore modules','7-minute HR demo'])
with start_tab:
    st.subheader('Choose a starting point')
    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown('<div class="wf-card"><h3>Need a workforce overview?</h3><p>Open Dashboard to see departments, model signals, skills and synthetic capacity gaps together.</p></div>',unsafe_allow_html=True)
        st.page_link('pages/5_Workforce_Dashboard.py',label='Open dashboard →')
    with c2:
        st.markdown('<div class="wf-card"><h3>Review a candidate?</h3><p>Upload a job description and resumes to inspect matched, partial and not-evidenced requirements.</p></div>',unsafe_allow_html=True)
        st.page_link('pages/1_Recruitment_Intelligence.py',label='Open recruitment →')
    with c3:
        st.markdown('<div class="wf-card"><h3>Check a policy?</h3><p>Ask a question and inspect the exact document, page, section and retrieved evidence.</p></div>',unsafe_allow_html=True)
        st.page_link('pages/3_HR_Policy_Assistant.py',label='Open policy assistant →')
with modules_tab:
    st.write('Use the sidebar to move between connected modules. Recruitment records remain available to the interview page during the same session; dashboard summaries use the shared Employee_ID.')
with demo_tab:
    st.write('1. Dashboard → 2. Recruitment → 3. Interview → 4. Policy Assistant → 5. Attrition → 6. Skill Graph → 7. Model Performance')
    st.info('All outputs support human review. The system does not hire, reject, terminate, promote, change compensation or penalize employees.')
modules=[('Recruitment Intelligence','Compare job-relevant qualifications with inspectable skill and project evidence.','pages/1_Recruitment_Intelligence.py'),('Interview Assistance','Turn candidate claims and role requirements into verification questions.','pages/2_Interview_Agent.py'),('Policy Reasoning','Retrieve policy sections with document and page citations.','pages/3_HR_Policy_Assistant.py'),('Attrition Analytics','Inspect model estimates, held-out metrics and SHAP contributions.','pages/4_Attrition_Intelligence.py'),('Skill Intelligence','Explore employee–skill–role relationships and capacity gaps.','pages/6_Skill_Graph.py'),('Workforce Analytics','Join multiple sources by Employee_ID and inspect department summaries.','pages/5_Workforce_Dashboard.py')]
for start in [0,3]:
    for col,(name,desc,path) in zip(st.columns(3),modules[start:start+3]):
        with col:
            with st.container(border=True):st.subheader(name);st.write(desc);st.page_link(path,label='Open module →')
st.info('IBM HR records are synthetic. Auxiliary skills, performance, attendance and training are generated demo data. Uploaded policies are fictional examples. This application does not authorize employment decisions.')
a,b=st.columns(2);a.metric('Trained pipeline','Ready' if (MODELS/'attrition_model.joblib').exists() else 'Run training');b.metric('Policy index','Ready' if (INDEX/'metadata.json').exists() else 'Build index')
st.page_link('pages/5_Workforce_Dashboard.py',label='Open workforce dashboard →')
