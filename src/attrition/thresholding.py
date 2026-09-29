import numpy as np
import pandas as pd
from src.attrition.evaluation import evaluate

def threshold_table(y, p):
    return pd.DataFrame([dict(threshold=float(t), **{k:v for k,v in evaluate(y,p,t).items() if k in ['precision','recall','f1']}) for t in np.arange(.05,.951,.025)])
def select_threshold(table):
    # Maximum validation F1, breaking ties by precision then higher threshold.
    return float(table.sort_values(['f1','precision','threshold'],ascending=False).iloc[0].threshold)
