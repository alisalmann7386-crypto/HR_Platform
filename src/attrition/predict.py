import importlib.metadata
import joblib
import numpy as np
import pandas as pd
from src.utils.config import MODELS
from src.utils.helpers import read_json, employee_ids
from src.utils.validators import validate_features

def validate_model_versions(metadata):
    for package in ['scikit-learn','lightgbm','imbalanced-learn']:
        expected=metadata.get('versions',{}).get(package)
        if expected and importlib.metadata.version(package)!=expected:
            raise RuntimeError(f'Model requires {package}=={expected}. Install requirements.txt before loading saved artifacts.')


def load_model():
    path=MODELS/'attrition_model.joblib'
    if not path.exists(): raise FileNotFoundError('Train first: python scripts/train_attrition.py --data data/attrition/WA_Fn-UseC_-HR-Employee-Attrition.csv')
    # Only load trusted locally trained joblib artifacts, never user uploads.
    metadata=read_json(MODELS/'attrition_metadata.json')
    validate_model_versions(metadata)
    return joblib.load(path),metadata
def predict_batch(df,pipeline=None,metadata=None):
    if pipeline is None: pipeline,metadata=load_model()
    X=validate_features(df,metadata['schema']);p=pipeline.predict_proba(X)[:,1]; t=metadata['threshold']
    if 'Employee_ID' in df:
        ids=df.Employee_ID.astype(str).str.strip()
        if df.Employee_ID.isna().any() or ids.eq('').any() or ids.duplicated().any(): raise ValueError('Employee_ID must be non-missing and unique.')
    elif 'EmployeeNumber' in df: ids=employee_ids(df)
    else: ids=pd.Series([f'UPLOAD-{i+1}' for i in range(len(df))],index=df.index)
    return pd.DataFrame({'Employee_ID':ids.to_numpy(),'Attrition_Probability':p,'Risk_Band':np.where(p>=t,'Elevated',np.where(p>=t/2,'Moderate','Low'))})
