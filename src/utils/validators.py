import numpy as np
import pandas as pd

def require_columns(df, columns):
    missing = sorted(set(columns) - set(df.columns))
    if missing: raise ValueError('Missing columns: ' + ', '.join(missing))
    if df.empty: raise ValueError('No data rows found.')

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
            out[c] = v
        else:
            known = set(spec['categories'])
            if not out[c].dropna().isin(known).all():
                raise ValueError(f'{c}: supported categories: {sorted(known)}')
    return out
