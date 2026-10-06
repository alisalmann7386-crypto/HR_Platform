"""Shared HR workspace presentation, independent of navigation and data."""
from copy import deepcopy
from pathlib import Path
import plotly.io as pio
import streamlit as st


def apply_theme():
    theme = deepcopy(pio.templates['plotly_dark'])
    theme.layout.update(paper_bgcolor='#192220',plot_bgcolor='#192220',
        font=dict(color='#c9d7cc',family='Arial, sans-serif'),
        title=dict(font=dict(color='#edf3e6',size=17)),
        colorway=['#a8d5a2','#b8a5d4','#e5bc7b','#76bcc0','#d68d88','#8aa5d0'],
        coloraxis=dict(colorscale=[[0,'#294335'],[.5,'#699b79'],[1,'#d5e8af']]),
        xaxis=dict(gridcolor='#34463e'),yaxis=dict(gridcolor='#34463e'))
    pio.templates['workforce_dark']=theme
    pio.templates.default='workforce_dark'
    css=(Path(__file__).resolve().parents[2]/'assets/workforce.css').read_text()
    st.markdown(f'<style>{css}</style>',unsafe_allow_html=True)
