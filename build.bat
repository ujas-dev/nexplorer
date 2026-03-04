@echo off
REM build.bat — NexPlorer Windows portable .exe via Nuitka
REM Output: dist\NexPlorer.exe  (single portable file, ~25-35 MB)
REM Zero Python required on target machine.

setlocal enabledelayedexpansion
set VERSION=1.0.0
set VENV=.venv_build

echo ═══════════════════════════════════════════
echo   NexPlorer v%VERSION% — Nuitka Build
echo   Platform: Windows
echo ═══════════════════════════════════════════

echo [1/7] Creating clean pip-only venv...
python -m venv %VENV%
call %VENV%\Scripts\activate.bat

echo [2/7] Installing runtime deps...
pip install --upgrade pip -q
pip install customtkinter blake3 zstandard lz4 brotli py7zr Pillow imagehash piexif watchdog psutil cryptography PyYAML schedule -q

pip install pymupdf   -q 2>nul || echo   skip: pymupdf
pip install mutagen   -q 2>nul || echo   skip: mutagen

echo [3/7] Installing Nuitka...
pip install nuitka ordered-set -q

REM UPX via choco if available
where choco >nul 2>&1 && (choco install upx -y -q 2>nul || true)

echo [4/7] Cleaning previous build...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist nexplorer.build rmdir /s /q nexplorer.build
if exist nexplorer.onefile-build rmdir /s /q nexplorer.onefile-build

echo [5/7] Compiling Python to native Windows binary (2-5 min)...
python -m nuitka ^
  --onefile ^
  --standalone ^
  --output-dir=dist ^
  --output-filename=NexPlorer.exe ^
  --enable-plugin=tk-inter ^
  --enable-plugin=upx ^
  --windows-icon-from-ico=nexplorer\assets\icons\nexplorer.ico ^
  --windows-disable-console ^
  --windows-company-name="NexPlorer" ^
  --windows-product-name="NexPlorer" ^
  --windows-file-version=1.0.0.0 ^
  --windows-product-version=1.0.0.0 ^
  --windows-file-description="NexPlorer - Intelligent File Explorer" ^
  --include-package=nexplorer ^
  --include-package=customtkinter ^
  --include-package=PIL ^
  --include-package=cryptography ^
  --include-package=zstandard ^
  --include-package=lz4 ^
  --include-package=brotli ^
  --include-package=py7zr ^
  --include-package=psutil ^
  --include-package=watchdog ^
  --include-package=piexif ^
  --include-package=imagehash ^
  --include-package=yaml ^
  --include-package=blake3 ^
  --nofollow-import-to=boto3 ^
  --nofollow-import-to=botocore ^
  --nofollow-import-to=google ^
  --nofollow-import-to=dropbox ^
  --nofollow-import-to=numpy ^
  --nofollow-import-to=pandas ^
  --nofollow-import-to=scipy ^
  --nofollow-import-to=matplotlib ^
  --nofollow-import-to=IPython ^
  --nofollow-import-to=unittest ^
  --nofollow-import-to=doctest ^
  --nofollow-import-to=pdb ^
  --nofollow-import-to=pydoc ^
  --nofollow-import-to=distutils ^
  --nofollow-import-to=setuptools ^
  --nofollow-import-to=pkg_resources ^
  --nofollow-import-to=docx ^
  --nofollow-import-to=openpyxl ^
  --nofollow-import-to=pptx ^
  --assume-yes-for-downloads ^
  --remove-output ^
  nexplorer\__main__.py

echo [6/7] Applying UPX compression...
where upx >nul 2>&1 && (
  upx --best --lzma dist\NexPlorer.exe 2>nul || upx --best dist\NexPlorer.exe 2>nul || echo   UPX compression skipped
)

echo [7/7] Build complete!
echo.
dir dist\NexPlorer.exe
echo.
echo Run: dist\NexPlorer.exe  (no install needed)
call %VENV%\Scripts\deactivate.bat
