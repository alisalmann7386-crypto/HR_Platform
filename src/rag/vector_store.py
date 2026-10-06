import os
import hashlib
import tempfile
from filelock import FileLock
from pathlib import Path
import faiss
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from src.utils.config import INDEX, EMBEDDING_MODEL
from src.utils.embeddings import encode, get_encoder
from src.utils.helpers import save_json, read_json, timestamp
from src.rag.document_loader import load_documents
from src.rag.chunker import chunk_documents, fit_semantic_chunks

def index_lock(folder):
    folder=Path(folder)
    folder.parent.mkdir(parents=True,exist_ok=True)
    return FileLock(str(folder.parent/(folder.name+'.lock')),timeout=120)


def publish_index(target, output, backup):
    if output.exists():os.replace(output,backup)
    try:os.replace(target,output)
    except OSError:
        if backup.exists():os.replace(backup,output)
        raise


def build_index(folder,output=INDEX,backend='semantic',chunk_size=140,chunk_overlap=25,model=EMBEDDING_MODEL):
    output=Path(output)
    with index_lock(output), tempfile.TemporaryDirectory(prefix='policy_build_',dir=output.parent) as temp:
        target=Path(temp)/'index'
        meta=_write_index(folder,target,backend,chunk_size,chunk_overlap,model)
        validate_index(target)
        publish_index(target,output,Path(temp)/'old')
        return meta


def _write_index(folder,output=INDEX,backend='semantic',chunk_size=140,chunk_overlap=25,model=EMBEDDING_MODEL):
    pages,errors=load_documents(folder);chunks=chunk_documents(pages,chunk_size,chunk_overlap)
    if backend=='semantic':
        encoder=get_encoder(model)
        chunks=fit_semantic_chunks(chunks,encoder.tokenizer,encoder.max_seq_length,chunk_overlap)
    texts=[c['section']+' '+c['text'] for c in chunks];output=Path(output);output.mkdir(parents=True,exist_ok=True)
    if backend=='semantic':vectors=encode(texts,model)
    elif backend=='lexical':
        vectorizer=TfidfVectorizer(ngram_range=(1,2),stop_words='english',max_features=12000)
        vectors=vectorizer.fit_transform(texts).toarray().astype('float32');joblib.dump(vectorizer,output/'lexical_vectorizer.joblib')
    else:raise ValueError('Backend must be semantic or lexical.')
    faiss.normalize_L2(vectors);index=faiss.IndexFlatIP(vectors.shape[1]);index.add(vectors)
    # Write to the isolated build directory; publish only after validation.
    faiss.write_index(index,str(output/'index.faiss'))
    save_json(output/'chunks.json',chunks)
    meta={'chunking_version':2,'backend':backend,'embedding_model':model if backend=='semantic' else 'TF-IDF (explicit lexical fallback)','dimensions':vectors.shape[1],'documents':len(set(c['document_name'] for c in chunks)),'pages':len(pages),'chunks':len(chunks),'chunk_size_words':chunk_size,'chunk_overlap_words':chunk_overlap,'created':timestamp(),'errors':errors,'source_hashes':{p['document_name']:p['document_sha256'] for p in pages}}
    names=['index.faiss','chunks.json']+(['lexical_vectorizer.joblib'] if backend=='lexical' else [])
    meta['artifact_hashes']={name:hashlib.sha256((output/name).read_bytes()).hexdigest() for name in names}
    save_json(output/'metadata.json',meta);return meta

def validate_index(folder):
    folder=Path(folder)
    meta=read_json(folder/'metadata.json')
    if meta['backend'] not in {'semantic','lexical'}:raise ValueError('Invalid index backend.')
    names=['index.faiss','chunks.json']+(['lexical_vectorizer.joblib'] if meta['backend']=='lexical' else [])
    for name in names:
        if hashlib.sha256((folder/name).read_bytes()).hexdigest()!=meta.get('artifact_hashes',{}).get(name):
            raise ValueError('Index artifact missing or changed: '+name)
    chunks=read_json(folder/'chunks.json')
    index=faiss.read_index(str(folder/'index.faiss'))
    if not chunks or len(chunks)!=meta['chunks'] or index.ntotal!=len(chunks) or index.d!=meta['dimensions']:
        raise ValueError('Index counts or dimensions mismatch.')
    if meta['backend']=='lexical' and len(joblib.load(folder/'lexical_vectorizer.joblib').get_feature_names_out())!=index.d:
        raise ValueError('Vectorizer dimensions mismatch.')
    return meta


def search(query,top_k=6,folder=INDEX,min_similarity=.30):
    if not 0<=min_similarity<=1:raise ValueError('Similarity threshold must be between 0 and 1.')
    with index_lock(folder):return _search(query,top_k,folder,min_similarity)


def _search(query,top_k=6,folder=INDEX,min_similarity=.30):
    if not query.strip():raise ValueError('Enter a policy question.')
    folder=Path(folder)
    if not (folder/'metadata.json').exists():raise FileNotFoundError('Policy index missing. Run python scripts/build_policy_index.py --input data/policies')
    meta=validate_index(folder);chunks=read_json(folder/'chunks.json')
    if meta['backend']=='semantic':q=encode([query],meta['embedding_model'])
    else:q=joblib.load(folder/'lexical_vectorizer.joblib').transform([query]).toarray().astype('float32')
    faiss.normalize_L2(q); index=faiss.read_index(str(folder/'index.faiss'))
    scores,ids=index.search(q,min(max(int(top_k),1),len(chunks)))
    return [dict(chunks[int(i)],similarity=float(s)) for s,i in zip(scores[0],ids[0]) if i>=0 and s>=min_similarity],meta
