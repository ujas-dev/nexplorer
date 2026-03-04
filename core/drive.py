"""Drive detection — HDD vs SSD vs NVMe, disk usage, partition info"""
import os, sys, subprocess, platform
from pathlib import Path
from typing import Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def detect_drive_type(path: str) -> str:
    """Returns 'ssd', 'nvme', 'hdd', or 'unknown'"""
    if not HAS_PSUTIL: return "unknown"
    try:
        p = Path(path).resolve()
        # Find which partition this path lives on
        best = ""
        best_part = None
        for part in psutil.disk_partitions(all=True):
            if str(p).startswith(part.mountpoint) and len(part.mountpoint) > len(best):
                best = part.mountpoint; best_part = part
        if not best_part: return "unknown"
        device = best_part.device.replace("/dev/","")

        if sys.platform.startswith("linux"):
            # Check rotational flag
            block = device.rstrip("0123456789p")
            rot = Path(f"/sys/block/{block}/queue/rotational")
            if rot.exists():
                is_rotational = rot.read_text().strip() == "1"
                if is_rotational: return "hdd"
                # NVMe check
                return "nvme" if "nvme" in block else "ssd"

        elif sys.platform == "darwin":
            out = subprocess.run(
                ["diskutil","info", device], capture_output=True, text=True
            ).stdout
            if "Solid State" in out: return "ssd"
            if "NVM" in out: return "nvme"
            return "hdd"

        elif sys.platform == "win32":
            # PowerShell query
            ps = (
                f"Get-PhysicalDisk | Where-Object {{$_.DeviceID -eq "
                f"(Get-Partition -DriveLetter '{p.drive[0]}' | "
                f"Get-Disk).Number}} | Select-Object -ExpandProperty MediaType"
            )
            out = subprocess.run(
                ["powershell","-Command", ps], capture_output=True, text=True
            ).stdout.strip()
            if "SSD" in out: return "ssd"
            if "NVMe" in out: return "nvme"
            if "HDD" in out: return "hdd"

    except Exception: pass
    return "unknown"


def disk_usage(path: str) -> dict:
    """Returns total, used, free, percent for a path"""
    if not HAS_PSUTIL:
        st = os.statvfs(path) if hasattr(os,"statvfs") else None
        if st:
            return {"total": st.f_blocks*st.f_frsize, "free": st.f_bavail*st.f_frsize,
                    "used": (st.f_blocks-st.f_bfree)*st.f_frsize, "percent": 0.0}
        return {}
    u = psutil.disk_usage(str(path))
    return {"total": u.total, "used": u.used, "free": u.free, "percent": u.percent}


def same_device(src: Path, dst: Path) -> bool:
    """True if src and dst are on the same physical partition (enables instant rename)"""
    try:
        return os.stat(src).st_dev == os.stat(dst.parent).st_dev
    except Exception: return False


def list_drives() -> list:
    """List all mounted drives/partitions with usage stats"""
    if not HAS_PSUTIL: return []
    result = []
    seen = set()
    for p in psutil.disk_partitions(all=False):
        if p.mountpoint in seen: continue
        seen.add(p.mountpoint)
        try:
            u = psutil.disk_usage(p.mountpoint)
            result.append({
                "mountpoint": p.mountpoint,
                "device":     p.device,
                "fstype":     p.fstype,
                "total":      u.total,
                "used":       u.used,
                "free":       u.free,
                "percent":    u.percent,
                "drive_type": detect_drive_type(p.mountpoint),
            })
        except Exception:
            pass
    return result
