import json
import numpy as np
import pandas as pd
import pytest
from src.utils.config import DATA,IBM,MODELS,REPORTS,POLICIES,INDEX
from src.utils.file_utils import extract_text
from src.utils.helpers import employee_ids,read_json
from src.attrition.preprocessing import load_data,features,split_data,preprocessor
from src.attrition.predict import load_model,predict_batch
from src.attrition.explain import contributions
from src.recruitment.resume_parser import parse_resume
from src.recruitment.jd_parser import parse_jd
from src.recruitment.matcher import analyze,match_skills
from src.rag.document_loader import load_documents
from src.rag.chunker import chunk_documents
from src.rag.vector_store import build_index,search
from src.rag.policy_agent import answer_question,REFUSAL
from src.skills.skill_gap import skill_gaps
from src.skills.skill_graph import build_graph
from src.interview.question_generator import generate_questions
from src.interview.response_analyzer import analyze_response

@pytest.fixture
def df():return load_data(IBM)
@pytest.fixture
def candidate():return parse_resume((DATA/'resumes/candidate_01.txt').read_text())
@pytest.fixture
def jd():return parse_jd((DATA/'jobs/ml_engineer.txt').read_text())

def test_resume_pdf():
    result=parse_resume(extract_text(DATA/'resumes/candidate_01.pdf'));assert 'Python' in result['skills'];assert result['projects']
def test_resume_docx():
    result=parse_resume(extract_text(DATA/'resumes/candidate_02.docx'));assert 'SQL' in result['skills'];assert result['experience_years']==2

def test_resume_sensitive_exclusion():
    a=parse_resume('Person A\nGender: Male\nSkills\nPython\nExperience\n1 year of experience\nProjects\nBuilt SQL tool')
    b=parse_resume('Person B\nGender: Female\nSkills\nPython\nExperience\n1 year of experience\nProjects\nBuilt SQL tool')
    assert a==b

def test_unknown_experience():assert parse_resume('Skills\nPython')['experience_years'] is None

def test_jd(jd):assert jd['minimum_experience']==1 and 'PyTorch' in jd['mandatory_skills'] and 'AWS' in jd['preferred_skills']
def test_alias(candidate):
    result=match_skills(['Natural Language Processing'],candidate,'lexical');assert result[0]['status']=='Strong';assert result[0]['evidence']
def test_match_no_hiring_label(candidate,jd):
    result=analyze(candidate,jd,backend='lexical');assert 0<=result['job_relevance_score']<=100;assert 'human' in result['note'].lower()
def test_recruitment_interview_integration(candidate,jd):
    analysis=analyze(candidate,jd,backend='lexical');questions=generate_questions(candidate,jd,analysis);assert any('RAG' in q['question'] for q in questions)
    report=analyze_response({'topic':'overfitting'},'Training accuracy is high but validation accuracy is low. Regularization and cross-validation can help.')
    assert len(report['concepts_demonstrated'])>=3

def test_employee_ids(df):assert df.Employee_ID.is_unique and df.Employee_ID.iloc[0]=='EMP-1'
def test_duplicate_ids_rejected():
    with pytest.raises(ValueError):employee_ids(pd.DataFrame({'EmployeeNumber':[1,1]}))
def test_sensitive_not_predictors(df):assert not {'Age','Gender','MaritalStatus','EmployeeNumber','Employee_ID','Attrition','EmployeeCount'} & set(features(df))
def test_split_disjoint(df):
    a,b,c=split_data(df);sets=[set(x.Employee_ID) for x in [a,b,c]]
    assert not (sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2]);assert sum(map(len,sets))==1470
    assert [len(a),len(b),len(c)]==[1029,220,221]
def test_preprocessing_fit_train_only(df):
    tr,va,_=split_data(df);X=features(tr);prep=preprocessor(X).fit(X)
    assert np.allclose(prep.named_transformers_['numeric'].named_steps['impute'].statistics_,X.select_dtypes(include='number').median().values)
    alt=features(va).copy();alt['Department']='UNSEEN_DEPARTMENT';assert prep.transform(alt).shape[0]==len(va)
