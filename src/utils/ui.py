import streamlit as st
import pandas as pd
from src.utils.config import MODELS, DATA, REPORTS
from src.utils.helpers import read_json


def title(name, description):
    st.markdown(
        '<span class="wf-badge">WORKFORCEAI · HUMAN REVIEW</span>',
        unsafe_allow_html=True,
    )
    st.title(name)
    st.caption(description)
    st.caption("Synthetic demo data · inspect evidence before taking any HR action")


def guard(function):
    try:
        function()
    except Exception as exc:
        st.error(f"{type(exc).__name__}: {exc}")
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
