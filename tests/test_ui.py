from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from src.utils.config import ROOT

@pytest.mark.parametrize('page',['app.py','pages/5_Workforce_Dashboard.py','pages/1_Recruitment_Intelligence.py','pages/2_Interview_Agent.py','pages/3_HR_Policy_Assistant.py','pages/4_Attrition_Intelligence.py','pages/6_Skill_Graph.py','pages/7_Model_Performance.py','pages/8_Project_Information.py'])
def test_page_render(page):
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run()
    if page!='app.py': app.switch_page(page).run()
    assert not app.exception,list(app.exception)
    assert not app.error,[x.value for x in app.error]

@pytest.mark.semantic
def test_recruitment_button():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run().switch_page('pages/1_Recruitment_Intelligence.py').run()
    app.button[0].click().run();assert not app.exception;assert not app.error
    assert len(app.session_state['recruitment_records'])==2

def test_manual_form():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run().switch_page('pages/4_Attrition_Intelligence.py').run()
    app.radio[0].set_value('Manual entry').run();app.button[0].click().run()
    assert not app.exception and not app.error
    assert len(app.session_state['latest_attrition_predictions'])==1

@pytest.mark.semantic
def test_recruitment_to_interview_ui():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run().switch_page('pages/1_Recruitment_Intelligence.py').run()
    app.button[0].click().run()
    app.switch_page('pages/2_Interview_Agent.py').run()
    app.button[0].click().run()
    app.text_area[0].set_value('I used vector embeddings, chunking and retrieval to supply context with citations. I evaluated recall on test queries.')
    app.button[1].click().run()
    assert not app.exception and not app.error
    assert len(app.session_state['interview_reports'])==1

@pytest.mark.semantic
def test_policy_retrieval_ui():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run().switch_page('pages/3_HR_Policy_Assistant.py').run()
    app.button[1].click().run()
    assert not app.exception and not app.error
    assert len(app.session_state['policy_result']['evidence'])>0
