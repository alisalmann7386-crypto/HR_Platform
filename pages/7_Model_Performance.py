import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.metrics import roc_curve,precision_recall_curve
from src.utils.ui import title,guard,model
from src.utils.config import REPORTS
from src.utils.helpers import read_json

def main():
    title('Model Performance','Real saved experiments; model and threshold selection use validation only.')
    _,meta=model();st.write('Selected model: **'+meta['model_name']+'**');st.caption(meta['selection_criterion']+'; '+meta['threshold_criterion'])
    metrics=meta['test_metrics']
    for col,name in zip(st.columns(5),['precision','recall','f1','roc_auc','pr_auc']):col.metric('Test '+name,f'{metrics[name]:.3f}')
    st.caption('PR-AUC is reported as average precision. Test set: '+str(meta['split_sizes']['test'])+' records. Estimates are uncertain on this small synthetic dataset.')
    st.subheader('Four-model comparison — validation at threshold 0.50');st.dataframe(pd.read_csv(REPORTS/'model_comparison.csv'),hide_index=True)
    st.subheader('Training-only five-fold cross-validation');st.dataframe(pd.read_csv(REPORTS/'cross_validation.csv'),hide_index=True)
    st.caption('Each metric includes mean and standard deviation. Preprocessing and any SMOTE are fitted within each training fold.')
    table=pd.read_csv(REPORTS/'threshold_analysis.csv');st.plotly_chart(px.line(table,x='threshold',y=['precision','recall','f1'],title='Validation threshold trade-offs'),use_container_width=True)
    st.caption(f'Selected threshold: {meta["threshold"]:.3f}. The fitted pipeline was not refit after selection, preserving the selected probability function.')
    a,b=st.columns(2)
    with a:st.plotly_chart(px.imshow(metrics['confusion_matrix'],x=['Predicted No','Predicted Yes'],y=['Actual No','Actual Yes'],text_auto=True,title='Final test confusion matrix'),use_container_width=True)
    pred=pd.read_csv(REPORTS/'test_predictions.csv');fpr,tpr,_=roc_curve(pred.Actual,pred.Attrition_Probability);precision,recall,_=precision_recall_curve(pred.Actual,pred.Attrition_Probability)
    with b:st.plotly_chart(px.line(x=fpr,y=tpr,labels={'x':'False-positive rate','y':'True-positive rate'},title='Test ROC curve'),use_container_width=True)
    st.plotly_chart(px.line(x=recall,y=precision,labels={'x':'Recall','y':'Precision'},title='Test precision–recall curve'),use_container_width=True)
    importance=pd.read_csv(REPORTS/'global_shap.csv').head(15)
    st.plotly_chart(px.bar(importance.sort_values('Mean_Absolute_SHAP_LogOdds'),x='Mean_Absolute_SHAP_LogOdds',y='Feature',orientation='h',title='Selected model: global SHAP over held-out records'),use_container_width=True)
    if (REPORTS/'weighted_lightgbm_shap.csv').exists():
        with st.expander('LightGBM TreeSHAP experiment (training records)'):
            imp=pd.read_csv(REPORTS/'weighted_lightgbm_shap.csv').head(15);st.plotly_chart(px.bar(imp,x='Mean_Absolute_SHAP_LogOdds',y='Feature',orientation='h'),use_container_width=True)
            st.caption('This explains the weighted LightGBM experiment, not the selected inference model.')
    st.subheader('Reliability and test-set uncertainty')
    calibration=REPORTS/'calibration_uncertainty.json';bins=REPORTS/'reliability_bins.csv'
    if calibration.exists() and bins.exists():
        detail=read_json(calibration);curve=pd.read_csv(bins)
        fig=px.scatter(curve,x='mean_probability',y='observed_rate',size='count',hover_data=['count'],
                       labels={'mean_probability':'Mean model estimate','observed_rate':'Observed attrition fraction'},
                       title='Held-out reliability (five quantile bins)')
        fig.add_shape(type='line',x0=0,y0=0,x1=1,y1=1,line=dict(color='#64748b',dash='dash'))
        fig.update_xaxes(range=[0,1]);fig.update_yaxes(range=[0,1]);st.plotly_chart(fig,use_container_width=True)
        st.dataframe(pd.DataFrame([{'Metric':k,'Lower 95%':v['lower_95'],'Upper 95%':v['upper_95']}
                                   for k,v in detail['intervals'].items()]),hide_index=True)
        st.caption(f"Descriptive percentile bootstrap over {detail['rows']} held-out rows ({detail['positive_rows']} positives). These ranges do not correct dataset bias or make predictions calibrated. No model or threshold was selected using test data.")
    else:st.info('Run python scripts/evaluate_calibration.py to create the descriptive reliability report.')
    with st.expander('Reproducibility metadata'):st.json(meta)
guard(main)
