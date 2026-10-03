"""A fresh clone can prepare its ignored policy index without retraining."""
import _bootstrap
from src.rag.bootstrap import ensure_policy_index
from src.attrition.predict import load_model
from src.rag.vector_store import search

if __name__=='__main__':
    model,metadata=load_model()
    index=ensure_policy_index()
    hits,_=search('medical leave followed by temporary remote work',top_k=6)
    if not hits:raise SystemExit('Deployment smoke check failed: no policy evidence retrieved.')
    print('Model:',metadata['model_name'],'| Policies:',index['documents'],'| Retrieved:',len(hits))
