"""
Fast file hashing — BLAKE3 preferred, SHA-256 fallback.
Supports full hash, partial hash (quick-scan), and streaming progress callback.
"""
import hashlib, os
from pathlib import Path
from typing import Callable, Optional

try:
    import blake3 as _b3
    ENGINE = "blake3"
    def _new_hasher(): return _b3.blake3()
except ImportError:
    ENGINE = "sha256"
    def _new_hasher(): return hashlib.sha256()


def hash_file(
    fp: Path,
    limit: int = 0,
    progress_cb: Optional[Callable[[int, int], None]] = None,
    chunk: int = 1 << 20,
) -> str:
    """
    Hash a file.
    limit=0 → full file.
    limit>0 → only first `limit` bytes (quick-scan mode).
    progress_cb(bytes_done, total) called each chunk if provided.
    """
    h = _new_hasher()
    size = fp.stat().st_size
    total = min(size, limit) if limit else size
    done  = 0
    with open(fp, "rb") as f:
        while True:
            to_read = min(chunk, total - done) if limit else chunk
            if to_read <= 0: break
            buf = f.read(to_read)
            if not buf: break
            h.update(buf)
            done += len(buf)
            if progress_cb: progress_cb(done, total)
    return h.hexdigest()


def hash_bytes(data: bytes) -> str:
    h = _new_hasher(); h.update(data); return h.hexdigest()
