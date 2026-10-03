from pathlib import Path
import pandas as pd
from src.utils.config import DATA, POLICIES
from src.rag.bootstrap import ensure_policy_index
from src.recruitment.resume_parser import parse_resume
from src.recruitment.jd_parser import parse_jd
from src.recruitment.matcher import analyze
from src.interview.question_generator import generate_questions
from scripts.evaluate_recruitment import evaluate as recruitment_evaluate
from scripts.evaluate_calibration import evaluate as calibration_evaluate


def test_first_visit_builds_and_reuses_policy_index(tmp_path):
    dest=tmp_path/'index'
    a=ensure_policy_index(POLICIES,dest,backend='lexical')
    assert a['documents']==6 and (dest/'index.faiss').exists()
    b=ensure_policy_index(POLICIES,dest,backend='lexical')
    assert b['created']==a['created']


def test_benchmark_reports_real_failures_when_pair_is_changed(tmp_path):
    data=pd.read_csv(DATA/'evaluation/recruitment_cases.csv')
    baseline,_=recruitment_evaluate(DATA/'evaluation/recruitment_cases.csv',backend='lexical')
    assert baseline['cases']>=25
    # A false gold label must reduce measured quality, not remain a hard-coded perfect score.
    data.loc[data.case_id=='R03','expected_alignment']=1
    changed=tmp_path/'cases.csv';data.to_csv(changed,index=False)
    altered,_=recruitment_evaluate(changed,backend='lexical')
    assert altered['requirement_alignment']['recall']<baseline['requirement_alignment']['recall']


def test_question_source_traces_real_resume_or_job():
    candidate=parse_resume((DATA/'resumes/candidate_01.txt').read_text())
    jd=parse_jd((DATA/'jobs/ml_engineer.txt').read_text())
    questions=generate_questions(candidate,jd,analyze(candidate,jd,backend='lexical'))
    assert questions and all(q['based_on'] for q in questions)
    assert any(q['based_on'].startswith('Resume project:') for q in questions)
    assert any(q['based_on'].startswith('Job requirement:') for q in questions)


def test_bootstrap_report_uses_saved_labels_and_changes_with_threshold():
    saved=pd.read_csv(Path(__file__).resolve().parents[1]/'reports/test_predictions.csv')
    low,_=calibration_evaluate(saved,.2,n_bootstrap=100)
    high,_=calibration_evaluate(saved,.8,n_bootstrap=100)
    assert low['positive_rows']==int(saved.Actual.sum())
    assert low['intervals']['recall']!=high['intervals']['recall']
    assert low['intervals']==calibration_evaluate(saved,.2,n_bootstrap=100)[0]['intervals']
