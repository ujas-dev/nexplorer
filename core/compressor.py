"""
NexPlorer Universal Compression Engine
Supports: zstd, lz4, brotli, gzip, bz2, lzma, zip, 7z, tar.gz, tar.xz, snappy
Auto-selects algorithm based on file type and user priority.
"""
import gzip, bz2, lzma, zipfile, tarfile, os, time, shutil
from pathlib import Path
from typing import Callable, Optional

# ── Optional fast libs
try:    import zstandard as _zstd;  HAS_ZSTD   = True
except ImportError:                  HAS_ZSTD   = False
try:    import lz4.frame as _lz4;   HAS_LZ4    = True
except ImportError:                  HAS_LZ4    = False
try:    import brotli as _brotli;   HAS_BROTLI = True
except ImportError:                  HAS_BROTLI = False
try:    import py7zr;               HAS_7Z     = True
except ImportError:                  HAS_7Z     = False
try:    import snappy;              HAS_SNAPPY  = True
except ImportError:                  HAS_SNAPPY  = False

CHUNK = 1 << 20  # 1MB

# Already-compressed formats — don't waste CPU trying to compress them
_SKIP_COMPRESS = {".jpg",".jpeg",".png",".gif",".mp4",".mkv",".mp3",".aac",
                  ".zip",".7z",".rar",".gz",".bz2",".xz",".zst",".lz4",
                  ".br",".webm",".avi",".heic",".webp",".epub"}

def _progress_wrapper(src_size: int, cb: Optional[Callable]):
    done = [0]
    def update(n):
        done[0] += n
        if cb: cb(done[0], src_size)
    return update


def smart_algorithm(fp: Path, priority: str = "balanced") -> str:
    """Auto-select best algorithm based on file type and priority."""
    ext = fp.suffix.lower()
    if ext in _SKIP_COMPRESS:
        return "lz4"   # already compressed — use fastest, saves little but preserves ability to store
    if priority == "speed":        return "lz4" if HAS_LZ4 else "gzip"
    if priority == "max_ratio":    return "lzma"
    if ext in {".txt",".csv",".json",".xml",".md",".log",".py",".js",".html",".css"}:
        return "brotli" if HAS_BROTLI else ("zstd" if HAS_ZSTD else "gzip")
    return "zstd" if HAS_ZSTD else "gzip"


def compress(
    src: Path,
    dst: Optional[Path] = None,
    algorithm: str = "auto",
    level: int = 3,
    priority: str = "balanced",
    password: Optional[str] = None,
    progress_cb: Optional[Callable[[int, int], None]] = None,
    dry_run: bool = False,
) -> dict:
    """
    Compress src file.
    Returns result dict: {src, dst, algorithm, original_size, compressed_size,
                          ratio, elapsed, speed_mbps}
    """
    if algorithm == "auto":
        algorithm = smart_algorithm(src, priority)

    from nexplorer.core.constants import COMPRESSORS
    ext = COMPRESSORS.get(algorithm, {}).get("ext", f".{algorithm}")

    out = dst or src.parent / (src.name + ext)
    t0  = time.perf_counter()
    src_size = src.stat().st_size

    if dry_run:
        return {"src": str(src), "dst": str(out), "algorithm": algorithm,
                "original_size": src_size, "compressed_size": 0,
                "ratio": 0, "elapsed": 0, "speed_mbps": 0, "dry_run": True}

    _fn = {
        "zstd":   _compress_zstd,
        "lz4":    _compress_lz4,
        "brotli": _compress_brotli,
        "gzip":   _compress_gzip,
        "bz2":    _compress_bz2,
        "lzma":   _compress_lzma,
        "zip":    _compress_zip,
        "7z":     _compress_7z,
        "tar.gz": _compress_tar_gz,
        "tar.xz": _compress_tar_xz,
        "snappy": _compress_snappy,
    }.get(algorithm)

    if not _fn:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    _fn(src, out, level, password, progress_cb)

    elapsed = time.perf_counter() - t0
    dst_size = out.stat().st_size
    ratio    = round((1 - dst_size / src_size) * 100, 1) if src_size else 0
    speed    = round((src_size / 1048576) / elapsed, 1) if elapsed else 0

    return {
        "src": str(src), "dst": str(out), "algorithm": algorithm,
        "original_size": src_size, "compressed_size": dst_size,
        "ratio": ratio, "elapsed": round(elapsed, 3), "speed_mbps": speed,
    }


