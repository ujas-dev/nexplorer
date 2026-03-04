#!/usr/bin/env bash
# build.sh — NexPlorer portable build via Nuitka
# Output: dist/NexPlorer-linux/   (portable folder)
#         dist/NexPlorer-linux.tar.gz  (distribute this)
# Zero Python required on target machine.

set -e

PYTHON=${PYTHON:-python}
VENV=".venv_build"
VERSION="1.0.0"
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')

echo "═══════════════════════════════════════════"
echo "  NexPlorer v${VERSION} — Nuitka Build"
echo "  Platform: ${PLATFORM}"
echo "═══════════════════════════════════════════"

# ── Step 1: Clean build venv (no conda, no system bloat) ──────────────────────
echo "[1/7] Creating clean pip-only venv..."
$PYTHON -m venv $VENV
source $VENV/bin/activate

# ── Step 2: Install minimal runtime deps ──────────────────────────────────────
echo "[2/7] Installing runtime deps..."
pip install --upgrade pip -q
pip install   customtkinter   blake3   zstandard lz4 brotli py7zr   Pillow imagehash piexif   watchdog psutil cryptography   PyYAML schedule   -q

# Optional extras — degrade gracefully if unavailable
pip install pymupdf   -q || echo "  skip: pymupdf"
pip install mutagen   -q || echo "  skip: mutagen"
pip install python-magic -q || echo "  skip: python-magic"

# ── Step 3: Install Nuitka + C compiler deps ──────────────────────────────────
echo "[3/7] Installing Nuitka..."
pip install nuitka ordered-set -q

# Ensure C compiler available (Nuitka needs gcc/clang)
if ! command -v gcc &>/dev/null && ! command -v clang &>/dev/null; then
  echo "  Installing gcc..."
  apt-get install -y gcc --quiet 2>/dev/null ||   brew install gcc --quiet 2>/dev/null ||   echo "  WARNING: No C compiler found. Install gcc first."
fi

# Install UPX for post-build compression
if command -v apt-get &>/dev/null; then
  apt-get install -y upx-ucl -q 2>/dev/null || true
elif command -v brew &>/dev/null; then
  brew install upx -q 2>/dev/null || true
fi

# ── Step 4: Clean previous build ──────────────────────────────────────────────
echo "[4/7] Cleaning previous artifacts..."
rm -rf build/ dist/ nexplorer.build nexplorer.dist nexplorer.onefile-build

# ── Step 5: Nuitka compile ────────────────────────────────────────────────────
echo "[5/7] Compiling Python → C → native binary (this takes 2-5 min)..."

$VENV/bin/python -m nuitka   --onefile   --standalone   --output-dir=dist   --output-filename=NexPlorer     --enable-plugin=tk-inter   --enable-plugin=upx     --include-package=nexplorer   --include-package=customtkinter   --include-package=PIL   --include-package=cryptography   --include-package=zstandard   --include-package=lz4   --include-package=brotli   --include-package=py7zr   --include-package=psutil   --include-package=watchdog   --include-package=piexif   --include-package=imagehash   --include-package=yaml   --include-package=blake3     --nofollow-import-to=boto3   --nofollow-import-to=botocore   --nofollow-import-to=google   --nofollow-import-to=dropbox   --nofollow-import-to=numpy   --nofollow-import-to=pandas   --nofollow-import-to=scipy   --nofollow-import-to=matplotlib   --nofollow-import-to=IPython   --nofollow-import-to=jupyter   --nofollow-import-to=sklearn   --nofollow-import-to=tensorflow   --nofollow-import-to=torch   --nofollow-import-to=docx   --nofollow-import-to=openpyxl   --nofollow-import-to=pptx   --nofollow-import-to=tkinter.test   --nofollow-import-to=lib2to3   --nofollow-import-to=unittest   --nofollow-import-to=doctest   --nofollow-import-to=pdb   --nofollow-import-to=pydoc   --nofollow-import-to=distutils   --nofollow-import-to=setuptools   --nofollow-import-to=pkg_resources   --nofollow-import-to=xmlrpc   --nofollow-import-to=ftplib   --nofollow-import-to=imaplib   --nofollow-import-to=mailbox   --nofollow-import-to=nntplib   --nofollow-import-to=poplib   --nofollow-import-to=telnetlib   --nofollow-import-to=turtledemo     --windows-disable-console   --assume-yes-for-downloads   --remove-output   --no-pyi-file     nexplorer/__main__.py

# ── Step 6: UPX compress the output binary (extra 30-40% reduction) ───────────
echo "[6/7] Applying UPX compression..."
if command -v upx &>/dev/null; then
  upx --best --lzma dist/NexPlorer 2>/dev/null ||   upx --best dist/NexPlorer 2>/dev/null ||   echo "  UPX failed on this binary — skipping (binary still works)"
else
  echo "  UPX not found — skipping compression"
fi

# ── Step 7: Report ────────────────────────────────────────────────────────────
echo "[7/7] Build complete!"
echo ""
echo "Binary:"
ls -lh dist/NexPlorer 2>/dev/null
echo ""
echo "Run with:"
echo "  chmod +x dist/NexPlorer && ./dist/NexPlorer"
echo ""

deactivate
