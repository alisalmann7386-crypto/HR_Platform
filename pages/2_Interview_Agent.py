import json
import streamlit as st
from src.utils.ui import title, guard, llm_toggle
from src.utils.helpers import timestamp
from src.interview.question_generator import generate_questions
from src.interview.response_analyzer import analyze_response


def main():
    title('Intelligent Interview Agent', 'Verify specific resume claims against the role using questions reviewed by an interviewer.')
    records = st.session_state.get('recruitment_records', [])
    if not records:
        st.info('Start in Recruitment Intelligence. Candidate and job evidence will appear here after analysis.')
        st.page_link('pages/1_Recruitment_Intelligence.py', label='Open recruitment →')
        return
    selected = st.selectbox('Candidate', range(len(records)), format_func=lambda i: records[i]['candidate']['candidate_id'], index=min(st.session_state.get('interview_candidate_index', 0), len(records)-1))
    record = records[selected]
    cid = record['candidate']['candidate_id']
    st.caption(f"Role: {record['job']['job_title']}")
    left, right = st.columns(2)
    left.write('**Matched skills:** ' + (', '.join(record['analysis']['matched_skills']) or 'None evidenced'))
    right.write('**Skills to verify:** ' + (', '.join(record['analysis']['missing_skills']) or 'None listed'))
    with st.expander('Relevant resume projects'):
        st.write(record['candidate']['projects'] or ['No projects extracted; review the resume.'])
    llm = llm_toggle('interview_llm')
    if st.button('Generate interview', type='primary'):
        with st.spinner('Preparing questions from role and resume evidence…'):
            questions = generate_questions(record['candidate'], record['job'], record['analysis'], llm)
        st.session_state['interview_questions'] = {'candidate_id': cid, 'questions': questions}
        st.session_state.pop('latest_interview_analysis', None)
    pack = st.session_state.get('interview_questions', {})
    if pack.get('candidate_id') == cid:
        questions = pack['questions']
        if not questions:
            st.info('All questions were removed. Generate a new interview to start again.')
        else:
            st.subheader(f'Interview questions · {len(questions)} remaining')
            i = st.selectbox('Question', range(len(questions)), format_func=lambda n: f"{n+1}. {questions[n]['category']}")
            q = questions[i]
            st.caption('Why this question: ' + q.get('based_on', 'Interviewer review required'))
            edited = st.text_area('Edit question before asking', value=q['question'], key=f'question_edit_{cid}_{i}')
            if edited.strip() and edited.strip() != q['question']:
                q['question'] = edited.strip()
                st.caption('Edited by interviewer; source context still requires review.')
            response = st.text_area('Candidate answer', height=170, key=f'answer_{cid}_{i}')
            notes = st.text_area('Interviewer notes', key=f'notes_{cid}_{i}')
            if st.button('Analyze answer and add to report'):
                analysis = analyze_response(q, response, llm)
                report = {'candidate_id': cid, 'job_role': record['job']['job_title'], 'question': dict(q),
                          'answer': response, 'analysis': analysis, 'interviewer_notes': notes, 'timestamp': timestamp()}
                st.session_state.setdefault('interview_reports', []).append(report)
                st.session_state['latest_interview_analysis'] = report
            report = st.session_state.get('latest_interview_analysis')
            if report and report['candidate_id'] == cid and report['question'] == q:
                st.json(report['analysis'])
            if st.button('Remove this question'):
                questions.pop(i)
                st.session_state.pop('latest_interview_analysis', None)
                st.rerun()
    reports = [r for r in st.session_state.get('interview_reports', []) if r['candidate_id'] == cid]
    if reports:
        st.download_button('Export structured interview report', json.dumps(reports, indent=2), 'interview_report.json', 'application/json')
        markdown = '\n\n'.join(f'## {r["question"]["question"]}\nBased on: {r["question"].get("based_on", "Interviewer-reviewed question")}\nAnswer: {r["answer"]}\n\nAnalysis: {json.dumps(r["analysis"], indent=2)}\n\nInterviewer notes: {r["interviewer_notes"]}' for r in reports)
        st.download_button('Export readable report', f'# {cid} — {record["job"]["job_title"]}\n\n' + markdown, 'interview_report.md', 'text/markdown')
    st.info('Local mode checks concept words and does not establish technical correctness. The interviewer owns edits and final interpretation.')


guard(main)
