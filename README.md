# 🗂️ NexPlorer v1.0.0

> The only file explorer that understands your files, not just their names.
> **Cross-platform · Offline-first · Open source · Zero telemetry**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)]()
[![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-green)]()
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)]()

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/nexplorer.git && cd nexplorer

# 2. Open in VS Code Dev Container (recommended)
code .
# → VS Code: "Reopen in Container"

# 3. Install deps inside container
pip install -r requirements.txt

# 4. Launch GUI (VNC on :5900 from dev container)
python -m nexplorer

# 5. (Optional) Install as CLI command
pip install -e ".[full]"
nexplorer
```

---

## 📦 Project Structure

```
nexplorer/
├── __init__.py           ← version
├── __main__.py           ← entry point (python -m nexplorer)
├── core/
│   ├── constants.py      ← categories, algorithm registry
│   ├── drive.py          ← HDD/SSD/NVMe detection, disk usage
│   ├── hasher.py         ← BLAKE3/SHA-256 file hashing
│   ├── scanner.py        ← threaded directory scanner
│   ├── transfer.py       ← ultra-fast copy/move + integrity gate + shred
│   ├── compressor.py     ← 11 compression algorithms
│   ├── encryptor.py      ← AES-256 vault encryption
│   └── metadata.py       ← universal metadata reader + EXIF editor
├── ui/
│   ├── app.py            ← main CTk window + sidebar nav
│   └── pages/
│       ├── explorer.py   ← file browser (tree + list + detail)
│       ├── transfer.py   ← copy/move with speed meter
│       ├── compress.py   ← compress/decompress all algorithms
│       ├── vault.py      ← encrypted folder vaults
│       ├── analytics.py  ← storage treemap + duplicate cost
│       └── settings.py   ← preferences
└── plugins/              ← custom rename/processing plugins
```

---

## ✨ What Makes NexPlorer Different

| Feature | NexPlorer | Windows Explorer | macOS Finder | Files by Google |
|---|---|---|---|---|
| Copy integrity gate (hash before+after) | ✅ | ❌ | ❌ | ❌ |
| Forensic-proof shred (7-pass DoD) | ✅ | ❌ | ❌ | ❌ |
| SSD-aware delete (encrypt-then-TRIM) | ✅ | ❌ | ❌ | ❌ |
| Atomic rename (instant same-drive move) | ✅ | ❌ | ❌ | ❌ |
| Kernel-space copy (os.sendfile) | ✅ | ❌ | ❌ | ❌ |
| 11 compression algorithms, smart auto-select | ✅ | zip only | zip only | ❌ |
| Per-folder AES-256 vault encryption | ✅ | ❌ | ❌ | ❌ |
| Drive type detection (show bottleneck) | ✅ | ❌ | ❌ | ❌ |
| EXIF metadata editor (strip GPS, device) | ✅ | ❌ | ❌ | ❌ |
| Universal file metadata panel | ✅ | Partial | Partial | ❌ |
| Plugin system | ✅ | ❌ | ❌ | ❌ |
| Fully offline, zero telemetry | ✅ | ❌ | ❌ | ❌ |

---

## 🛣️ Roadmap

| Version | Features |
|---|---|
| **v1.0.0** ← current | Core engine + GUI explorer + transfer + compression + encryption |
| **v1.1.0** | Analytics treemap · Vault UI · Settings · Watch mode |
| **v1.2.0** | Local LLM file chat · Auto-tag by content · Natural language search |
| **v1.3.0** | Multi-cloud unified view (S3/GDrive/Dropbox) · P2P LAN sync |
| **v2.0.0** | Mobile (Kivy/Android/iOS) · Plugin marketplace |

---

## ⚙️ Dev Container Setup

Requirements: **Docker Desktop, VS Code + Dev Containers extension**

```
VNC viewer → localhost:5900   (no password)
```

Tested on: Windows 11 i7-1255U 16GB RAM [cite:164]

---

## 📄 License

MIT — see [LICENSE](LICENSE)
