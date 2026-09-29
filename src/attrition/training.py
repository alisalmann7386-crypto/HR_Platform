import hashlib
import importlib.metadata
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from lightgbm import LGBMClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from src.attrition.preprocessing import load_data, features, split_data, preprocessor, EXCLUDED
from src.attrition.evaluation import evaluate
from src.attrition.thresholding import threshold_table, select_threshold
from src.attrition.explain import contributions
from src.utils.config import ROOT, MODELS, REPORTS
from src.utils.helpers import save_json, timestamp

def train(data, output=ROOT):
    output=Path(output); models=output/'models'; reports=output/'reports'
    models.mkdir(parents=True,exist_ok=True); reports.mkdir(parents=True,exist_ok=True)
    df=load_data(data); tr,va,te=split_data(df)
    Xtr,Xva,Xte=[features(x) for x in [tr,va,te]]
    ytr,yva,yte=[x.Attrition.eq('Yes').astype(int) for x in [tr,va,te]]
    print(f'Dataset loaded: {len(df)} rows. Target: Attrition. Distribution: {df.Attrition.value_counts().to_dict()}')
    print(f'Train: {len(tr)} Validation: {len(va)} Test: {len(te)}')
    common=dict(n_estimators=160,learning_rate=.035,num_leaves=15,max_depth=-1,min_child_samples=25,reg_lambda=2.,verbosity=-1,random_state=42,n_jobs=2,deterministic=True,force_col_wise=True)
    configurations={
        'Logistic Regression':(LogisticRegression(C=.3,max_iter=3000,random_state=42),False),
        'LightGBM':(LGBMClassifier(**common),False),
        'Weighted LightGBM':(LGBMClassifier(class_weight='balanced',**common),False),
        'SMOTE + LightGBM':(LGBMClassifier(**common),True)}
    results=[]; experiments=[]; fitted={}; cvrows=[]
    for name,(estimator,smote) in configurations.items():
        print('Training',name,flush=True)
        steps=[('preprocess',preprocessor(Xtr))]
        if smote: steps.append(('smote',SMOTE(random_state=42,k_neighbors=5)))
        steps.append(('model',estimator)); pipe=Pipeline(steps)
        cv=cross_validate(pipe,Xtr,ytr,cv=StratifiedKFold(5,shuffle=True,random_state=42),scoring={'roc_auc':'roc_auc','pr_auc':'average_precision','f1':'f1','recall':'recall','precision':'precision'},n_jobs=1,error_score='raise')
        cvrow={'model':name}
        for metric in ['roc_auc','pr_auc','f1','recall','precision']:
            cvrow[metric+'_mean']=float(np.mean(cv['test_'+metric]));cvrow[metric+'_std']=float(np.std(cv['test_'+metric]))
        cvrows.append(cvrow)
        pipe.fit(Xtr,ytr); fitted[name]=pipe
        joblib.dump(pipe,models/(name.lower().replace(' + ','_').replace(' ','_')+'.joblib'))
        metrics=evaluate(yva,pipe.predict_proba(Xva)[:,1])
        results.append({'model':name,'split':'validation','threshold':.5,**{k:v for k,v in metrics.items() if k!='confusion_matrix'}})
        experiments.append({'model':name,'parameters':estimator.get_params(),'smote':smote,'random_state':42,'training_size':len(tr),'validation_size':len(va),'test_size':len(te),'evaluation_split':'validation','timestamp':timestamp(),**metrics})
        print('Completed.',flush=True)
    comparison=pd.DataFrame(results)
    # Predeclared selection: validation average precision, tie by ROC-AUC.
    selected=comparison.sort_values(['pr_auc','roc_auc'],ascending=False).iloc[0]['model']
    pipe=fitted[selected]; table=threshold_table(yva,pipe.predict_proba(Xva)[:,1]); threshold=select_threshold(table)
    # Do not refit after threshold selection; keep the same probability function.
    test_p=pipe.predict_proba(Xte)[:,1]; final=evaluate(yte,test_p,threshold)
    schema={c:({'type':'numeric','min':float(Xtr[c].min()),'max':float(Xtr[c].max()),'default':float(Xtr[c].median())} if pd.api.types.is_numeric_dtype(Xtr[c]) else {'type':'categorical','categories':sorted(Xtr[c].dropna().unique().tolist()),'default':str(Xtr[c].mode()[0])}) for c in Xtr}
    metadata={'model_name':selected,'model_version':'1.0.0','dataset':Path(data).name,'dataset_sha256':hashlib.sha256(Path(data).read_bytes()).hexdigest(),'dataset_rows':len(df),'training_date':timestamp(),'features':list(Xtr.columns),'excluded_features':EXCLUDED,'schema':schema,'threshold':threshold,'selection_criterion':'Highest validation average precision, then ROC-AUC','threshold_criterion':'Maximum validation F1, then precision, then higher threshold','random_state':42,'split_sizes':{'train':len(tr),'validation':len(va),'test':len(te)},'probability_note':'Uncalibrated model estimates, not real-world departure likelihoods; no prediction horizon is provided by this dataset.','pr_auc_definition':'Average precision (step-wise PR integral)','band_edges':[threshold/2,threshold],'test_metrics':final,**{k:v for k,v in final.items() if k!='confusion_matrix'},'versions':{p:importlib.metadata.version(p) for p in ['scikit-learn','lightgbm','imbalanced-learn','shap','pandas','numpy']}}
    joblib.dump(pipe,models/'attrition_model.joblib');save_json(models/'attrition_metadata.json',metadata)
    Xtr.sample(min(100,len(Xtr)),random_state=42).to_csv(models/'shap_background.csv',index=False)
    comparison.to_csv(reports/'model_comparison.csv',index=False);comparison.to_csv(models/'model_comparison.csv',index=False)
    pd.DataFrame(cvrows).to_csv(reports/'cross_validation.csv',index=False)
    table.to_csv(reports/'threshold_analysis.csv',index=False);table.to_csv(models/'threshold_analysis.csv',index=False)
    save_json(reports/'experiments.json',experiments);save_json(reports/'test_metrics.json',final)
    save_json(reports/'split_manifest.json',{k:x.Employee_ID.tolist() for k,x in [('train',tr),('validation',va),('test',te)]})
    pd.DataFrame({'Employee_ID':te.Employee_ID,'Actual':yte,'Attrition_Probability':test_p,'Predicted':(test_p>=threshold).astype(int)}).to_csv(reports/'test_predictions.csv',index=False)
    values,names=contributions(pipe,Xte, Xtr.sample(100,random_state=42))
    pd.DataFrame({'Feature':names,'Mean_Absolute_SHAP_LogOdds':np.abs(values).mean(axis=0)}).sort_values('Mean_Absolute_SHAP_LogOdds',ascending=False).to_csv(reports/'global_shap.csv',index=False)
    values_lgb,names_lgb=contributions(fitted['Weighted LightGBM'],Xtr.head(200))
    pd.DataFrame({'Feature':names_lgb,'Mean_Absolute_SHAP_LogOdds':np.abs(values_lgb).mean(axis=0)}).sort_values('Mean_Absolute_SHAP_LogOdds',ascending=False).to_csv(reports/'weighted_lightgbm_shap.csv',index=False)
    from src.attrition.predict import predict_batch
    all_predictions=predict_batch(df,pipe,metadata)
    all_values,all_names=contributions(pipe,features(df),Xtr.sample(100,random_state=42))
    all_predictions['Top_Model_Signals']=['; '.join(all_names[np.argsort(np.abs(row))[-5:][::-1]]) for row in all_values]
    split_lookup={eid:k for k,group in [('train',tr),('validation',va),('test',te)] for eid in group.Employee_ID}
    all_predictions['Split']=df.Employee_ID.map(split_lookup)
    all_predictions['Purpose']='Historical synthetic demo; not a current workforce forecast'
    processed=output/'data/processed';processed.mkdir(parents=True,exist_ok=True)
    all_predictions.to_csv(processed/'attrition_predictions.csv',index=False)
    print(comparison.to_string(index=False)); print('Selected:',selected,'Threshold:',threshold)
    print('FINAL TEST RESULTS',final); print('Saved model:',models/'attrition_model.joblib')
    return metadata
