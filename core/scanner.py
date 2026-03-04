"""
NexPlorer Directory Scanner
- Non-blocking threaded scan with progress callback
- Builds FileNode tree (name, size, mtime, category, children)
- Extension stats, size distribution, duplicate candidates (size-bucket)
"""
import os, stat, fnmatch, threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable, List, Optional
from collections import defaultdict

from nexplorer.core.constants import get_category


@dataclass
class FileNode:
    path:     Path
    name:     str
    size:     int
    mtime:    float
    is_dir:   bool
    category: str
    children: List["FileNode"] = field(default_factory=list)

    @property
    def size_str(self) -> str:
        for unit in ("B","KB","MB","GB","TB"):
            if self.size < 1024: return f"{self.size:.1f} {unit}"
            self.size /= 1024
        return f"{self.size:.1f} PB"


class Scanner:
    def __init__(
        self,
        root: Path,
        exclude: list = None,
        progress_cb: Optional[Callable[[int, str], None]] = None,
        done_cb: Optional[Callable[[dict], None]] = None,
    ):
        self.root       = root
        self.exclude    = exclude or ["*.tmp","*.DS_Store","Thumbs.db","desktop.ini"]
        self.progress_cb= progress_cb
        self.done_cb    = done_cb
        self._stop      = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self):
        try:
            result = self._scan(self.root, depth=0)
            if self.done_cb and not self._stop.is_set():
                self.done_cb(result)
        except Exception as e:
            if self.done_cb: self.done_cb({"error": str(e)})

    def _scan(self, path: Path, depth: int) -> dict:
        nodes, ext_count, ext_size, size_buckets = [], defaultdict(int), defaultdict(int), defaultdict(list)
        total_files = total_dirs = total_size = 0

        try:
            entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return {"error": f"Permission denied: {path}"}

        for entry in entries:
            if self._stop.is_set(): break
            if any(fnmatch.fnmatch(entry.name, p) for p in self.exclude):
                continue
            try:
                s    = entry.stat()
                size = s.st_size if entry.is_file() else 0
                cat  = get_category(entry.suffix) if entry.is_file() else "folder"
                node = FileNode(
                    path=entry, name=entry.name, size=size,
                    mtime=s.st_mtime, is_dir=entry.is_dir(), category=cat
                )
                if entry.is_dir():
                    total_dirs += 1
                    node.children = []   # lazy-load on expand
                else:
                    total_files += 1
                    total_size  += size
                    e = entry.suffix.lower() or "(none)"
                    ext_count[e]  += 1
                    ext_size[e]   += size
                    size_buckets[size].append(str(entry))

                nodes.append(node)
                if self.progress_cb:
                    self.progress_cb(total_files, entry.name)
            except Exception:
                continue

        return {
            "nodes":        nodes,
            "total_files":  total_files,
            "total_dirs":   total_dirs,
            "total_size":   total_size,
            "ext_count":    dict(sorted(ext_count.items(), key=lambda x:-x[1])),
            "ext_size":     dict(sorted(ext_size.items(),  key=lambda x:-x[1])),
            "dup_candidates": {s: paths for s,paths in size_buckets.items()
                               if len(paths) > 1 and s > 0},
        }
