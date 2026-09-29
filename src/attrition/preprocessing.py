import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from src.utils.helpers import employee_ids
from src.utils.validators import require_columns

EXCLUDED = ['Attrition','EmployeeNumber','Employee_ID','EmployeeCount','Over18','StandardHours','Gender','Age','MaritalStatus']
def load_data(path):
    df = pd.read_csv(path)
    require_columns(df, ['Attrition','EmployeeNumber','Department','JobRole','MonthlyIncome','OverTime'])
    if df['Attrition'].isna().any() or not df['Attrition'].isin(['Yes','No']).all(): raise ValueError('Attrition must contain Yes/No only.')
    if df.duplicated().any(): raise ValueError('Duplicate rows detected; resolve before training.')
    df['Employee_ID'] = employee_ids(df)
    return df

def features(df): return df.drop(columns=EXCLUDED, errors='ignore')
def split_data(df):
    train, other = train_test_split(df, test_size=.30, stratify=df.Attrition, random_state=42)
    validation, test = train_test_split(other, test_size=.50, stratify=other.Attrition, random_state=42)
    return train, validation, test

def preprocessor(X):
    nums = X.select_dtypes(include='number').columns.tolist()
    cats = [c for c in X if c not in nums]
    return ColumnTransformer([
        ('numeric', Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]), nums),
        ('categorical',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('encode',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cats)
    ], verbose_feature_names_out=True)
