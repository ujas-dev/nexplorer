"""
NexPlorer v1.0.0 — Main Application Window
Dark-themed CustomTkinter GUI. Sidebar nav → pages swapped into main frame.
Run: python -m nexplorer
"""
import threading, os, platform, sys
from pathlib import Path

import customtkinter as ctk

from nexplorer.ui.pages.explorer  import ExplorerPage
from nexplorer.ui.pages.transfer  import TransferPage
from nexplorer.ui.pages.compress  import CompressPage
from nexplorer.ui.pages.vault     import VaultPage
from nexplorer.ui.pages.analytics import AnalyticsPage
from nexplorer.ui.pages.settings  import SettingsPage

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

NAV_ITEMS = [
    ("🗂️  Explorer",    "explorer"),
    ("📦  Transfer",    "transfer"),
    ("🗜️  Compress",    "compress"),
    ("🔐  Vault",       "vault"),
    ("📊  Analytics",   "analytics"),
    ("⚙️  Settings",    "settings"),
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
}


class NexPlorerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🗂️ NexPlorer v1.0.0")
        self.geometry("1400x860")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["bg"])

        self._pages: dict = {}
        self._active_nav = ctk.StringVar(value="explorer")
        self._build_layout()
        self._show_page("explorer")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Layout ───────────────────────────────────────────────────────────────
    def _build_layout(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=COLORS["sidebar"],
                                    corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(24,8), padx=16)
        ctk.CTkLabel(logo_frame, text="🗂️", font=("Segoe UI Emoji",36)).pack()
        ctk.CTkLabel(logo_frame, text="NexPlorer",
                     font=("Segoe UI",20,"bold"),
                     text_color=COLORS["accent"]).pack()
        ctk.CTkLabel(logo_frame, text="v1.0.0",
                     font=("Segoe UI",11),
                     text_color=COLORS["muted"]).pack()

        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["card"]).pack(
            fill="x", padx=16, pady=12)

        # Nav buttons
        for label, key in NAV_ITEMS:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                font=("Segoe UI", 13),
                anchor="w",
                fg_color="transparent",
                text_color=COLORS["text"],
                hover_color=COLORS["card"],
                corner_radius=8,
                height=42,
                command=lambda k=key: self._show_page(k)
            )
            btn.pack(fill="x", padx=12, pady=2)

        # OS info at bottom of sidebar
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(expand=True)
        os_lbl = ctk.CTkLabel(
            self.sidebar,
            text=f"{platform.system()} {platform.release()}\nPython {sys.version[:6]}",
            font=("Segoe UI",10),
            text_color=COLORS["muted"],
            justify="center",
        )
        os_lbl.pack(pady=16)

        # Main content area
        self.content = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

    # ── Page switching ────────────────────────────────────────────────────────
    def _show_page(self, key: str):
        for w in self.content.winfo_children():
            w.pack_forget()
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
        self._active_nav.set(key)

    def _on_close(self):
        self.destroy()


def main():
    app = NexPlorerApp()
    app.mainloop()
