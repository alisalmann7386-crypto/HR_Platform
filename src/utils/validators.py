import numpy as np
import pandas as pd

def require_columns(df, columns):
    missing = sorted(set(columns) - set(df.columns))
    if missing: raise ValueError('Missing columns: ' + ', '.join(missing))
    if df.empty: raise ValueError('No data rows found.')

INTEGER_DOMAINS = {
    'Education': range(1,6), 'JobLevel': range(1,6), 'StockOptionLevel': range(4),
    'PerformanceRating': range(1,5), **{k:range(1,5) for k in
    ['EnvironmentSatisfaction','JobInvolvement','JobSatisfaction','RelationshipSatisfaction','WorkLifeBalance']}}
COUNT_FIELDS = {'NumCompaniesWorked','TotalWorkingYears','TrainingTimesLastYear','YearsAtCompany',
                'YearsInCurrentRole','YearsSinceLastPromotion','YearsWithCurrManager'}


def feature_range_warnings(df,schema):
    return [f'{c}: some values are outside the training range; interpret estimates cautiously.'
            for c,spec in schema.items() if spec['type']=='numeric'
            and ((df[c]<spec['min']) | (df[c]>spec['max'])).any()]


def validate_features(df, schema):
    require_columns(df, schema)
    out = df[list(schema)].copy()
    for c, spec in schema.items():
        if spec['type'] == 'numeric':
            v = pd.to_numeric(out[c], errors='coerce')
            if (out[c].notna() & v.isna()).any() or np.isinf(v.dropna()).any():
                raise ValueError(f'{c}: enter finite numeric values or leave missing.')
            if (v.dropna() < 0).any(): raise ValueError(f'{c}: negative values are invalid.')
            if c in ['EnvironmentSatisfaction','JobInvolvement','JobSatisfaction','RelationshipSatisfaction','WorkLifeBalance'] and not v.dropna().isin([1,2,3,4]).all():
                raise ValueError(f'{c}: use an integer from 1 to 4.')
            if c in INTEGER_DOMAINS and not v.dropna().isin(INTEGER_DOMAINS[c]).all():
                raise ValueError(f'{c}: invalid ordinal category.')
            if c in COUNT_FIELDS and (v.dropna()%1!=0).any():
                raise ValueError(f'{c}: enter whole numbers.')
            out[c] = v
        else:
            known = set(spec['categories'])
            if not out[c].dropna().isin(known).all():
                raise ValueError(f'{c}: supported categories: {sorted(known)}')
    for child,parent in [('YearsAtCompany','TotalWorkingYears'),('YearsInCurrentRole','YearsAtCompany'),('YearsSinceLastPromotion','YearsAtCompany'),('YearsWithCurrManager','YearsAtCompany')]:
        if child in out and parent in out and (out[child]>out[parent]).any():
            raise ValueError(f'{child} cannot exceed {parent}.')
    return out
