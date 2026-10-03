"""Build the bundled policy index on first use in a fresh checkout/deployment."""
import hashlib
import os
import tempfile
from pathlib import Path

from src.rag.vector_store import build_index
from src.utils.config import EMBEDDING_MODEL, INDEX, POLICIES
from src.utils.helpers import read_json


def ensure_policy_index(source=POLICIES, output=INDEX, backend=None, model=EMBEDDING_MODEL):
    source, output = Path(source), Path(output)
    backend = backend or os.getenv('EMBEDDING_BACKEND', 'semantic')
    if backend not in {'semantic', 'lexical'}:
        raise ValueError('EMBEDDING_BACKEND must be semantic or lexical.')
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.glob('*.pdf'))}
    if not hashes:
        raise FileNotFoundError(f'No policy PDFs found in {source}.')
    metadata_file = output / 'metadata.json'
    if metadata_file.exists() and (output / 'index.faiss').exists():
        try:
            meta = read_json(metadata_file)
            if (meta.get('source_hashes') == hashes and meta.get('backend') == backend
                and (backend == 'lexical' or meta.get('embedding_model') == model)):
                return meta
        except (ValueError, OSError, KeyError):
            pass
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='policy_build_', dir=output.parent) as temporary:
        target = Path(temporary) / 'index'
        meta = build_index(source, output=target, backend=backend, model=model)
        # A failed build leaves the previous usable index untouched.
        backup = Path(temporary) / 'old'
        if output.exists():
            os.replace(output, backup)
        try:
            os.replace(target, output)
        except OSError:
            if backup.exists():
                os.replace(backup, output)
            raise
        return meta
