import streamlit as st
import pandas as pd
import plotly.express as px
from src.utils.ui import title,guard,model,download_csv
from src.utils.config import IBM,MODELS,DATA
from src.attrition.preprocessing import load_data
from src.attrition.predict import predict_batch
from src.attrition.explain import local_explanation, contributions
import numpy as np

GROUPS={
 'Employee profile':['Education','EducationField','DistanceFromHome','NumCompaniesWorked'],
 'Job information':['Department','JobRole','JobLevel','JobInvolvement','BusinessTravel'],
 'Satisfaction':['EnvironmentSatisfaction','JobSatisfaction','RelationshipSatisfaction','WorkLifeBalance'],
 'Compensation':['MonthlyIncome','MonthlyRate','DailyRate','HourlyRate','PercentSalaryHike','StockOptionLevel'],
 'Experience':['TotalWorkingYears','YearsAtCompany','YearsInCurrentRole','YearsSinceLastPromotion','YearsWithCurrManager','TrainingTimesLastYear'],
 'Work conditions':['OverTime','PerformanceRating']}


def manual_form(meta):
    st.caption('Defaults are training medians/modes. Review every applicable input before analysis.')
    with st.form('employee_form'):
        eid=st.text_input('Employee ID','MANUAL-001');values={}
        for group,fields in GROUPS.items():
            with st.expander(group,expanded=group in ('Employee profile','Job information')):
                columns=st.columns(3)
                for i,name in enumerate(fields):
                    if name not in meta['schema']:continue
                    spec=meta['schema'][name]
                    with columns[i%3]:
                        if spec['type']=='numeric':values[name]=st.number_input(name,min_value=0.,value=float(spec['default']),step=1.)
                        else:values[name]=st.selectbox(name,spec['categories'],index=spec['categories'].index(spec['default']))
        if st.form_submit_button('Analyze Attrition Signal'):
            st.session_state['manual_employee']=pd.DataFrame([dict(values,Employee_ID=eid)])
    return st.session_state.get('manual_employee')


def show_prediction(frame,pipe,meta,batch=False):
    with st.spinner('Running saved model and preparing explanation…'):
        result=predict_batch(frame,pipe,meta)
    if batch:
        if len(result):
            background=pd.read_csv(MODELS/'shap_background.csv')
            values,names=contributions(pipe,frame[meta['features']],background)
            result['Top_Model_Signals']=['; '.join(names[np.argsort(np.abs(row))[-3:][::-1]]) for row in values]
        cols=st.columns(4)
        for col,(label,count) in zip(cols,[('Processed',len(result)),('Low',sum(result.Risk_Band=='Low')),
                 ('Moderate',sum(result.Risk_Band=='Moderate')),('Elevated',sum(result.Risk_Band=='Elevated'))]):
            col.metric(label,int(count))
    st.dataframe(result,hide_index=True);download_csv(result,'attrition_predictions.csv')
    st.session_state['latest_attrition_predictions']=result
    if len(result):
        idx=st.selectbox('Explain prediction',range(len(result)),format_func=lambda i:result.iloc[i].Employee_ID,key='explain_batch' if batch else 'explain_single')
        row=frame.iloc[[idx]][meta['features']];bg=pd.read_csv(MODELS/'shap_background.csv')
        explanation=local_explanation(pipe,row,bg)
        st.metric('Model estimate',f'{result.iloc[idx].Attrition_Probability:.1%}')
        st.caption('Uncalibrated estimate from synthetic historical data, with no defined forecast horizon.')
        a,b=st.columns(2)
        with a:
            st.subheader('Factors increasing model score')
            st.dataframe(explanation[explanation.SHAP_log_odds>0].head(8),hide_index=True)
        with b:
            st.subheader('Factors decreasing model score')
            st.dataframe(explanation[explanation.SHAP_log_odds<0].head(8),hide_index=True)
        fig=px.bar(explanation.head(15).sort_values('SHAP_log_odds'),x='SHAP_log_odds',y='Feature',orientation='h',color='Direction',
                   color_discrete_map={'Increases model score':'#F59E0B','Decreases model score':'#3B82F6'})
        st.plotly_chart(fig,use_container_width=True)
        st.caption('SHAP contributions are log-odds changes in the model score. They describe model behavior and do not establish causes.')
        download_csv(explanation,'employee_shap.csv')


def main():
    title('Attrition Intelligence','Inspect saved model estimates and their feature contributions for human review.')
    with st.spinner('Loading trained attrition model…'):
        pipe,meta=model()
    st.caption(f"Selected: {meta['model_name']} · Operating threshold: {meta['threshold']:.3f}")
    individual,batch=st.tabs(['Individual Prediction','Batch Prediction'])
    with individual:
        mode=st.radio('Individual input',['Select demo employee','Manual entry'],horizontal=True)
        if mode=='Select demo employee':
            df=load_data(IBM);eid=st.selectbox('Employee ID',df.Employee_ID);frame=df[df.Employee_ID==eid]
            st.dataframe(frame[['Employee_ID','Department','JobRole','OverTime','JobSatisfaction','MonthlyIncome']],hide_index=True)
        else:frame=manual_form(meta)
        if frame is not None:show_prediction(frame,pipe,meta)
    with batch:
        st.download_button('Download CSV template',(DATA/'processed/employee_upload_example.csv').read_bytes(),'employee_upload_example.csv','text/csv')
        uploaded=st.file_uploader('Employee CSV',type='csv')
        st.caption('Required model features must be present. Extra columns and protected fields are ignored. This upload remains session-local.')
        if uploaded:
            frame=pd.read_csv(uploaded)
            if len(frame)>500:raise ValueError('For interactive review, upload at most 500 records per batch.')
            show_prediction(frame,pipe,meta,batch=True)
    st.info('This statistical signal must not be used as an automatic employment decision.')


guard(main)
