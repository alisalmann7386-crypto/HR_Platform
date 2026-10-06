"""Regressions for failures reproduced in the October repository review."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from io import BytesIO
import json
import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from src.utils.config import ROOT, POLICIES
from src.recruitment.resume_parser import parse_resume
from src.recruitment.jd_parser import parse_jd
from src.recruitment.skill_extractor import extract_skills
from src.recruitment.matcher import analyze
from src.interview.response_analyzer import analyze_response
from src.interview.question_generator import generate_questions
from src.rag.bootstrap import ensure_policy_index
from src.rag.vector_store import build_index, validate_index, search
from src.rag.policy_agent import answer_question
from src.attrition.predict import load_model, validate_model_versions
from src.utils.validators import validate_features


def interview_app():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run()
    app.switch_page('pages/1_Recruitment_Intelligence.py').run()
    app.selectbox[0].set_value('lexical').run()
    app.button[0].click().run()
    return app.switch_page('pages/2_Interview_Agent.py').run()


def test_drafts_survive_question_and_page_navigation():
    app=interview_app();app.button[0].click().run()
    app.text_area[1].set_value('First draft').run()
    app.text_area[2].set_value('Verify example').run()
    app.selectbox[1].set_value(1).run()
    assert app.text_area[1].value==''
    app.text_area[1].set_value('Second draft').run()
    app.selectbox[1].set_value(0).run()
    assert app.text_area[1].value=='First draft' and app.text_area[2].value=='Verify example'
    app.switch_page('pages/5_Workforce_Dashboard.py').run()
    app.switch_page('pages/2_Interview_Agent.py').run()
    assert app.text_area[1].value=='First draft'
    assert not app.exception and not app.error


def test_delete_and_regenerate_cannot_reassign_old_answers():
    app=interview_app();app.button[0].click().run()
    old=deepcopy(app.session_state['interview_questions'])
    app.text_area[1].set_value('Answer to removed question').run()
    app.button[2].click().run()
    assert app.session_state['interview_questions']['questions'][0]['question_id']==old['questions'][1]['question_id']
    assert app.text_area[1].value==''
    app.text_area[1].set_value('Original project example').run();app.button[1].click().run()
    assert any('concepts_demonstrated' in e.value for e in app.json)
    app.text_area[1].set_value('Unreviewed changed answer').run()
    assert not any('concepts_demonstrated' in e.value for e in app.json)
    app.button[0].click().run()
    assert app.session_state['interview_questions']['interview_id']!=old['interview_id']
    assert app.text_area[1].value==''
    assert app.session_state['interview_reports'][0]['answer']=='Original project example'
    assert 'draft' not in app.session_state['interview_reports'][0]['question']


@pytest.mark.parametrize('heading',['References','Hobbies','Personal information'])
def test_unsupported_resume_sections(heading):
    parsed=parse_resume(f'Skills: Python\nExperience\nBuilt SQL services\n{heading}\nAlice uses AWS and Docker\nProjects\nBuilt a FastAPI service')
    assert {'Python','SQL','FastAPI'}<=set(parsed['skills'])
    assert not {'AWS','Docker'}&set(parsed['skills'])


def test_requirement_first_description():
    assert set(parse_jd('Python required\nSQL required')['mandatory_skills'])=={'Python','SQL'}


@pytest.mark.parametrize('separator',['\n','. '])
def test_positive_skill_after_negated_occurrence(separator):
    assert [x['skill'] for x in extract_skills('No Python experience'+separator+'Built Python services')]==['Python']
    assert extract_skills('No Python experience. Without AWS certification.')==[]


def test_missing_projects_does_not_increase_score(monkeypatch):
    monkeypatch.setattr('src.recruitment.matcher.encode',lambda texts:np.ones((len(texts),1),dtype='float32')*.5)
    candidate=parse_resume('Skills\nPython\nProjects\nBuilt services')
    jd=parse_jd('Developer\nRequirements: Python\nResponsibilities:\nBuild services')
    complete=analyze(candidate,jd)
    candidate['projects']=[]
    missing=analyze(candidate,jd)
    assert complete['active_weight_total']==missing['active_weight_total']
    assert missing['job_relevance_score']<=complete['job_relevance_score']


@pytest.mark.parametrize('change',[{'JobLevel':999},{'Education':0},{'StockOptionLevel':9},{'NumCompaniesWorked':1.5},{'YearsAtCompany':99},{'YearsInCurrentRole':99},{'PerformanceRating':99}])
def test_invalid_feature_domains(change):
    _,meta=load_model();row={k:v['default'] for k,v in meta['schema'].items()};row.update(change)
    with pytest.raises(ValueError):validate_features(pd.DataFrame([row]),meta['schema'])


def test_model_version_mismatch_fails_before_loading():
    with pytest.raises(RuntimeError,match='scikit-learn'):
        validate_model_versions({'versions':{'scikit-learn':'0.0.0'}})


def fail(*args,**kwargs):raise RuntimeError('Provider outage')


def test_interview_provider_outage_falls_back(monkeypatch):
    monkeypatch.setattr('src.interview.question_generator.complete',fail)
    monkeypatch.setattr('src.interview.response_analyzer.complete',fail)
    assert 'Local fallback' in analyze_response({'topic':'general'},'An example project',True)['method']
    questions=generate_questions({'skills':[]},{'job_title':'Engineer'},{},True)
    assert questions and all('Local fallback' in q['generation_mode'] for q in questions)


@pytest.mark.parametrize('field,value',[('important_missing_concepts',4),('concepts_demonstrated','bad'),('relevant_examples',False)])
def test_invalid_interview_response_falls_back(monkeypatch,field,value):
    result=analyze_response({'topic':'general'},'An example project');result[field]=value
    monkeypatch.setattr('src.interview.response_analyzer.complete',lambda *a:json.dumps(result))
    assert 'Local fallback' in analyze_response({'topic':'general'},'An example project',True)['method']


def policy_source(monkeypatch):
    source={'text':'Medical leave requires manager approval. Emergency requests need HR review.','section':'Medical leave','document_name':'policy.pdf','page_number':1}
    monkeypatch.setattr('src.rag.policy_agent.retrieve',lambda *a:([source],{'backend':'lexical'}))
    return source


def test_valid_quote_cannot_launder_fabricated_policy_claim(monkeypatch):
    source=policy_source(monkeypatch)
    monkeypatch.setattr('src.rag.policy_agent.complete',lambda *a:json.dumps({'supported':True,'claims':[{'text':'Leave is automatically approved','source_id':1,'quote':'Medical leave requires manager approval.'}]}))
    result=answer_question('medical leave',use_llm=True)
    assert 'automatically approved' not in result['answer'] and source['text'] in result['answer']


def test_policy_outage_keeps_evidence(monkeypatch):
    source=policy_source(monkeypatch);monkeypatch.setattr('src.rag.policy_agent.complete',fail)
    result=answer_question('medical leave',use_llm=True)
    assert 'fallback' in result['mode'] and source['text'] in result['answer']


def test_unknown_policy_topic_abstains_despite_related_hits(monkeypatch):
    policy_source(monkeypatch)
    assert answer_question('medical leave cryptocurrency reimbursement')['mode']=='abstention'


@pytest.mark.parametrize('payload',[{}, {'choices':[]}, {'choices':[{'message':{'content':None}}]}])
def test_malformed_provider_transport_is_sanitized(monkeypatch,payload):
    from src.utils.llm import complete
    for key,value in {'LLM_PROVIDER':'openai','LLM_MODEL':'test','LLM_API_KEY':'test-only'}.items():monkeypatch.setenv(key,value)
    class Response:
        def raise_for_status(self):pass
        def json(self):return payload
    monkeypatch.setattr('src.utils.llm.requests.post',lambda *a,**k:Response())
    with pytest.raises(RuntimeError,match='no response was used'):complete('system','user')


@pytest.mark.parametrize('artifact',['chunks.json','index.faiss','lexical_vectorizer.joblib'])
def test_corrupt_index_rebuilds(tmp_path,artifact):
    dest=tmp_path/'index';ensure_policy_index(POLICIES,dest,backend='lexical')
    (dest/artifact).write_bytes(b'corrupt')
    ensure_policy_index(POLICIES,dest,backend='lexical')
    assert validate_index(dest)['documents']==6


def test_index_settings_and_concurrent_initialization(tmp_path):
    dest=tmp_path/'index'
    with ThreadPoolExecutor(3) as pool:
        results=list(pool.map(lambda _:ensure_policy_index(POLICIES,dest,backend='lexical'),range(3)))
    assert len({r['created'] for r in results})==1
    changed=ensure_policy_index(POLICIES,dest,backend='lexical',chunk_size=70,chunk_overlap=10)
    assert changed['chunk_size_words']==70
    assert search('medical leave',folder=dest,min_similarity=.05)[0]


def test_failed_rebuild_preserves_old_index(tmp_path,monkeypatch):
    dest=tmp_path/'index';build_index(POLICIES,dest,backend='lexical')
    before=(dest/'index.faiss').read_bytes()
    monkeypatch.setattr('src.rag.vector_store._write_index',fail)
    with pytest.raises(RuntimeError):build_index(POLICIES,dest,backend='lexical')
    assert (dest/'index.faiss').read_bytes()==before
    validate_index(dest)


@pytest.mark.semantic
def test_semantic_chunks_fit_real_encoder_and_keep_tail():
    from src.rag.chunker import fit_semantic_chunks
    from src.utils.embeddings import get_encoder,encode
    encoder=get_encoder()
    source={'chunk_id':'original','section':'Expenses','text':'Policy introduction '*250+'Reimbursement requires approval.','page_number':3,'document_name':'policy.pdf'}
    chunks=fit_semantic_chunks([source],encoder.tokenizer,encoder.max_seq_length)
    texts=[c['section']+' '+c['text'] for c in chunks]
    assert len(chunks)>1 and chunks[-1]['text'].endswith('Reimbursement requires approval.')
    assert all(len(encoder.tokenizer.encode(t))<=encoder.max_seq_length for t in texts)
    assert all(c['page_number']==3 for c in chunks)
    assert encode(texts).shape==(len(chunks),384)


def test_unrepresentable_heading_rejected():
    from src.rag.chunker import fit_semantic_chunks
    class Tokenizer:
        def encode(self,text,**kwargs):return text.split()+['CLS','SEP']
    with pytest.raises(ValueError,match='token budget'):
        fit_semantic_chunks([{'section':'Heading too long','text':'word','chunk_id':'id'}],Tokenizer(),3)


def test_upload_failure_cleanup_and_safe_delete(tmp_path,monkeypatch):
    import src.rag.uploads as uploads
    monkeypatch.setattr(uploads,'SESSION_ROOT',tmp_path/'sessions')
    monkeypatch.setattr(uploads,'build_index',fail)
    with pytest.raises(RuntimeError):uploads.build_session_index([],'lexical')
    assert list(uploads.SESSION_ROOT.iterdir())==[]
    with pytest.raises(ValueError):uploads.remove_session_index(tmp_path/'unrelated'/'index')


def test_upload_limits_and_duplicates():
    from src.rag.uploads import build_session_index
    a=BytesIO(b'pdf');a.name='same.pdf'
    with pytest.raises(ValueError,match='Duplicate'):build_session_index([a,a],'lexical')
    with pytest.raises(ValueError,match='20 policies'):build_session_index([a]*21,'lexical')


def test_policy_offline_controls_and_submitted_question(monkeypatch):
    monkeypatch.setattr('src.rag.bootstrap.ensure_policy_index',fail)
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run().switch_page('pages/3_HR_Policy_Assistant.py').run()
    assert app.selectbox[0].options==['semantic','lexical'] and not app.error
    app.selectbox[0].set_value('lexical').run();app.button[0].click().run()
    # Session index is now usable despite unavailable bundled setup.
    retrieve=next(b for b in app.button if b.label=='Retrieve policy evidence')
    retrieve.click().run()
    original=app.session_state['policy_result']['submitted_query']
    app.text_area[0].set_value('A changed question').run()
    assert app.session_state['policy_result']['submitted_query']==original
    assert any('previous submission' in w.value for w in app.warning)
    assert not app.exception and not app.error


def test_stale_recruitment_inputs_are_labeled():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run().switch_page('pages/1_Recruitment_Intelligence.py').run()
    app.selectbox[0].set_value('lexical').run();app.button[0].click().run()
    app.text_area[0].set_value('Role: SQL Engineer\nMandatory Skills: SQL').run()
    assert any('previous analysis' in w.value for w in app.warning)


def test_auth_hash_rate_limit_and_roles():
    from src.utils.access import password_hash,verify_password,authenticate,allowed_page
    hashed=password_hash('test passphrase')
    assert verify_password('test passphrase',hashed) and not verify_password('wrong',hashed)
    accounts={'reviewer-test':{'password_hash':hashed,'role':'reviewer'}}
    for _ in range(5):assert authenticate('reviewer-test','wrong',accounts,now=100) is None
    assert authenticate('reviewer-test','test passphrase',accounts,now=101) is None
    assert authenticate('reviewer-test','test passphrase',accounts,now=401)=='reviewer'
    assert not allowed_page('viewer','pages/2_Interview_Agent.py')
    assert allowed_page('viewer','pages/5_Workforce_Dashboard.py')


def test_confidential_mode_fails_closed(monkeypatch):
    monkeypatch.setenv('WORKFORCE_DATA_MODE','confidential')
    monkeypatch.setenv('WORKFORCE_AUTH_ENABLED','false')
    app=AppTest.from_file(str(ROOT/'app.py')).run()
    assert any('Confidential mode requires' in e.value for e in app.error)
    assert not app.exception


def test_enabled_auth_requires_configured_accounts(monkeypatch):
    monkeypatch.setenv('WORKFORCE_AUTH_ENABLED','true')
    app=AppTest.from_file(str(ROOT/'app.py')).run()
    assert app.error and not app.exception


def test_viewer_login_direct_page_denial_and_logout(monkeypatch):
    from src.utils.access import password_hash
    monkeypatch.setenv('WORKFORCE_AUTH_ENABLED','true')
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90)
    app.secrets['workforce_users']={'viewer-ui':{'role':'viewer','password_hash':password_hash('demo-secret')}}
    app.run()
    app.text_input[0].set_value('viewer-ui');app.text_input[1].set_value('demo-secret')
    app.button[0].click().run()
    assert app.session_state['access_identity']['role']=='viewer'
    assert not app.error
    app.session_state['recruitment_records']=[{'private':'test'}]
    next(b for b in app.sidebar.button if b.label=='Sign out').click().run()
    assert 'access_identity' not in app.session_state and 'recruitment_records' not in app.session_state
    direct=AppTest.from_file(str(ROOT/'pages/2_Interview_Agent.py'),default_timeout=90)
    direct.secrets['workforce_users']=app.secrets['workforce_users']
    direct.run()
    direct.text_input[0].set_value('viewer-ui');direct.text_input[1].set_value('demo-secret')
    direct.button[0].click().run()
    assert any('does not permit' in e.value for e in direct.error)


def test_dashboard_department_filter():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run().switch_page('pages/5_Workforce_Dashboard.py').run()
    total=int(app.metric[0].value)
    app.multiselect[0].set_value([app.multiselect[0].options[0]]).run()
    assert 0<int(app.metric[0].value)<total and app.metric[1].value=='1'
    assert not app.exception and not app.error


def test_environment_chunk_settings_are_applied(monkeypatch,tmp_path):
    monkeypatch.setenv('RAG_CHUNK_SIZE','65');monkeypatch.setenv('RAG_CHUNK_OVERLAP','10')
    meta=ensure_policy_index(POLICIES,tmp_path/'index',backend='lexical')
    assert meta['chunk_size_words']==65 and meta['chunk_overlap_words']==10
