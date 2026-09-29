import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.metrics import roc_curve,precision_recall_curve
from src.utils.ui import title,guard,model
from src.utils.config import REPORTS

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
    with st.expander('Reproducibility metadata'):st.json(meta)
guard(main)
