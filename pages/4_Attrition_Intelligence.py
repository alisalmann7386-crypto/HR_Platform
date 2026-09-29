import streamlit as st
import pandas as pd
import plotly.express as px
from src.utils.ui import title,guard,model,download_csv
from src.utils.config import IBM,MODELS,DATA
from src.attrition.preprocessing import load_data
from src.attrition.predict import predict_batch
from src.attrition.explain import local_explanation

def main():
    title('Attrition Intelligence','Inspect an uncalibrated model estimate and its contributions. Bands are display categories, not employment decisions.')
    pipe,meta=model();st.caption(f'Selected: {meta["model_name"]} | Operating threshold: {meta["threshold"]:.3f} | No prediction horizon is available.')
    mode=st.radio('Input mode',['Select demo employee','Manual entry','CSV upload'],horizontal=True)
    frame=None
    if mode=='Select demo employee':
        df=load_data(IBM);eid=st.selectbox('Employee ID',df.Employee_ID);frame=df[df.Employee_ID==eid]
        st.dataframe(frame[['Employee_ID','Department','JobRole','OverTime','JobSatisfaction','MonthlyIncome']],hide_index=True)
    elif mode=='Manual entry':
        st.caption('Defaults are training medians/modes. Edit all applicable fields; this is not a real employee profile.')
        with st.form('employee_form'):
            eid=st.text_input('Employee ID','MANUAL-001');values={};columns=st.columns(3)
            for i,(name,spec) in enumerate(meta['schema'].items()):
                with columns[i%3]:
                    if spec['type']=='numeric':values[name]=st.number_input(name,min_value=0.,value=spec['default'],step=1.)
                    else:values[name]=st.selectbox(name,spec['categories'],index=spec['categories'].index(spec['default']))
            if st.form_submit_button('Predict manual entry'):st.session_state['manual_employee']=pd.DataFrame([dict(values,Employee_ID=eid)])
        frame=st.session_state.get('manual_employee')
    else:
        st.download_button('Download batch CSV template',(DATA/'processed/employee_upload_example.csv').read_bytes(),'employee_upload_example.csv','text/csv')
        uploaded=st.file_uploader('Employee CSV',type='csv')
        if uploaded:frame=pd.read_csv(uploaded)
        st.caption('All model feature columns are required; missing cells can be imputed. Protected fields and extra columns are ignored. Unknown category values are reported for correction.')
    if frame is not None:
        result=predict_batch(frame,pipe,meta);st.dataframe(result,hide_index=True);download_csv(result,'attrition_predictions.csv')
        st.session_state['latest_attrition_predictions']=result
        st.caption('Batch uploads remain session-local and do not replace the bundled dashboard workforce.')
        if len(result):
            idx=st.selectbox('Explain prediction',range(len(result)),format_func=lambda i:result.iloc[i].Employee_ID)
            row=frame.iloc[[idx]][meta['features']];bg=pd.read_csv(MODELS/'shap_background.csv')
            explanation=local_explanation(pipe,row,bg)
            st.metric('Predicted attrition probability',f'{result.iloc[idx].Attrition_Probability:.1%}');st.caption('Uncalibrated output on a synthetic dataset; not a real-world forecast.')
            fig=px.bar(explanation.head(15).sort_values('SHAP_log_odds'),x='SHAP_log_odds',y='Feature',orientation='h',color='Direction',color_discrete_map={'Increases model score':'#C2410C','Decreases model score':'#2563EB'})
            st.plotly_chart(fig,use_container_width=True);st.caption('SHAP contributions are in log-odds units, not percentage points. They explain model behavior, not causation. Positive values increase the model score.')
            download_csv(explanation,'employee_shap.csv')
guard(main)
