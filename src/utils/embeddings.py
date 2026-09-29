"""Semantic encoding with an explicit lexical fallback; never silently substitute."""
from functools import lru_cache
import numpy as np
from src.utils.config import EMBEDDING_MODEL

@lru_cache(maxsize=2)
def get_encoder(model=EMBEDDING_MODEL):
    try:
        from sentence_transformers import SentenceTransformer
        try:
            return SentenceTransformer(model, device='cpu', trust_remote_code=False, local_files_only=True)
        except (OSError, ValueError):
            return SentenceTransformer(model, device='cpu', trust_remote_code=False)
    except Exception as e:
        raise RuntimeError('Embedding model unavailable. Download it in a network-enabled environment, set EMBEDDING_MODEL to a local model path, or explicitly select lexical fallback.') from e

def encode(texts, model=EMBEDDING_MODEL):
    return np.asarray(get_encoder(model).encode(list(texts),normalize_embeddings=True,show_progress_bar=False),dtype='float32')
