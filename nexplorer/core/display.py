"""
NexPlorer Display Detection
- Detects real screen width/height (works in VNC, remote desktop, local)
- Detects if running inside VNC / headless Xvfb (DISPLAY=:99)
- Returns OS name used for native window control styling
- Provides maximize/center strategy per platform
"""
import os, sys, platform

def get_os() -> str:
    """Returns: 'windows' | 'macos' | 'linux' | 'vnc'"""
    s = platform.system().lower()
    if s == "windows": return "windows"
    if s == "darwin":  return "macos"
    # Linux — check if inside VNC / Xvfb
    display = os.environ.get("DISPLAY", "")
    if display.startswith(":9"):  # :99 Xvfb, :90, etc.
        return "vnc"
    return "linux"


def is_vnc() -> bool:
    return get_os() == "vnc"


def get_screen_size(tk_root) -> tuple[int, int]:
    """
    Get actual usable screen size.
    Works for local display, VNC (Xvfb :99), macOS, Windows.
    Returns (width, height) as integers.
    Falls back to tk root winfo if XRANDR not available.
    """
    try:
        # Most reliable: ask Xvfb/X11 directly
        import subprocess
        if sys.platform.startswith("linux") or sys.platform == "darwin":
            out = subprocess.run(
                ["xrandr", "--current"], capture_output=True, text=True, timeout=3
            ).stdout
            for line in out.splitlines():
                if " connected" in line and "x" in line:
                    # e.g. "eDP-1 connected 1920x1080+0+0"
                    for token in line.split():
                        if "x" in token and "+" in token:
                            wh = token.split("+")[0]
                            w, h = wh.split("x")
                            return int(w), int(h)
    except Exception:
        pass
    # Fallback: Tkinter native screen query
    tk_root.update_idletasks()
    return tk_root.winfo_screenwidth(), tk_root.winfo_screenheight()


def get_title_bar_config(os_name: str) -> dict:
    """
    Returns styling config for the custom title bar
    matching the native OS window control style.
    Windows 11 → close/min/max on RIGHT, pill-shaped
    macOS      → close/min/max on LEFT, circle (traffic light)
    Linux/VNC  → close/min/max on RIGHT, squared
    """
    configs = {
        "windows": {
            "btn_side":    "right",
            "btn_shape":   "rect",       # flat squared Windows 11 style
            "btn_radius":  4,
            "btn_size":    46,
            "btn_height":  32,
            "close_color": "#c42b1c",
            "min_color":   "#2d2d2d",
            "max_color":   "#2d2d2d",
            "hover_close": "#e81123",
            "hover_min":   "#404040",
            "hover_max":   "#404040",
            "icon_close":  "✕",
            "icon_min":    "─",
            "icon_max":    "□",
            "icon_restore":"❐",
            "drag_allowed": True,
        },
        "macos": {
            "btn_side":    "left",
            "btn_shape":   "circle",     # macOS traffic light
            "btn_radius":  8,
            "btn_size":    13,
            "btn_height":  13,
            "close_color": "#ff5f57",
            "min_color":   "#febc2e",
            "max_color":   "#28c840",
            "hover_close": "#bf4942",
            "hover_min":   "#bf9122",
            "hover_max":   "#1ea332",
            "icon_close":  "×",
            "icon_min":    "−",
            "icon_max":    "+",
            "icon_restore":"+",
            "drag_allowed": True,
        },
        "linux": {
            "btn_side":    "right",
            "btn_shape":   "rect",
            "btn_radius":  6,
            "btn_size":    40,
            "btn_height":  28,
            "close_color": "#cc241d",
            "min_color":   "#3c3836",
            "max_color":   "#3c3836",
            "hover_close": "#fb4934",
            "hover_min":   "#504945",
            "hover_max":   "#504945",
            "icon_close":  "✕",
            "icon_min":    "─",
            "icon_max":    "□",
            "icon_restore":"❐",
            "drag_allowed": True,
        },
        "vnc": {
            "btn_side":    "right",
            "btn_shape":   "rect",
            "btn_radius":  6,
            "btn_size":    40,
            "btn_height":  28,
            "close_color": "#cc241d",
            "min_color":   "#3c3836",
            "max_color":   "#3c3836",
            "hover_close": "#fb4934",
            "hover_min":   "#504945",
            "hover_max":   "#504945",
            "icon_close":  "✕",
            "icon_min":    "─",
            "icon_max":    "□",
            "icon_restore":"❐",
            "drag_allowed": True,   # VNC: drag enabled since OS chrome may be hidden
        },
    }
    return configs.get(os_name, configs["linux"])
