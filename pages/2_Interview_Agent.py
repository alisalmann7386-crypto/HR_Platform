import json
import streamlit as st
from src.utils.ui import title,guard,llm_toggle
from src.utils.helpers import timestamp
from src.interview.question_generator import generate_questions
from src.interview.response_analyzer import analyze_response

def main():
    title('Intelligent Interview Agent','Verify resume claims using role-specific questions and an inspectable technical rubric.')
    records=st.session_state.get('recruitment_records',[])
    if not records:st.info('Analyze candidates in Recruitment Intelligence first. The same candidate, job and matching evidence are reused here.');st.page_link('pages/1_Recruitment_Intelligence.py',label='Open recruitment →');return
    selected=st.selectbox('Candidate',range(len(records)),format_func=lambda i:records[i]['candidate']['candidate_id'])
    record=records[selected];cid=record['candidate']['candidate_id'];llm=llm_toggle('interview_llm')
    if st.button('Generate interview',type='primary'):
        st.session_state['interview_questions']={'candidate_id':cid,'questions':generate_questions(record['candidate'],record['job'],record['analysis'],llm)}
    pack=st.session_state.get('interview_questions',{})
    if pack.get('candidate_id')==cid:
        questions=pack['questions'];i=st.selectbox('Question',range(len(questions)),format_func=lambda i:questions[i]['category']+' — '+questions[i]['question'])
        q=questions[i];st.write(q['question']);response=st.text_area('Candidate answer',height=170,key=f'answer_{cid}_{i}');notes=st.text_area('Interviewer notes',key=f'notes_{cid}_{i}')
        if st.button('Analyze answer and add to report'):
            analysis=analyze_response(q,response,llm)
            report={'candidate_id':cid,'job_role':record['job']['job_title'],'question':q,'answer':response,'analysis':analysis,'interviewer_notes':notes,'timestamp':timestamp()}
            st.session_state.setdefault('interview_reports',[]).append(report);st.session_state['latest_interview_analysis']=report
        report=st.session_state.get('latest_interview_analysis')
        if report and report['candidate_id']==cid and report['question']==q:st.json(report['analysis'])
    reports=[r for r in st.session_state.get('interview_reports',[]) if r['candidate_id']==cid]
    if reports:
        st.download_button('Export structured interview report',json.dumps(reports,indent=2),'interview_report.json','application/json')
        markdown='\n\n'.join(f'## {r["question"]["question"]}\nAnswer: {r["answer"]}\n\nAnalysis: {json.dumps(r["analysis"],indent=2)}\n\nInterviewer notes: {r["interviewer_notes"]}' for r in reports)
        st.download_button('Export readable report',f'# {cid} — {record["job"]["job_title"]}\n\n'+markdown,'interview_report.md','text/markdown')
    st.info('Local mode checks concept words; it cannot establish correctness. LLM mode adds a draft technical interpretation with quoted evidence. No personality, honesty, intelligence or employability judgments are produced by the rubric.')
guard(main)
