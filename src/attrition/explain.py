import numpy as np
import pandas as pd
import shap

def contributions(pipeline, frame, background=None):
    pre = pipeline.named_steps['preprocess']; model = pipeline.named_steps['model']
    X = pre.transform(frame)
    if hasattr(model, 'booster_'):
        explainer = shap.TreeExplainer(model, model_output='raw')
    else:
        if background is None: raise ValueError('Training background required for logistic SHAP.')
        explainer = shap.LinearExplainer(model, pre.transform(background))
    result = explainer(X)
    values = np.asarray(result.values)
    if values.ndim == 3: values = values[:,:,1]
    names = pre.get_feature_names_out()
    return values, names

def local_explanation(pipeline, frame, background=None):
    values, names = contributions(pipeline, frame, background)
    return pd.DataFrame({'Feature':names,'SHAP_log_odds':values[0]}).assign(Direction=lambda d:np.where(d.SHAP_log_odds>=0,'Increases model score','Decreases model score')).sort_values('SHAP_log_odds',key=abs,ascending=False)
