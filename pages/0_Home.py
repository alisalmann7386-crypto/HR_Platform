import streamlit as st
from src.utils.ui import title
from src.utils.config import MODELS,INDEX

title('WorkforceAI','AI-Driven Intelligent Workforce Management and HR Decision Support Platform')
st.markdown('### Understand people. Detect risks. Discover skills. Support better HR decisions.')
st.write('Connect employee records, policy evidence, recruitment analysis and workforce capabilities in one explainable academic platform.')
modules=[('Recruitment Intelligence','Compare job-relevant qualifications with inspectable skill and project evidence.','pages/1_Recruitment_Intelligence.py'),('Interview Assistance','Turn candidate claims and role requirements into verification questions.','pages/2_Interview_Agent.py'),('Policy Reasoning','Retrieve policy sections with document and page citations.','pages/3_HR_Policy_Assistant.py'),('Attrition Analytics','Inspect model estimates, held-out metrics and SHAP contributions.','pages/4_Attrition_Intelligence.py'),('Skill Intelligence','Explore employee–skill–role relationships and capacity gaps.','pages/6_Skill_Graph.py'),('Workforce Analytics','Join multiple sources by Employee_ID and inspect department summaries.','pages/5_Workforce_Dashboard.py')]
for start in [0,3]:
    for col,(name,desc,path) in zip(st.columns(3),modules[start:start+3]):
        with col:
            with st.container(border=True):st.subheader(name);st.write(desc);st.page_link(path,label='Open module →')
st.info('IBM HR records are synthetic. Auxiliary skills, performance, attendance and training are generated demo data. Uploaded policies are fictional examples. This application does not authorize employment decisions.')
a,b=st.columns(2);a.metric('Trained pipeline','Ready' if (MODELS/'attrition_model.joblib').exists() else 'Run training');b.metric('Policy index','Ready' if (INDEX/'metadata.json').exists() else 'Build index')
st.page_link('pages/5_Workforce_Dashboard.py',label='Open workforce dashboard →')
