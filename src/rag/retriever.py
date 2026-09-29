from src.rag.vector_store import search

def retrieve(query,top_k=6,min_similarity=.30,folder=None):
    kwargs={} if folder is None else {'folder':folder}
    return search(query,top_k,min_similarity=min_similarity,**kwargs)
