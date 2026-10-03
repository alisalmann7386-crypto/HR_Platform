import streamlit as st
import pandas as pd
import plotly.express as px
from src.utils.ui import title,guard,workforce,download_csv
from src.utils.config import DATA
from src.skills.skill_gap import skill_gaps,LEVELS
from src.skills.skill_graph import build_graph,plot_graph
from src.skills.recommendations import suggestions

def main():
    title('Workforce Skill Graph','Explore capabilities, role requirements and synthetic workforce-development scenarios.')
    _,tables=workforce();skills=tables['employee_skills'];requirements=tables['role_skill_requirements']
    with st.expander('Use alternative skills and role requirements CSVs'):
        uploaded=st.file_uploader('employee_skills.csv',type='csv');req=st.file_uploader('role_skill_requirements.csv',type='csv')
        if uploaded:skills=pd.read_csv(uploaded)
        if req:requirements=pd.read_csv(req)
    # Capacity is calculated on the complete selected dataset; graph filters never alter organizational demand.
    gaps=skill_gaps(skills,requirements)
    filters=st.columns(5);selection=skills.copy()
    for col,name in zip(filters,['Department','Employee_ID','Job_Role','Skill','Skill_Level']):
        with col:
            chosen=st.multiselect(name,sorted(skills[name].unique()))
            if chosen:selection=selection[selection[name].isin(chosen)]
    limit=st.slider('Maximum employees drawn',5,100,25)
    displayed_ids=sorted(selection.Employee_ID.unique())[:limit];selection=selection[selection.Employee_ID.isin(displayed_ids)]
    if len(selection):
        subset=requirements[requirements.Role.isin(selection.Job_Role.unique())]
        projects=pd.read_csv(DATA/'workforce/projects.csv');projects=projects[projects.Employee_ID.isin(displayed_ids)] if uploaded is None else None
        with st.spinner('Building employee–skill–role graph…'):
            G=build_graph(selection,subset,projects)
            figure=plot_graph(G)
        st.plotly_chart(figure,use_container_width=True)
        focus=st.selectbox('Inspect employee',displayed_ids)
        view=selection[selection.Employee_ID==focus]
        with st.container(border=True):
            st.write(f"**{focus}** · {view.Job_Role.iloc[0]} · {view.Department.iloc[0]}")
            st.write('Skills: '+', '.join(f'{r.Skill} ({r.Skill_Level})' for r in view.itertuples()))
        st.caption(f'Drawing {len(displayed_ids)} employees; graph cap is for readability only. Hover nodes; scroll to zoom.')
        with st.expander('Graph edge evidence'):st.dataframe(pd.DataFrame([{'Source':a,'Target':b,**v} for a,b,v in G.edges(data=True)]),hide_index=True)
    else:st.info('No employees match those graph filters.')
    st.subheader('Role-specific skill capacity');st.caption('Full input dataset, independent of graph display filters. Count distinct employees in the role who meet or exceed the required level. Employees can cover multiple skills; this is not a staffing allocation optimizer.')
    st.dataframe(gaps,hide_index=True);download_csv(gaps,'skill_gaps.csv')
    st.plotly_chart(px.bar(gaps.sort_values('Gap',ascending=False).head(15),x='Skill',y='Gap',color='Role'),use_container_width=True)
    for text in suggestions(gaps)[:8]:st.write('• '+text)
guard(main)