def test_reload_predictions_match_saved_test(df):
    pipe,meta=load_model();_,_,test=split_data(df);saved=pd.read_csv(REPORTS/'test_predictions.csv')
    assert np.allclose(predict_batch(test,pipe,meta).Attrition_Probability,saved.Attrition_Probability)
def test_manual_prediction():
    _,meta=load_model();row=pd.DataFrame([{k:v['default'] for k,v in meta['schema'].items()}]);out=predict_batch(row);assert len(out)==1 and 0<=out.Attrition_Probability.iloc[0]<=1
def test_invalid_batch(df):
    with pytest.raises(ValueError):predict_batch(df.drop(columns='MonthlyIncome'))
    x=df.head(1).copy();x['MonthlyIncome']=-5
    with pytest.raises(ValueError):predict_batch(x)
def test_shap_additivity(df):
    pipe,meta=load_model();X=features(df.head(3));bg=pd.read_csv(MODELS/'shap_background.csv');v,n=contributions(pipe,X,bg)
    assert v.shape==(3,len(n));assert np.isfinite(v).all()
    import shap
    model=pipe.named_steps['model'];prep=pipe.named_steps['preprocess'];explainer=shap.LinearExplainer(model,prep.transform(bg))
    e=explainer(prep.transform(X));assert np.allclose(e.base_values+e.values.sum(axis=1),model.decision_function(prep.transform(X)))
def test_tree_shap(df):
    import joblib,shap
    pipe=joblib.load(MODELS/'weighted_lightgbm.joblib');X=features(df.head(3));prep=pipe.named_steps['preprocess'];model=pipe.named_steps['model'];e=shap.TreeExplainer(model)(prep.transform(X));assert np.allclose(e.base_values+e.values.sum(axis=1),model.predict(prep.transform(X),raw_score=True))
def test_policy_chunks():
    pages,errors=load_documents(POLICIES);chunks=chunk_documents(pages);assert len(pages)==12 and not errors
    assert len({x['chunk_id'] for x in chunks})==len(chunks)
    assert all(x['page_number'] in [1,2] and x['section'] for x in chunks)
    assert any(x['section'].startswith('3.1 Temporary') for x in chunks)
    assert not any(x['section'].startswith(('10 working','500 was')) for x in chunks)
def test_chunk_invalid_overlap():
    with pytest.raises(ValueError):chunk_documents([],50,50)
def test_lexical_retrieval_and_citations(tmp_path):
    build_index(POLICIES,tmp_path,backend='lexical');hits,meta=search('medical leave temporary remote work',6,tmp_path,.05)
    assert hits and any(x['document_name']=='Work_From_Home_Policy.pdf' for x in hits)
    for hit in hits:assert hit['page_number']>0 and hit['chunk_id'] and hit['section']
    response=answer_question('medical leave temporary remote work',6,.05,False,tmp_path);assert 'Source:' in response['answer']
def test_abstention(tmp_path):
    build_index(POLICIES,tmp_path,backend='lexical');answer=answer_question('quasar gravitational lensing xyzzy',6,.3,False,tmp_path);assert answer['answer']==REFUSAL
def test_llm_invalid_citation_abstains(monkeypatch,tmp_path):
    build_index(POLICIES,tmp_path,backend='lexical')
    monkeypatch.setattr('src.rag.policy_agent.complete',lambda *args:json.dumps({'supported':True,'claims':[{'text':'Unlimited leave','source_id':999,'quote':'fake'}]}))
    assert REFUSAL in answer_question('sick leave',6,.05,True,tmp_path)['answer']
