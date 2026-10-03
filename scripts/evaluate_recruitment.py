"""Author-curated synthetic benchmark, independent of IBM attrition evaluation."""
try:
    import _bootstrap
except ModuleNotFoundError:
    from scripts import _bootstrap
import argparse
from pathlib import Path
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support
from src.recruitment.skill_extractor import extract_skills
from src.recruitment.matcher import match_skills
from src.utils.config import DATA, REPORTS
from src.utils.helpers import save_json


def evaluate(cases, backend='semantic'):
    frame = pd.read_csv(cases).fillna('')
    rows=[]
    for case in frame.itertuples(index=False):
        observed={s['skill'] for s in extract_skills(case.resume_text)}
        expected=set(str(case.expected_skills).split('|'))
        candidate={'skills':sorted(observed),'skill_evidence':extract_skills(case.resume_text)}
        hit=match_skills([case.requirement],candidate,backend)[0]
        rows.append({'case_id':case.case_id,'expected_skills':sorted(expected),'extracted_skills':sorted(observed),
                     'requirement':case.requirement,'expected_alignment':int(case.expected_alignment),
                     'predicted_alignment':int(hit['status']!='Not evidenced'),
                     'status':hit['status'],'similarity':hit['similarity'],'evidence':hit['evidence'],
                     'reason':case.reason})
    labels=[int(x['expected_alignment']) for x in rows]
    predictions=[x['predicted_alignment'] for x in rows]
    precision,recall,f1,_=precision_recall_fscore_support(labels,predictions,average='binary',zero_division=0)
    tp=fp=fn=0
    for row in rows:
        gold=set(row['expected_skills']);found=set(row['extracted_skills'])
        tp+=len(gold&found);fp+=len(found-gold);fn+=len(gold-found)
    report={'benchmark':'author-curated synthetic cases; no independent HR annotation',
            'backend':backend,'cases':len(rows),
            'skill_extraction':{'precision':tp/(tp+fp) if tp+fp else 0.,'recall':tp/(tp+fn) if tp+fn else 0.,'true_positives':tp,'false_positives':fp,'false_negatives':fn},
            'requirement_alignment':{'precision':float(precision),'recall':float(recall),'f1':float(f1),'false_positives':sum(r['expected_alignment']==0 and r['predicted_alignment']==1 for r in rows),
                                     'false_negatives':sum(r['expected_alignment']==1 and r['predicted_alignment']==0 for r in rows)}}
    return report,rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cases',default=str(DATA/'evaluation/recruitment_cases.csv'));p.add_argument('--backend',choices=['semantic','lexical'],default='semantic');a=p.parse_args()
    report,rows=evaluate(a.cases,a.backend);REPORTS.mkdir(exist_ok=True)
    save_json(REPORTS/f'recruitment_evaluation_{a.backend}.json',report)
    pd.DataFrame(rows).to_csv(REPORTS/f'recruitment_cases_{a.backend}.csv',index=False)
    print(report)
