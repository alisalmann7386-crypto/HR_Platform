"""Descriptive held-out reliability and bootstrap intervals; never alters the fitted model."""
try:
    import _bootstrap
except ModuleNotFoundError:
    from scripts import _bootstrap
import argparse
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score, f1_score, precision_score, recall_score, brier_score_loss
from src.utils.config import REPORTS, MODELS
from src.utils.helpers import read_json, save_json


def evaluate(predictions, threshold, n_bootstrap=1000, seed=42):
    y=predictions['Actual'].to_numpy(dtype=int)
    p=predictions['Attrition_Probability'].to_numpy(dtype=float)
    if len(y)<10 or len(set(y))<2 or len(y)!=len(p):
        raise ValueError('Calibration analysis requires labeled predictions from both classes.')
    n_bins=min(5, max(2, len(y)//40))
    groups=pd.qcut(p, q=n_bins, labels=False, duplicates='drop')
    reliability=(pd.DataFrame({'bin':groups,'actual':y,'probability':p})
                 .groupby('bin').agg(count=('actual','size'),mean_probability=('probability','mean'),observed_rate=('actual','mean')).reset_index())
    rng=np.random.default_rng(seed);samples=[]
    for _ in range(n_bootstrap):
        indices=rng.integers(0,len(y),len(y));by=y[indices];bp=p[indices]
        if len(set(by))<2:continue
        predicted=bp>=threshold
        samples.append({'precision':precision_score(by,predicted,zero_division=0),
                        'recall':recall_score(by,predicted,zero_division=0),
                        'f1':f1_score(by,predicted,zero_division=0),
                        'roc_auc':roc_auc_score(by,bp),
                        'average_precision':average_precision_score(by,bp),
                        'brier_score':brier_score_loss(by,bp)})
    frame=pd.DataFrame(samples)
    intervals={metric:{'lower_95':float(frame[metric].quantile(.025)),'upper_95':float(frame[metric].quantile(.975))} for metric in frame}
    report={'method':'descriptive test-set reliability and percentile bootstrap over held-out rows',
            'note':'Neither a calibrated model nor an independent generalization estimate. No threshold/model selection from test results.',
            'rows':len(y),'positive_rows':int(y.sum()),'bins':len(reliability),'bootstrap_replicates':len(frame),
            'seed':seed,'threshold':float(threshold),'intervals':intervals}
    return report,reliability

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--predictions',default=str(REPORTS/'test_predictions.csv'));parser.add_argument('--replicates',type=int,default=1000);args=parser.parse_args()
    meta=read_json(MODELS/'attrition_metadata.json');report,curve=evaluate(pd.read_csv(args.predictions),meta['threshold'],args.replicates)
    save_json(REPORTS/'calibration_uncertainty.json',report)
    curve.to_csv(REPORTS/'reliability_bins.csv',index=False)
    print(report)