def decompress(
    src: Path,
    dst_dir: Optional[Path] = None,
    password: Optional[str] = None,
    progress_cb: Optional[Callable[[int, int], None]] = None,
) -> dict:
    """Auto-detect format from extension and decompress."""
    out_dir = dst_dir or src.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    name = src.name.lower()

    if   name.endswith(".zst"):         _decompress_zstd(src, out_dir)
    elif name.endswith(".lz4"):         _decompress_lz4(src, out_dir)
    elif name.endswith(".br"):          _decompress_brotli(src, out_dir)
    elif name.endswith(".gz") and not name.endswith(".tar.gz"):
                                        _decompress_gzip(src, out_dir)
    elif name.endswith(".bz2") and not name.endswith(".tar.bz2"):
                                        _decompress_bz2(src, out_dir)
    elif name.endswith(".xz") and not name.endswith(".tar.xz"):
                                        _decompress_lzma(src, out_dir)
    elif name.endswith(".zip"):         _decompress_zip(src, out_dir, password)
    elif name.endswith(".7z"):          _decompress_7z(src, out_dir, password)
    elif "tar" in name:                 _decompress_tar(src, out_dir)
    elif name.endswith(".snappy"):      _decompress_snappy(src, out_dir)
    else:
        raise ValueError(f"Unknown archive format: {src.suffix}")

    return {"src": str(src), "dst": str(out_dir),
            "elapsed": round(time.perf_counter()-t0, 3)}


# ── Per-algorithm implementations ────────────────────────────────────────────

def _compress_zstd(src, dst, level, pwd, cb):
    if not HAS_ZSTD: raise ImportError("pip install zstandard")
    cctx = _zstd.ZstdCompressor(level=min(level*3, 22), threads=-1)
    sz   = src.stat().st_size; done = 0
    with open(src,"rb") as fi, open(dst,"wb") as fo:
        with cctx.stream_writer(fo) as w:
            while buf := fi.read(CHUNK):
                w.write(buf); done += len(buf)
                if cb: cb(done, sz)

def _decompress_zstd(src, dst_dir):
    if not HAS_ZSTD: raise ImportError("pip install zstandard")
    dctx = _zstd.ZstdDecompressor()
    out  = dst_dir / src.stem
    with open(src,"rb") as fi, open(out,"wb") as fo:
        dctx.copy_stream(fi, fo)

def _compress_lz4(src, dst, level, pwd, cb):
    if not HAS_LZ4: raise ImportError("pip install lz4")
    sz = src.stat().st_size; done = 0
    with open(src,"rb") as fi, _lz4.open(dst,"wb",
              compression_level=_lz4.COMPRESSIONLEVEL_MAX) as fo:
        while buf := fi.read(CHUNK):
            fo.write(buf); done += len(buf)
            if cb: cb(done, sz)

def _decompress_lz4(src, dst_dir):
    if not HAS_LZ4: raise ImportError("pip install lz4")
    out = dst_dir / src.stem
    with _lz4.open(str(src),"rb") as fi, open(out,"wb") as fo:
        shutil.copyfileobj(fi, fo)

def _compress_brotli(src, dst, level, pwd, cb):
    if not HAS_BROTLI: raise ImportError("pip install brotli")
    data = src.read_bytes()
    dst.write_bytes(_brotli.compress(data, quality=min(level*1+3, 11)))
    if cb: cb(len(data), len(data))

def _decompress_brotli(src, dst_dir):
    if not HAS_BROTLI: raise ImportError("pip install brotli")
    (dst_dir / src.stem).write_bytes(_brotli.decompress(src.read_bytes()))

