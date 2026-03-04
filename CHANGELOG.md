# Changelog

## [1.0.0] — 2026-03-05

### Added
- Full project architecture: `nexplorer/core/` + `nexplorer/ui/`
- `core/drive.py` — HDD/SSD/NVMe detection, disk usage, same-device check
- `core/hasher.py` — BLAKE3/SHA-256 with streaming progress
- `core/scanner.py` — threaded directory scanner with extension/size stats
- `core/transfer.py` — atomic rename, sendfile, mmap, integrity gate, forensic shred
- `core/compressor.py` — 11 algorithms: zstd, lz4, brotli, gzip, bz2, lzma, zip, 7z, tar.gz, tar.xz, snappy
- `core/encryptor.py` — AES-256 vault (PBKDF2-HMAC-SHA256, 600k iterations)
- `core/metadata.py` — PDF/ePub/Office/Image/Audio/Video metadata reader + EXIF editor
- `core/constants.py` — file categories, algorithm registry, shred standards
- `ui/app.py` — dark CustomTkinter main window with sidebar nav
- `ui/pages/explorer.py` — full file browser with metadata panel + action bar
- `ui/pages/transfer.py` — copy/move with real-time speed meter + drive info
- `ui/pages/compress.py` — compress/decompress with smart algorithm picker
- `ui/pages/vault.py` — scaffold (full UI in v1.1.0)
- `ui/pages/analytics.py` — scaffold (full UI in v1.1.0)
- `ui/pages/settings.py` — scaffold (full UI in v1.1.0)
- Devcontainer: Dockerfile + docker-compose + devcontainer.json (VNC on :5900)
- `requirements.txt`, `setup.py`, `README.md`
