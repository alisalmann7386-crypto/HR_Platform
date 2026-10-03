import streamlit as st
import pandas as pd
import plotly.express as px
from src.utils.ui import title,guard,workforce
from src.utils.config import INDEX,DATA
from src.utils.helpers import read_json
from src.skills.skill_gap import skill_gaps
from src.dashboard.analytics import department_summary
from src.dashboard.insights import workforce_insights

def main():
    title('Workforce Intelligence Dashboard','Employee records + model signals + skills + performance + attendance + training')
    df,tables=workforce();departments=st.multiselect('Departments',sorted(df.Department.unique()))
    if departments:df=df[df.Department.isin(departments)]
    skills=tables['employee_skills'];skills=skills[skills.Employee_ID.isin(df.Employee_ID)]
    requirements=tables['role_skill_requirements'];requirements=requirements[requirements.Role.isin(skills.Job_Role.unique())]
    gaps=skill_gaps(skills,requirements)
    records=st.session_state.get('recruitment_records',[])
    counts=[('Total employees',len(df)),('Departments',df.Department.nunique()),('Elevated signals',int(df.Risk_Band.eq('Elevated').sum())),('Candidates analyzed',len(records)),('Open demo roles',len(list((DATA/'jobs').glob('*.txt')))),('Largest skill gap',int(gaps.Gap.max()) if len(gaps) else 0),('Policies indexed',read_json(INDEX/'metadata.json')['documents'] if (INDEX/'metadata.json').exists() else 0)]
    for col,(label,value) in zip(st.columns(4),counts[:4]):col.metric(label,value)
    for col,(label,value) in zip(st.columns(3),counts[4:]):col.metric(label,value)
    st.caption('Bundled workforce includes historical records with known Attrition labels; all-record predictions are demonstration inference, not held-out evaluation or a current active employee census.')
    a,b=st.columns(2)
    with a:st.plotly_chart(px.histogram(df,x='Attrition_Probability',nbins=25,title='Model estimate distribution'),use_container_width=True)
    with b:st.plotly_chart(px.histogram(df,x='Department',color='Risk_Band',title='Retention-attention bands by department'),use_container_width=True)
    a,b=st.columns(2)
    with a:st.plotly_chart(px.histogram(df,x='OverTime',color='Attrition',barmode='group',title='Recorded overtime vs historical attrition'),use_container_width=True)
    with b:st.plotly_chart(px.histogram(df,x='JobSatisfaction',color='Attrition',barmode='group',title='Recorded job satisfaction vs historical attrition'),use_container_width=True)
    a,b=st.columns(2)
    with a:
        top=skills.groupby('Skill').Employee_ID.nunique().sort_values(ascending=False).head(12).rename('Employees').reset_index()
        st.plotly_chart(px.bar(top,x='Employees',y='Skill',orientation='h',title='Common skills — synthetic'),use_container_width=True)
    with b:st.plotly_chart(px.bar(gaps.sort_values('Gap',ascending=False).head(12),x='Skill',y='Gap',color='Role',title='Largest role-skill gaps — synthetic'),use_container_width=True)
    a,b=st.columns(2)
    with a:st.plotly_chart(px.pie(df,names='Department',title='Employees by department'),use_container_width=True)
    with b:st.plotly_chart(px.bar(gaps.groupby('Role',as_index=False).Coverage.mean(),x='Role',y='Coverage',title='Mean role skill coverage — synthetic'),use_container_width=True)
    if records:st.plotly_chart(px.histogram(pd.DataFrame([r['analysis'] for r in records]),x='job_relevance_score',title='Session recruitment relevance scores'),use_container_width=True)
    st.subheader('Multi-source department view');summary=department_summary(df);st.dataframe(summary,hide_index=True)
    st.subheader('AI Workforce Insights')
    for insight in workforce_insights(summary,gaps,skills):
        with st.container(border=True):st.write(insight)
    st.caption('These observations describe model patterns and synthetic skill capacity; investigate context before any HR action.')
    with st.expander('Common model signals among elevated records'):
        signals=df.loc[df.Risk_Band.eq('Elevated'),'Top_Model_Signals'].str.split('; ').explode().value_counts().head(8)
        st.dataframe(signals.rename('Occurrences in top three contributions').reset_index(),hide_index=True)
        st.caption('Largest absolute contributions, not necessarily increasing contributions; associations in this model, not causes.')
    with st.expander('Joined employee records (auxiliary fields are synthetic)'):st.dataframe(df[['Employee_ID','Department','JobRole','Attrition_Probability','Risk_Band','Top_Model_Signals','Performance_Score','Attendance_Rate','Training_Hours','Courses_Completed']],hide_index=True)
    if st.button('Review workload and development policies'):
        st.session_state['policy_query']='What do the performance review and work from home policies say about workload and development support?';st.switch_page('pages/3_HR_Policy_Assistant.py')
    st.caption('No causal relationship is inferred between synthetic auxiliary fields and attrition. Skill targets describe future demo capacity, not real vacancies.')
guard(main)