def test_gap_levels_and_distinct():
    s=pd.DataFrame([['A','D','R','Python','Beginner'],['B','D','R','Python','Advanced'],['B','D','R','Python','Advanced']],columns=['Employee_ID','Department','Job_Role','Skill','Skill_Level'])
    r=pd.DataFrame([['R','Python','Intermediate',3,'High']],columns=['Role','Skill','Required_Level','Required_Employees','Priority']);g=skill_gaps(s,r)
    assert g.Available.iloc[0]==1 and g.Gap.iloc[0]==2
    graph=build_graph(s,r);assert graph['Employee:B']['Skill:Python']['relation']=='HAS_SKILL';assert graph['Role:R']['Skill:Python']['relation']=='REQUIRES'
def test_unified_dashboard():
    from src.dashboard.analytics import load_workforce,department_summary
    joined,tables=load_workforce();assert len(joined)==1470 and joined.Employee_ID.is_unique
    assert joined[['Performance_Score','Attendance_Rate','Training_Hours','Attrition_Probability']].notna().all().all()
    assert department_summary(joined).Employees.sum()==1470

@pytest.mark.semantic
def test_real_semantic_matching(candidate,jd):
    from src.utils.embeddings import encode
    vectors=encode(['natural language processing','NLP','hotel expense report'])
    assert vectors.shape==(3,384) and float(vectors[0]@vectors[1])>float(vectors[0]@vectors[2])
    result=analyze(candidate,jd,backend='semantic');assert result['evidence']['projects'] and 0<=result['job_relevance_score']<=100
@pytest.mark.semantic
def test_semantic_policy_retrieval():
    hits,meta=search('Can an employee take medical leave followed by temporary work from home?',6,INDEX,.30)
    assert meta['backend']=='semantic';assert {'Leave_Policy.pdf','Work_From_Home_Policy.pdf'}<=set(x['document_name'] for x in hits)

@pytest.mark.parametrize('filename',['candidate_01.pdf','candidate_02.docx'])
def test_uploaded_resume_can_be_read_repeatedly(filename):
    from io import BytesIO
    upload=BytesIO((DATA/'resumes'/filename).read_bytes())
    upload.seek(7)
    first=extract_text(upload,name=filename)
    assert extract_text(upload,name=filename)==first
    assert upload.tell()==7

@pytest.mark.parametrize('payload',[[],None,'invalid',{'supported':True,'claims':[None]}, {'supported':True,'claims':'bad'}, {'supported':'false','claims':[{'text':'Approved','source_id':1,'quote':'Medical leave'}]}, {'supported':True,'claims':[{'text':None,'source_id':1,'quote':'Medical leave'}]}])
def test_malformed_policy_llm_abstains(monkeypatch,payload):
    evidence=[{'text':'Medical leave requires approval.','document_name':'policy.pdf','page_number':1,'section':'Leave'}]
    monkeypatch.setattr('src.rag.policy_agent.retrieve',lambda *args:(evidence,{'backend':'lexical'}))
    monkeypatch.setattr('src.rag.policy_agent.complete',lambda *args:json.dumps(payload))
    assert answer_question('medical leave',use_llm=True)['mode']=='abstention'

@pytest.mark.parametrize('ids',[['','EMP-2'],['  ','EMP-2'],['EMP-1',' EMP-1 ']])
def test_blank_or_normalized_duplicate_ids_rejected(df,ids):
    rows=df.head(2).copy();rows['Employee_ID']=ids
    with pytest.raises(ValueError,match='Employee_ID'):predict_batch(rows)

@pytest.mark.parametrize('value',[None,'','  '])
def test_skill_capacity_rejects_missing_identity(value):
    skills=pd.DataFrame([[value,'D','R','Python','Advanced']],columns=['Employee_ID','Department','Job_Role','Skill','Skill_Level'])
    req=pd.DataFrame([['R','Python','Intermediate',3,'High']],columns=['Role','Skill','Required_Level','Required_Employees','Priority'])
    with pytest.raises(ValueError,match='Employee_ID'):skill_gaps(skills,req)
