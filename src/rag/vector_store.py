import json
import os
import hashlib
from pathlib import Path
import faiss
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from src.utils.config import INDEX, EMBEDDING_MODEL
from src.utils.embeddings import encode
from src.utils.helpers import save_json, read_json, timestamp
from src.rag.document_loader import load_documents
from src.rag.chunker import chunk_documents

def build_index(folder,output=INDEX,backend='semantic',chunk_size=140,chunk_overlap=25,model=EMBEDDING_MODEL):
    pages,errors=load_documents(folder);chunks=chunk_documents(pages,chunk_size,chunk_overlap)
    texts=[c['section']+' '+c['text'] for c in chunks];output=Path(output);output.mkdir(parents=True,exist_ok=True)
    if backend=='semantic':vectors=encode(texts,model)
    elif backend=='lexical':
        vectorizer=TfidfVectorizer(ngram_range=(1,2),stop_words='english',max_features=12000)
        vectors=vectorizer.fit_transform(texts).toarray().astype('float32');joblib.dump(vectorizer,output/'lexical_vectorizer.joblib')
    else:raise ValueError('Backend must be semantic or lexical.')
    faiss.normalize_L2(vectors);index=faiss.IndexFlatIP(vectors.shape[1]);index.add(vectors)
    # Replace index last only after all computations succeeded.
    faiss.write_index(index,str(output/'index.faiss'))
    save_json(output/'chunks.json',chunks)
    meta={'backend':backend,'embedding_model':model if backend=='semantic' else 'TF-IDF (explicit lexical fallback)','dimensions':vectors.shape[1],'documents':len(set(c['document_name'] for c in chunks)),'pages':len(pages),'chunks':len(chunks),'chunk_size_words':chunk_size,'chunk_overlap_words':chunk_overlap,'created':timestamp(),'errors':errors,'source_hashes':{p['document_name']:p['document_sha256'] for p in pages}}
    save_json(output/'metadata.json',meta);return meta

def search(query,top_k=6,folder=INDEX,min_similarity=.30):
    if not query.strip():raise ValueError('Enter a policy question.')
    folder=Path(folder)
    if not (folder/'metadata.json').exists():raise FileNotFoundError('Policy index missing. Run python scripts/build_policy_index.py --input data/policies')
    meta=read_json(folder/'metadata.json');chunks=read_json(folder/'chunks.json')
    if meta['backend']=='semantic':q=encode([query],meta['embedding_model'])
    else:q=joblib.load(folder/'lexical_vectorizer.joblib').transform([query]).toarray().astype('float32')
    faiss.normalize_L2(q); index=faiss.read_index(str(folder/'index.faiss'))
    scores,ids=index.search(q,min(max(int(top_k),1),len(chunks)))
    return [dict(chunks[int(i)],similarity=float(s)) for s,i in zip(scores[0],ids[0]) if i>=0 and s>=min_similarity],meta
