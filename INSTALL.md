# 📥 Installing NexPlorer

> **Zero installation required. No Python. No dependencies. Download and run.**

---

## 🪟 Windows

1. Download `NexPlorer-windows-x86_64.exe`
2. Double-click it

That's it. No installer. No admin rights needed.

> **Windows SmartScreen warning?**
> Click "More info" → "Run anyway". This happens because the .exe is not code-signed yet.
> [See our roadmap for signing](../../issues).

---

## 🐧 Linux

```bash
# Download
wget https://github.com/ujas-dev/nexplorer/releases/latest/download/NexPlorer-linux-x86_64

# Make executable
chmod +x NexPlorer-linux-x86_64

# Run
./NexPlorer-linux-x86_64
```

**Optional: add to PATH**
```bash
sudo mv NexPlorer-linux-x86_64 /usr/local/bin/nexplorer
nexplorer   # run from anywhere
```

---

## 🍎 macOS

```bash
# Download
curl -L -o NexPlorer https://github.com/ujas-dev/nexplorer/releases/latest/download/NexPlorer-macos-x86_64

# Make executable
chmod +x NexPlorer

# Remove quarantine (macOS Gatekeeper blocks unsigned binaries)
xattr -cr NexPlorer

# Run
./NexPlorer
```

---

## ✅ What's Inside the Binary

The single executable file includes:
- Complete Python runtime (compiled to native C via Nuitka)
- All GUI libraries (CustomTkinter)
- All compression engines (zstd, lz4, brotli, 7z, gzip, etc.)
- AES-256 encryption engine
- File hashing (BLAKE3)
- Drive detection
- File metadata reader (PDF, image, audio, video)

**Nothing else needs to be installed.**

---

## 📦 Expected File Sizes

| Platform | Size |
|---|---|
| Windows `.exe` | ~25–35 MB |
| Linux binary | ~20–30 MB |
| macOS binary | ~25–35 MB |

This is **industry standard** for a full-featured portable GUI application with zero dependencies.
For comparison: WinRAR = 4 MB (Windows-only, no GUI framework bundled), 7-Zip = 1.5 MB (Win32 raw API only), VLC = 40 MB portable.