def _compress_gzip(src, dst, level, pwd, cb):
    sz = src.stat().st_size; done = 0
    with open(src,"rb") as fi, gzip.open(dst,"wb",compresslevel=min(level,9)) as fo:
        while buf := fi.read(CHUNK):
            fo.write(buf); done += len(buf)
            if cb: cb(done, sz)

def _decompress_gzip(src, dst_dir):
    out = dst_dir / src.stem
    with gzip.open(src,"rb") as fi, open(out,"wb") as fo:
        shutil.copyfileobj(fi, fo)

def _compress_bz2(src, dst, level, pwd, cb):
    sz = src.stat().st_size; done = 0
    with open(src,"rb") as fi, bz2.open(dst,"wb",compresslevel=min(level,9)) as fo:
        while buf := fi.read(CHUNK):
            fo.write(buf); done += len(buf)
            if cb: cb(done, sz)

def _decompress_bz2(src, dst_dir):
    out = dst_dir / src.stem
    with bz2.open(src,"rb") as fi, open(out,"wb") as fo:
        shutil.copyfileobj(fi, fo)

def _compress_lzma(src, dst, level, pwd, cb):
    sz = src.stat().st_size; done = 0
    with open(src,"rb") as fi, lzma.open(dst,"wb",preset=min(level,9)) as fo:
        while buf := fi.read(CHUNK):
            fo.write(buf); done += len(buf)
            if cb: cb(done, sz)

def _decompress_lzma(src, dst_dir):
    out = dst_dir / src.stem
    with lzma.open(src,"rb") as fi, open(out,"wb") as fo:
        shutil.copyfileobj(fi, fo)

def _compress_zip(src, dst, level, pwd, cb):
    with zipfile.ZipFile(dst,"w",zipfile.ZIP_DEFLATED,
                         compresslevel=min(level,9)) as zf:
        if pwd: zf.setpassword(pwd.encode())
        zf.write(src, src.name)
    if cb: cb(src.stat().st_size, src.stat().st_size)

def _decompress_zip(src, dst_dir, pwd):
    with zipfile.ZipFile(src,"r") as zf:
        if pwd: zf.setpassword(pwd.encode())
        zf.extractall(dst_dir)

def _compress_7z(src, dst, level, pwd, cb):
    if not HAS_7Z: raise ImportError("pip install py7zr")
    filters = [{"id": py7zr.FILTER_LZMA2, "preset": min(level*2, 9)}]
    with py7zr.SevenZipFile(dst,"w",password=pwd,filters=filters) as z:
        z.write(src, src.name)
    if cb: cb(src.stat().st_size, src.stat().st_size)

def _decompress_7z(src, dst_dir, pwd):
    if not HAS_7Z: raise ImportError("pip install py7zr")
    with py7zr.SevenZipFile(src,"r",password=pwd) as z:
        z.extractall(dst_dir)

def _compress_tar_gz(src, dst, level, pwd, cb):
    with tarfile.open(dst,"w:gz", compresslevel=min(level,9)) as tf:
        tf.add(src, arcname=src.name)
    if cb: cb(src.stat().st_size, src.stat().st_size)

def _compress_tar_xz(src, dst, level, pwd, cb):
    with tarfile.open(dst,"w:xz", preset=min(level,9)) as tf:
        tf.add(src, arcname=src.name)
    if cb: cb(src.stat().st_size, src.stat().st_size)

def _decompress_tar(src, dst_dir):
    with tarfile.open(src,"r:*") as tf:
        tf.extractall(dst_dir)

def _compress_snappy(src, dst, level, pwd, cb):
    if not HAS_SNAPPY: raise ImportError("pip install python-snappy")
    data = src.read_bytes()
    dst.write_bytes(snappy.compress(data))
    if cb: cb(len(data), len(data))

def _decompress_snappy(src, dst_dir):
    if not HAS_SNAPPY: raise ImportError("pip install python-snappy")
    (dst_dir / src.stem).write_bytes(snappy.decompress(src.read_bytes()))
