"""
NexPlorer v1.0.0 — Main Application Window
- Starts small, then maximizes to actual screen size (VNC-safe)
- Custom title bar: Windows 11 style / macOS traffic light / Linux/VNC squared
- OS auto-detected via nexplorer.core.display
"""
import sys, platform, threading
from pathlib import Path

import customtkinter as ctk

from nexplorer.core.display    import get_os, get_screen_size, get_title_bar_config, is_vnc
from nexplorer.ui.titlebar     import TitleBar
from nexplorer.ui.pages.explorer  import ExplorerPage
from nexplorer.ui.pages.transfer  import TransferPage
from nexplorer.ui.pages.compress  import CompressPage
from nexplorer.ui.pages.vault     import VaultPage
from nexplorer.ui.pages.analytics import AnalyticsPage
from nexplorer.ui.pages.settings  import SettingsPage

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

NAV_ITEMS = [
    ("🗂️  Explorer",   "explorer"),
    ("📦  Transfer",   "transfer"),
    ("🗜️  Compress",   "compress"),
    ("🔐  Vault",      "vault"),
    ("📊  Analytics",  "analytics"),
    ("⚙️  Settings",   "settings"),
]

COLORS = {
    "bg":        "#1a1a2e",
    "sidebar":   "#16213e",
    "card":      "#0f3460",
    "accent":    "#e94560",
    "accent2":   "#533483",
    "text":      "#eaeaea",
    "muted":     "#888888",
    "success":   "#00b894",
    "warning":   "#fdcb6e",
    "error":     "#d63031",
    "titlebar":  "#0d0d1a",
}

SIDEBAR_W = 220
MIN_W, MIN_H = 900, 600
STARTUP_W, STARTUP_H = 1000, 680   # small start size


class NexPlorerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self._os_name  = get_os()
        self._tb_cfg   = get_title_bar_config(self._os_name)
        self._pages: dict = {}

        # ── 1. Start small and centered ──────────────────────────────────────
        self.geometry(f"{STARTUP_W}x{STARTUP_H}")
        self.minsize(MIN_W, MIN_H)
        self.title("NexPlorer")

        # Remove OS window chrome — we draw our own title bar
        self.overrideredirect(True)

        self.configure(fg_color=COLORS["bg"])
        self.resizable(True, True)

        self._build_layout()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── 2. After window renders, detect actual screen size and maximize ──
        self.after(100, self._smart_maximize)

    # ── Smart maximize ────────────────────────────────────────────────────────
    def _smart_maximize(self):
        sw, sh = get_screen_size(self)

        # Center on startup first, then maximize
        cx = max(0, (sw - STARTUP_W) // 2)
        cy = max(0, (sh - STARTUP_H) // 2)
        self.geometry(f"{STARTUP_W}x{STARTUP_H}+{cx}+{cy}")
        self.update()

        # After 200ms, expand to full screen
        self.after(200, lambda: self._do_maximize(sw, sh))

    def _do_maximize(self, sw: int, sh: int):
        """
        Maximize strategy per environment:
        - Windows  → state(zoomed)  — uses taskbar-aware maximize
        - macOS    → attributes(-zoomed) — native full-screen
        - Linux    → geometry(WxH+0+0)
        - VNC      → geometry(WxH+0+0) — Xvfb full virtual screen
        """
        env = self._os_name
        if env == "windows":
            self.overrideredirect(False)   # restore chrome for Windows zoomed
            self.state("zoomed")
            self.overrideredirect(True)    # re-hide chrome
            self.state("normal")
            self.geometry(f"{sw}x{sh}+0+0")
        elif env == "macos":
            self.geometry(f"{sw}x{sh}+0+0")
        else:
            # Linux / VNC — directly set full virtual screen geometry
            self.geometry(f"{sw}x{sh}+0+0")

        self._tb.maximized = True
        self._tb._is_max   = True
        self._tb._prev_geo = f"{STARTUP_W}x{STARTUP_H}"

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_layout(self):
        # ── Custom title bar (OS-aware) ───────────────────────────────────────
        self._tb = TitleBar(self, window=self, cfg=self._tb_cfg,
                            colors=COLORS, title="NexPlorer v1.0.0")
        self._tb.pack(fill="x", side="top")

        # OS badge in title bar
        os_icons = {"windows":"🪟","macos":"🍎","linux":"🐧","vnc":"🖥️"}
        icon = os_icons.get(self._os_name, "🖥️")
        env_label = "VNC" if self._os_name == "vnc" else platform.system()
        ctk.CTkLabel(
            self._tb,
            text=f"{icon} {env_label}",
            font=("Segoe UI", 10),
            text_color=COLORS["muted"],
        ).pack(side="right" if self._tb_cfg["btn_side"] == "left" else "left",
               padx=16)

        # ── Body ──────────────────────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        body.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = ctk.CTkFrame(body, width=SIDEBAR_W,
                                    fg_color=COLORS["sidebar"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo.pack(fill="x", pady=(20,8), padx=16)
        ctk.CTkLabel(logo, text="🗂️", font=("Segoe UI Emoji", 32)).pack()
        ctk.CTkLabel(logo, text="NexPlorer",
                     font=("Segoe UI", 20, "bold"),
                     text_color=COLORS["accent"]).pack()
        ctk.CTkLabel(logo, text="v1.0.0",
                     font=("Segoe UI", 10),
                     text_color=COLORS["muted"]).pack()

        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["card"]).pack(
            fill="x", padx=16, pady=10)

        # Nav buttons
        self._nav_btns = {}
        for label, key in NAV_ITEMS:
            btn = ctk.CTkButton(
                self.sidebar, text=label,
                font=("Segoe UI", 13), anchor="w",
                fg_color="transparent", text_color=COLORS["text"],
                hover_color=COLORS["card"], corner_radius=8, height=42,
                command=lambda k=key: self._show_page(k)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self._nav_btns[key] = btn

        # System info at sidebar bottom
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(expand=True)
        env_info = "VNC / Xvfb" if is_vnc() else f"{platform.system()} {platform.release()}"
        ctk.CTkLabel(
            self.sidebar,
            text=f"{env_info}\nPython {sys.version[:6]}",
            font=("Segoe UI", 10), text_color=COLORS["muted"], justify="center"
        ).pack(pady=16)

        # Main content frame
        self.content = ctk.CTkFrame(body, fg_color=COLORS["bg"], corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        # Show default page
        self._show_page("explorer")

    # ── Page switching ─────────────────────────────────────────────────────────
    def _show_page(self, key: str):
        for w in self.content.winfo_children():
            w.pack_forget()

        # Highlight active nav
        for k, btn in self._nav_btns.items():
            btn.configure(fg_color=COLORS["card"] if k == key else "transparent")

        if key not in self._pages:
            cls = {
                "explorer":  ExplorerPage,
                "transfer":  TransferPage,
                "compress":  CompressPage,
                "vault":     VaultPage,
                "analytics": AnalyticsPage,
                "settings":  SettingsPage,
            }.get(key)
            if cls:
                self._pages[key] = cls(self.content, colors=COLORS)

        if key in self._pages:
            self._pages[key].pack(fill="both", expand=True)

    def _on_close(self):
        self.destroy()


def main():
    app = NexPlorerApp()
    app.mainloop()
