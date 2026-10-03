"""Evaluate page/section retrieval against author-curated fictional policy questions."""
try:
    import _bootstrap
except ModuleNotFoundError:
    from scripts import _bootstrap
import argparse
from pathlib import Path
import pandas as pd
from src.rag.vector_store import search
from src.utils.config import DATA, INDEX, REPORTS
from src.utils.helpers import save_json


def evaluate(cases, index=INDEX, k=5, min_similarity=.30):
    frame=pd.read_csv(cases).fillna('');rows=[]
    for case in frame.itertuples(index=False):
        found,meta=search(case.question,k,index,min_similarity)
        expected=[x.split('|',2) for x in str(case.expected_sources).split(';') if x]
        retrieved={(r['document_name'],str(r['page_number']),r['section']) for r in found}
        hits=[any(name==doc and number==expected_page and section.startswith(prefix) for name,number,section in retrieved) for doc,expected_page,prefix in expected]
        rows.append({'case_id':case.case_id,'question':case.question,'answerable':bool(int(case.answerable)),
                     'expected_sources':case.expected_sources,'expected_source_hits':sum(hits),'expected_source_count':len(expected),
                     'all_expected_in_top_k':all(hits) if expected else None,
                     'abstained':not found,'retrieved_sources':'; '.join(f"{r['document_name']}|{r['page_number']}|{r['section']}" for r in found)})
    supported=[r for r in rows if r['answerable']];unsupported=[r for r in rows if not r['answerable']]
    total=sum(r['expected_source_count'] for r in supported)
    report={'benchmark':'author-curated questions for fictional policies; retrieval only, not answer faithfulness',
            'index_backend':meta['backend'],'top_k':k,'min_similarity':min_similarity,
            'questions':len(rows),'supported_questions':len(supported),'unsupported_questions':len(unsupported),
            'source_recall_at_k':sum(r['expected_source_hits'] for r in supported)/total if total else 0.,
            'all_sources_recalled_rate':sum(bool(r['all_expected_in_top_k']) for r in supported)/len(supported) if supported else 0.,
            'unsupported_abstention_rate':sum(r['abstained'] for r in unsupported)/len(unsupported) if unsupported else 0.}
    return report,rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cases',default=str(DATA/'evaluation/policy_queries.csv'));p.add_argument('--index',default=str(INDEX));p.add_argument('--top-k',type=int,default=5);p.add_argument('--min-similarity',type=float,default=.30);a=p.parse_args()
    report,rows=evaluate(a.cases,a.index,a.top_k,a.min_similarity);REPORTS.mkdir(exist_ok=True)
    save_json(REPORTS/'policy_retrieval_evaluation.json',report)
    pd.DataFrame(rows).to_csv(REPORTS/'policy_retrieval_cases.csv',index=False)
    print(report)
