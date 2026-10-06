"""Bounded, disposable policy indexes, isolated by browser session."""
import shutil
import tempfile
import time
from pathlib import Path
from src.rag.vector_store import build_index
from src.utils.config import POLICIES

SESSION_ROOT = Path(tempfile.gettempdir())/'workforce_policy_sessions'
TTL_SECONDS = 24*60*60


def remove_session_index(index):
    parent = Path(index).resolve().parent
    if parent.parent != SESSION_ROOT.resolve() or not parent.name.startswith('session_'):
        raise ValueError('Invalid session index location.')
    shutil.rmtree(parent, ignore_errors=True)


def cleanup_expired(now=None):
    now = time.time() if now is None else now
    if SESSION_ROOT.exists():
        for folder in SESSION_ROOT.glob('session_*'):
            if folder.is_dir() and now-folder.stat().st_mtime > TTL_SECONDS:
                shutil.rmtree(folder, ignore_errors=True)


def touch_session(index):
    import os
    parent = Path(index).resolve().parent
    if parent.parent != SESSION_ROOT.resolve():raise ValueError('Invalid session location.')
    os.utime(parent, None)


def build_session_index(uploads, backend, chunk_size=140, chunk_overlap=25):
    uploads = uploads or []
    if len(uploads)>20:raise ValueError('Upload at most 20 policies per session.')
    items, seen, total = [], set(), 0
    for upload in uploads:
        name = Path(upload.name.replace('\\','/')).name
        data = upload.getvalue()
        if Path(name).suffix.lower()!='.pdf':raise ValueError('Policy uploads must be PDF files.')
        if name.casefold() in seen:raise ValueError('Duplicate PDF names; rename documents first.')
        if len(data)>20*1024*1024:raise ValueError('Policy exceeds 20 MB.')
        total += len(data)
        if total>50*1024*1024:raise ValueError('Combined policies exceed 50 MB.')
        seen.add(name.casefold());items.append((name,data))
    SESSION_ROOT.mkdir(parents=True,exist_ok=True,mode=0o700)
    cleanup_expired()
    root = Path(tempfile.mkdtemp(prefix='session_',dir=SESSION_ROOT))
    try:
        source = root/'policies'
        source.mkdir()
        for name,data in items:(source/name).write_bytes(data)
        meta = build_index(source if items else POLICIES,root/'index',backend,chunk_size,chunk_overlap)
        return root/'index',meta
    except Exception:
        shutil.rmtree(root,ignore_errors=True)
        raise
