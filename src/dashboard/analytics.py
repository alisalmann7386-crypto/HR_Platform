import pandas as pd
from src.utils.config import DATA, IBM, REPORTS
from src.attrition.preprocessing import load_data
from src.attrition.predict import predict_batch
from src.utils.validators import require_columns

def load_workforce():
    profiles=load_data(IBM).drop(columns=['Gender','Age','MaritalStatus'],errors='ignore')
    tables={k:pd.read_csv(DATA/'workforce'/f'{k}.csv') for k in ['employee_skills','performance','attendance','training','role_skill_requirements']}
    for key in ['employee_skills','performance','attendance','training']:
        if not tables[key].Employee_ID.isin(profiles.Employee_ID).all():raise ValueError(f'{key}: unknown Employee_ID')
    unified=profiles.copy()
    for key in ['performance','attendance','training']:
        table=tables[key]
        if table.Employee_ID.duplicated().any():raise ValueError(f'{key}: expected one summary row per employee')
        unified=unified.merge(table.drop(columns='Synthetic',errors='ignore'),on='Employee_ID',how='left',validate='one_to_one')
    predictions=predict_batch(profiles)
    from src.attrition.predict import load_model
    from src.attrition.explain import contributions
    from src.utils.config import MODELS
    import numpy as np
    pipe,meta=load_model()
    vals,names=contributions(pipe,profiles[meta['features']],pd.read_csv(MODELS/'shap_background.csv'))
    predictions['Top_Model_Signals']=['; '.join(names[np.argsort(np.abs(row))[-3:][::-1]]) for row in vals]
    unified=unified.merge(predictions,on='Employee_ID',validate='one_to_one')
    return unified,tables

def department_summary(df):
    return df.assign(Elevated=df.Risk_Band.eq('Elevated').astype(int)).groupby('Department').agg(Employees=('Employee_ID','nunique'),Elevated_Signals=('Elevated','sum'),Mean_Model_Probability=('Attrition_Probability','mean'),Synthetic_Training_Hours=('Training_Hours','mean'),Synthetic_Attendance_Rate=('Attendance_Rate','mean'),Synthetic_Performance_Score=('Performance_Score','mean')).reset_index()
