import json
import streamlit as st
import pandas as pd
from src.utils.ui import title,guard
from src.utils.config import DATA
from src.utils.file_utils import extract_text
from src.recruitment.resume_parser import parse_resume
from src.recruitment.jd_parser import parse_jd
from src.recruitment.matcher import analyze,DEFAULT_WEIGHTS

def main():
    title('Recruitment Intelligence','Compare evidence against job requirements. Scores are configurable heuristics, not hiring recommendations.')
    demo=st.checkbox('Use bundled fictional demonstration candidates',value=True)
    jd_file=st.file_uploader('Optional job description document',type=['pdf','docx','txt'])
    default=(DATA/'jobs/ml_engineer.txt').read_text()
    if jd_file:default=extract_text(jd_file)
    text=st.text_area('Job description',value=default,height=240)
    backend=st.selectbox('Matching engine',['semantic','lexical'],help='Semantic uses sentence-transformer cosine similarity. Lexical uses only canonical skill aliases and is an explicit fallback.')
    uploads=[] if demo else st.file_uploader('Candidate resumes (PDF / DOCX)',type=['pdf','docx'],accept_multiple_files=True)
    with st.expander('Recruiter-configurable component weights'):
        weights={key:st.number_input(key.title()+' weight',0,100,value=value) for key,value in DEFAULT_WEIGHTS.items()}
        st.caption('Active weights are normalized. Requirements not specified are omitted. Missing evidence is not proof of missing ability.')
    if st.button('Analyze qualifications',type='primary'):
        jd=parse_jd(text)
        if not jd['mandatory_skills']:raise ValueError('No mandatory skills recognized. Add a Mandatory Skills heading with supported skills.')
        sources=[p.read_text() for p in sorted((DATA/'resumes').glob('candidate_*.txt'))] if demo else [extract_text(p) for p in uploads]
        if not sources:raise ValueError('Upload at least one resume.')
        records=[]
        with st.spinner('Extracting professional evidence and comparing requirements…'):
            for i,source in enumerate(sources,1):
                candidate=parse_resume(source,f'Candidate {i:02}')
                result=analyze(candidate,jd,weights,backend)
                records.append({'candidate':candidate,'job':jd,'analysis':result})
        st.session_state['recruitment_records']=records
        st.session_state.pop('interview_questions',None)
        st.session_state['interview_reports']=[]
    records=st.session_state.get('recruitment_records',[])
    if records:
        st.subheader('Candidate comparison')
        st.dataframe(pd.DataFrame([{'Candidate':r['candidate']['candidate_id'],'Job-Relevance Score':r['analysis']['job_relevance_score'],'Experience (stated years)':r['candidate']['experience_years'],'Strong Matches':', '.join(r['analysis']['matched_skills']),'Not Evidenced':', '.join(r['analysis']['missing_skills']),'Projects':len(r['candidate']['projects']),'Education':'; '.join(r['candidate']['education']),'Engine':r['analysis']['backend']} for r in records]),hide_index=True)
        for r in records:
            with st.expander(r['candidate']['candidate_id']+' — requirement evidence'):
                st.dataframe(pd.DataFrame(r['analysis']['mandatory']+r['analysis']['preferred']),hide_index=True)
                st.json(r['analysis']['components']);st.json(r['analysis']['evidence'])
                for warning in r['analysis']['unknowns']:st.warning(warning)
                st.caption(r['analysis']['note'])
                st.json(r['candidate'])
        with st.expander('Parsed job description JSON'):st.json(records[0]['job'])
        st.download_button('Export recruitment analysis',json.dumps(records,indent=2),'recruitment_analysis.json','application/json')
        st.page_link('pages/2_Interview_Agent.py',label='Generate interview from these candidates →')
    st.caption('Parser recognizes explicit professional sections and a curated skill vocabulary. Verify extracted experience, qualifications and evidence before use. Names and demographic fields do not enter score calculations.')
guard(main)
