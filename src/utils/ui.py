import streamlit as st
import logging
from pathlib import Path
from src.utils.config import ROOT
from src.utils.config import MODELS, DATA, REPORTS
from src.utils.helpers import read_json


def title(name, description):
    st.markdown(
        '<span class="wf-badge">PEOPLE OPERATIONS · EVIDENCE WORKSPACE</span>',
        unsafe_allow_html=True,
    )
    st.title(name)
    st.caption(description)
    st.caption("Human review required · demonstration datasets are labeled within each module")


def module_link(path, label):
    from src.utils.access import allowed_page
    if allowed_page(st.session_state.get('access_role','admin'),path):st.page_link(path,label=label)


def guard(function):
    from src.utils.access import require_access, allowed_page
    role=require_access(render_controls=False)
    page=Path(function.__code__.co_filename).resolve().relative_to(ROOT).as_posix()
    if not allowed_page(role,page):
        st.error('Your access role does not permit this module.')
        st.stop()
    try:
        function()
    except Exception as exc:
        if isinstance(exc,(ValueError,FileNotFoundError,RuntimeError)):
            st.error(str(exc))
        else:
            logging.getLogger(__name__).error('module_failure type=%s',type(exc).__name__)
            st.error('This module encountered an unexpected error. No result was produced.')
        st.info(
            "This module could not complete. Check the input and setup guidance above; "
            "other pages remain available."
        )


@st.cache_resource
def model():
    from src.attrition.predict import load_model
    return load_model()


@st.cache_data
def workforce():
    from src.dashboard.analytics import load_workforce
    return load_workforce()


def download_csv(df, name):
    st.download_button("Download " + name, df.to_csv(index=False), name, "text/csv")


def llm_toggle(key):
    from src.utils.llm import available
    enabled = st.checkbox(
        "Use configured LLM (sends this module’s submitted content to the provider)",
        key=key,
        disabled=not available(),
    )
    if not available():
        st.caption(
            "No LLM configured. Evidence extraction and local interview templates remain available."
        )
    return enabled
