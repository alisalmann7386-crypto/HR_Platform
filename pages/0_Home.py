import streamlit as st
from src.utils.ui import module_link
from src.utils.access import allowed_page

st.markdown('''<div class="wf-hero"><div class="wf-eyebrow">PEOPLE OPERATIONS / YOUR WORKSPACE</div><h1>Better context.<br><em>More human decisions.</em></h1><p>Prepare for interviews, understand your workforce and find the policy evidence you need — in one considered workspace.</p></div>''',unsafe_allow_html=True)
st.caption('Demo environment · historical workforce records, synthetic auxiliary data and fictional policies.')
records=st.session_state.get('recruitment_records',[])
a,b,c=st.columns(3)
a.metric('Candidates in this session',len(records))
b.metric('Answers reviewed this session',len(st.session_state.get('interview_reports',[])))
c.metric('Decision owner','You')
st.subheader('What would you like to work on?')
workflows=[
    ('01','Prepare your next hire','Compare job requirements with resume evidence, then build a focused interview.','pages/1_Recruitment_Intelligence.py','Review candidates'),
    ('02','Understand your workforce','Explore department patterns, retention signals and capability needs.','pages/5_Workforce_Dashboard.py','Explore workforce'),
    ('03','Find the policy behind it','Read cited excerpts, including conditions and approval requirements.','pages/3_HR_Policy_Assistant.py','Open policy library')]
visible=[w for w in workflows if allowed_page(st.session_state.get('access_role','admin'),w[3])]
for col,(number,name,description,path,action) in zip(st.columns(len(visible)),visible):
    with col:
        st.markdown(f'<div class="wf-card"><span class="wf-step">{number}</span><h3>{name}</h3><p>{description}</p></div>',unsafe_allow_html=True)
        module_link(path,action+' →')
st.subheader('Keep the review moving')
left,right=st.columns(2)
with left:
    if records:
        st.success(f'{len(records)} candidates have evidence ready for interview review.')
        module_link('pages/2_Interview_Agent.py','Continue to interviews →')
    else:st.info('Start with the two fictional candidates in Candidate review, or explore the bundled workforce dashboard.')
with right:
    st.info('Review source text before acting. Missing evidence means unknown. Keep people in control.')
    module_link('pages/7_Model_Performance.py','Inspect model quality →')
