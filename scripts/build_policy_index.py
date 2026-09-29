import _bootstrap
import argparse
import os
from src.rag.vector_store import build_index
from src.utils.config import POLICIES, EMBEDDING_MODEL
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',default=str(POLICIES));p.add_argument('--backend',choices=['semantic','lexical'],default=os.getenv('EMBEDDING_BACKEND','semantic'));p.add_argument('--model',default=EMBEDDING_MODEL);p.add_argument('--chunk-size',type=int,default=int(os.getenv('RAG_CHUNK_SIZE',140)));p.add_argument('--chunk-overlap',type=int,default=int(os.getenv('RAG_CHUNK_OVERLAP',25)))
    a=p.parse_args();m=build_index(a.input,backend=a.backend,chunk_size=a.chunk_size,chunk_overlap=a.chunk_overlap,model=a.model)
    print(f'Documents indexed: {m["documents"]}\nPages processed: {m["pages"]}\nChunks generated: {m["chunks"]}\nEmbedding model: {m["embedding_model"]}\nVector store saved: vector_store/');print('Skipped documents:',m['errors'])
