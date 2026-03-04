"""
NexPlorer Per-Folder Vault Encryption
AES-256 (Fernet) — encrypt/decrypt individual files or full folders.
Password is derived via PBKDF2-HMAC-SHA256 (600k iterations, NIST recommended).
Vault appears as a single .nvault file — locked icon in UI.
"""
import os, json, time, base64, hashlib, struct
from pathlib import Path
from typing import Optional

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

PBKDF2_ITERATIONS = 600_000
MAGIC = b"NXVLT1"   # NexPlorer Vault v1 magic header


def _derive_key(password: str, salt: bytes) -> bytes:
    if not HAS_CRYPTO: raise ImportError("pip install cryptography")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt_folder(
    folder: Path,
    vault_path: Path,
    password: str,
    progress_cb=None,
    dry_run: bool = False,
) -> dict:
    """Pack all files in folder into a single .nvault encrypted archive."""
    if not HAS_CRYPTO: raise ImportError("pip install cryptography")
    files = list(folder.rglob("*"))
    files = [f for f in files if f.is_file()]
    if dry_run:
        return {"status":"dry_run","files":len(files),"vault":str(vault_path)}

    salt = os.urandom(16)
    key  = _derive_key(password, salt)
    fern = Fernet(key)

    manifest = []
    blobs    = []
    for i, fp in enumerate(files):
        rel  = str(fp.relative_to(folder))
        data = fp.read_bytes()
        enc  = fern.encrypt(data)
        manifest.append({"rel": rel, "size": len(enc)})
        blobs.append(enc)
        if progress_cb: progress_cb(i+1, len(files))

    manifest_json  = json.dumps(manifest).encode()
    manifest_enc   = fern.encrypt(manifest_json)
    manifest_len   = struct.pack(">I", len(manifest_enc))

    with open(vault_path, "wb") as f:
        f.write(MAGIC)
        f.write(salt)
        f.write(manifest_len)
        f.write(manifest_enc)
        for blob in blobs:
            f.write(blob)

    return {"status":"ok","vault":str(vault_path),
            "files_packed":len(files),"size":vault_path.stat().st_size}


def decrypt_vault(
    vault_path: Path,
    out_dir: Path,
    password: str,
    progress_cb=None,
    dry_run: bool = False,
) -> dict:
    if not HAS_CRYPTO: raise ImportError("pip install cryptography")
    with open(vault_path,"rb") as f:
        magic = f.read(6)
        if magic != MAGIC: raise ValueError("Not a NexPlorer vault file")
        salt         = f.read(16)
        manifest_len = struct.unpack(">I", f.read(4))[0]
        manifest_enc = f.read(manifest_len)

        key  = _derive_key(password, salt)
        fern = Fernet(key)

        try:
            manifest = json.loads(fern.decrypt(manifest_enc))
        except Exception:
            raise ValueError("Wrong password or corrupted vault")

        if dry_run:
            return {"status":"dry_run","files":len(manifest),"out":str(out_dir)}

        for i, entry in enumerate(manifest):
            enc  = f.read(entry["size"])
            data = fern.decrypt(enc)
            out  = out_dir / entry["rel"]
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            if progress_cb: progress_cb(i+1, len(manifest))

    return {"status":"ok","files_extracted":len(manifest),"out":str(out_dir)}
