"""NexPlorer — shared constants"""

APP_NAME    = "NexPlorer"
APP_VERSION = "1.0.0"

# ── File categories
CATEGORIES = {
    "image":    {".jpg",".jpeg",".png",".gif",".bmp",".tiff",".tif",
                 ".webp",".heic",".heif",".avif",".raw",".cr2",".nef",".arw",".dng",".svg"},
    "video":    {".mp4",".mkv",".avi",".mov",".wmv",".flv",".webm",".m4v",".3gp",".ts"},
    "audio":    {".mp3",".flac",".wav",".aac",".ogg",".m4a",".wma",".opus",".aiff"},
    "pdf":      {".pdf"},
    "ebook":    {".epub",".mobi",".azw",".azw3",".fb2",".djvu"},
    "office":   {".docx",".doc",".odt",".xlsx",".xls",".ods",".pptx",".ppt",".odp",".rtf"},
    "code":     {".py",".js",".ts",".jsx",".tsx",".java",".cpp",".c",".h",".cs",
                 ".go",".rs",".rb",".php",".swift",".kt",".scala",".r",".sh",".bash",".zsh"},
    "data":     {".csv",".json",".xml",".yaml",".yml",".toml",".ini",".sql",".db",".sqlite"},
    "archive":  {".zip",".tar",".gz",".bz2",".xz",".7z",".rar",".zst",".lz4",".br"},
    "text":     {".txt",".md",".rst",".log",".conf",".cfg"},
    "font":     {".ttf",".otf",".woff",".woff2"},
    "iso":      {".iso",".img",".dmg"},
}

def get_category(ext: str) -> str:
    e = ext.lower()
    for cat, exts in CATEGORIES.items():
        if e in exts: return cat
    return "other"

# ── Compression algorithms registry
COMPRESSORS = {
    "zstd":   {"name":"Zstandard", "ext":".zst",  "speed":"⚡⚡⚡⚡", "ratio":"🗜️🗜️🗜️🗜️",  "best_for":"All-purpose best balance"},
    "lz4":    {"name":"LZ4",       "ext":".lz4",  "speed":"⚡⚡⚡⚡⚡","ratio":"🗜️🗜️",      "best_for":"Real-time, speed priority"},
    "brotli": {"name":"Brotli",    "ext":".br",   "speed":"⚡⚡⚡",   "ratio":"🗜️🗜️🗜️🗜️",  "best_for":"Text, web assets"},
    "lzma":   {"name":"LZMA/XZ",  "ext":".xz",   "speed":"⚡",      "ratio":"🗜️🗜️🗜️🗜️🗜️","best_for":"Maximum compression, cold archive"},
    "gzip":   {"name":"GZip",     "ext":".gz",   "speed":"⚡⚡⚡",   "ratio":"🗜️🗜️🗜️",    "best_for":"Universal compatibility"},
    "bz2":    {"name":"BZip2",    "ext":".bz2",  "speed":"⚡⚡",     "ratio":"🗜️🗜️🗜️🗜️",  "best_for":"Legacy support"},
    "zip":    {"name":"ZIP",      "ext":".zip",  "speed":"⚡⚡⚡",   "ratio":"🗜️🗜️🗜️",    "best_for":"Cross-platform sharing"},
    "7z":     {"name":"7-Zip",    "ext":".7z",   "speed":"⚡⚡",     "ratio":"🗜️🗜️🗜️🗜️🗜️","best_for":"Archives with AES encryption"},
    "tar.gz": {"name":"TAR+GZ",  "ext":".tar.gz","speed":"⚡⚡⚡",  "ratio":"🗜️🗜️🗜️",    "best_for":"Linux/macOS standard"},
    "tar.xz": {"name":"TAR+XZ",  "ext":".tar.xz","speed":"⚡",     "ratio":"🗜️🗜️🗜️🗜️🗜️","best_for":"Linux distro packaging"},
    "snappy": {"name":"Snappy",   "ext":".snappy","speed":"⚡⚡⚡⚡⚡","ratio":"🗜️",        "best_for":"Databases, streaming"},
}

# ── Shred passes standards
SHRED_STANDARDS = {
    "quick":        {"passes": 1,  "label": "Quick (1-pass random)"},
    "dod_3pass":    {"passes": 3,  "label": "DoD 3-pass"},
    "dod_7pass":    {"passes": 7,  "label": "DoD 5220.22-M (7-pass) ← recommended"},
    "gutmann_35":   {"passes": 35, "label": "Gutmann 35-pass (maximum)"},
}

# ── Drive type labels
DRIVE_LABELS = {
    "hdd": ("HDD", "✅ Forensic-proof shred available"),
    "ssd": ("SSD", "⚠️  Encrypt-then-TRIM used — hardware limits apply"),
    "nvme":("NVMe","⚡ Max transfer speed available"),
    "unknown":("Drive",""),
}
