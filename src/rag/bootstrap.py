"""Build the bundled policy index on first use in a fresh checkout/deployment."""
import hashlib
import os
import tempfile
from pathlib import Path

from src.rag.vector_store import build_index, index_lock, validate_index, publish_index
from src.utils.config import EMBEDDING_MODEL, INDEX, POLICIES


def ensure_policy_index(source=POLICIES, output=INDEX, backend=None, model=EMBEDDING_MODEL, chunk_size=None, chunk_overlap=None):
    with index_lock(output):
        return _ensure_policy_index(source,output,backend,model,chunk_size,chunk_overlap)


def _ensure_policy_index(source, output, backend, model, chunk_size, chunk_overlap):
    source, output = Path(source), Path(output)
    backend = backend or os.getenv('EMBEDDING_BACKEND', 'semantic')
    chunk_size=int(chunk_size if chunk_size is not None else os.getenv('RAG_CHUNK_SIZE',140))
    chunk_overlap=int(chunk_overlap if chunk_overlap is not None else os.getenv('RAG_CHUNK_OVERLAP',25))
    if not 0<=chunk_overlap<chunk_size:raise ValueError('Overlap must be smaller than chunk size.')
    if backend not in {'semantic', 'lexical'}:
        raise ValueError('EMBEDDING_BACKEND must be semantic or lexical.')
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.glob('*.pdf'))}
    if not hashes:
        raise FileNotFoundError(f'No policy PDFs found in {source}.')
    metadata_file = output / 'metadata.json'
    if metadata_file.exists() and (output / 'index.faiss').exists():
        try:
            meta = validate_index(output)
            if (meta.get('source_hashes') == hashes and meta.get('backend') == backend
                and (backend == 'lexical' or (meta.get('embedding_model') == model and meta.get('chunking_version') == 2))
                and meta.get('chunk_size_words')==chunk_size and meta.get('chunk_overlap_words')==chunk_overlap):
                return meta
        except (ValueError, OSError, KeyError, RuntimeError, TypeError):
            pass
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='policy_build_', dir=output.parent) as temporary:
        target = Path(temporary) / 'index'
        meta = build_index(source, output=target, backend=backend, model=model, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        # A failed build leaves the previous usable index untouched.
        backup = Path(temporary) / 'old'
        publish_index(target,output,backup)
        return meta
