import json
import streamlit as st
import pandas as pd
from src.utils.ui import title, guard
from src.utils.config import DATA
from src.utils.file_utils import extract_text
from src.recruitment.resume_parser import parse_resume
from src.recruitment.jd_parser import parse_jd
from src.recruitment.matcher import analyze, DEFAULT_WEIGHTS


def main():
    title('Recruitment Intelligence','Review job-related evidence across resumes. Scores are configurable heuristics, not hiring recommendations.')
    st.subheader('Step 1 · Job description')
    demo=st.checkbox('Use bundled fictional demonstration candidates',value=True)
    jd_file=st.file_uploader('Upload job description (TXT, PDF or DOCX)',type=['pdf','docx','txt'])
    default=(DATA/'jobs/ml_engineer.txt').read_text()
    if jd_file:default=extract_text(jd_file)
    text=st.text_area('Or paste/edit the job description',value=default,height=220)
    st.subheader('Step 2 · Candidate resumes')
    uploads=[] if demo else st.file_uploader('Upload multiple candidate resumes (PDF or DOCX)',type=['pdf','docx'],accept_multiple_files=True)
    st.caption('Bundled examples: two fictional candidates.' if demo else f'Uploaded resumes: {len(uploads or [])}.')
    backend=st.selectbox('Matching engine',['semantic','lexical'],help='Semantic compares embeddings; lexical uses canonical aliases only.')
    with st.expander('Adjust recruiter weights'):
        weights={key:st.number_input(key.title()+' weight',0,100,value=value) for key,value in DEFAULT_WEIGHTS.items()}
        st.caption('Active components are normalized; missing resume evidence does not prove missing ability.')
    st.subheader('Step 3 · Analyze qualifications')
    if st.button('Analyze qualifications',type='primary'):
        jd=parse_jd(text)
        if not jd['mandatory_skills']:raise ValueError('No mandatory skills recognized. Add a Mandatory Skills heading with supported skills.')
        sources=[p.read_text() for p in sorted((DATA/'resumes').glob('candidate_*.txt'))] if demo else [extract_text(p) for p in uploads or []]
        if not sources:raise ValueError('Upload at least one resume.')
        records=[]
        with st.spinner('Parsing resumes and comparing job requirements…'):
            for i,source in enumerate(sources,1):
                candidate=parse_resume(source,f'Candidate {i:02}')
                records.append({'candidate':candidate,'job':jd,'analysis':analyze(candidate,jd,weights,backend)})
        st.session_state['recruitment_records']=records
        st.session_state.pop('interview_questions',None)
        st.session_state.pop('latest_interview_analysis',None)
        for key in list(st.session_state):
            if key.startswith(('answer_Candidate ','notes_Candidate ','question_edit_Candidate ')):del st.session_state[key]
        st.session_state['interview_reports']=[]
    records=st.session_state.get('recruitment_records',[])
    if records:
        job=records[0]['job'];st.subheader('Parsed role')
        a,b,c=st.columns(3)
        a.metric('Job title',job['job_title']);b.metric('Mandatory skills',len(job['mandatory_skills']));c.metric('Preferred skills',len(job['preferred_skills']))
        st.write('**Mandatory:** '+(', '.join(job['mandatory_skills']) or 'None'))
        st.write('**Preferred:** '+(', '.join(job['preferred_skills']) or 'None'))
        with st.expander('Responsibilities, education and full JD JSON'):st.json(job)
        st.subheader('Step 4 · Compare candidate evidence')
        st.dataframe(pd.DataFrame([{'Candidate':r['candidate']['candidate_id'],'Job-Relevance Score':r['analysis']['job_relevance_score'],
             'Mandatory Matches':sum(x['status']=='Strong' for x in r['analysis']['mandatory']),
             'Preferred Matches':sum(x['status']=='Strong' for x in r['analysis']['preferred']),
             'Experience (stated years)':r['candidate']['experience_years'],'Projects':len(r['candidate']['projects']),
             'Education':'; '.join(r['candidate']['education']),'Missing Skills':', '.join(r['analysis']['missing_skills'])} for r in records]),hide_index=True)
        for r in records:
            analysis=r['analysis'];candidate=r['candidate']
            with st.expander(f"{candidate['candidate_id']} · matching evidence"):
                if analysis['job_relevance_score'] is not None:
                    st.metric('Job-Relevance Score',f"{analysis['job_relevance_score']:.1f}%")
                    st.progress(min(max(analysis['job_relevance_score']/100,0),1))
                a,b,c=st.columns(3)
                a.write('**Strong matches:** '+(', '.join(analysis['matched_skills']) or 'None'))
                b.write('**Partial matches:** '+(', '.join(x['requirement'] for x in analysis['mandatory']+analysis['preferred'] if x['status']=='Partial') or 'None'))
                c.write('**Not evidenced:** '+(', '.join(analysis['missing_skills']) or 'None'))
                st.dataframe(pd.DataFrame(analysis['mandatory']+analysis['preferred']),hide_index=True)
                st.write('**Projects:** '+('; '.join(candidate['projects']) or 'Not provided'))
                st.write('**Education and certifications:** '+('; '.join(candidate['education']+candidate['certifications']) or 'Not provided'))
                for warning in analysis['unknowns']:st.warning(warning)
                st.caption(analysis['note'])
        st.download_button('Export recruitment analysis',json.dumps(records,indent=2),'recruitment_analysis.json','application/json')
        selected=st.selectbox('Choose candidate for interview',range(len(records)),format_func=lambda i:records[i]['candidate']['candidate_id'])
        if st.button('Generate interview for selected candidate'):
            st.session_state['interview_candidate_index']=selected
            st.switch_page('pages/2_Interview_Agent.py')
    st.caption('Verify extracted evidence before use. Names and demographic fields do not enter score calculations.')


guard(main)
