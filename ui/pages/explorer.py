"""
NexPlorer — Explorer Page
Left: folder tree  |  Right: file list with metadata strip + action bar
"""
import os, threading
from pathlib import Path
from datetime import datetime

import customtkinter as ctk

from nexplorer.core.scanner  import Scanner
from nexplorer.core.metadata import read as read_meta
from nexplorer.core.transfer import safe_copy, safe_move, shred
from nexplorer.core.drive    import list_drives

COLORS = {}   # injected by App


def fmt_size(n):
    for u in ("B","KB","MB","GB","TB"):
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"

def fmt_mtime(t):
    return datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M")


class ExplorerPage(ctk.CTkFrame):
    def __init__(self, parent, colors: dict):
        global COLORS; COLORS = colors
        super().__init__(parent, fg_color=colors["bg"])
        self._current_path = Path.home()
        self._scan_result  = None
        self._selected     = None
        self._build()
        self._scan(self._current_path)

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        # ── Top bar: drives + path
        top = ctk.CTkFrame(self, fg_color=COLORS["sidebar"], corner_radius=8)
        top.pack(fill="x", padx=16, pady=(16,8))

        ctk.CTkLabel(top, text="📍", font=("Segoe UI",13)).pack(side="left",padx=(12,4))
        self._path_var = ctk.StringVar(value=str(self._current_path))
        self._path_entry = ctk.CTkEntry(top, textvariable=self._path_var,
                                        font=("Cascadia Code",12), width=600)
        self._path_entry.pack(side="left", padx=4, pady=8)
        self._path_entry.bind("<Return>", lambda e: self._navigate(self._path_var.get()))

        ctk.CTkButton(top, text="Go", width=60,
                      command=lambda: self._navigate(self._path_var.get())
                      ).pack(side="left", padx=4)
        ctk.CTkButton(top, text="⬆ Up", width=70,
                      command=self._go_up).pack(side="left", padx=4)
        ctk.CTkButton(top, text="🏠 Home", width=80,
                      command=lambda: self._navigate(str(Path.home()))
                      ).pack(side="left", padx=4)

        # Drive chips
        drives_frame = ctk.CTkFrame(top, fg_color="transparent")
        drives_frame.pack(side="right", padx=12)
        for d in list_drives()[:5]:
            lbl = f"{d['mountpoint']} ({fmt_size(d['free'])} free)"
            ctk.CTkButton(
                drives_frame, text=lbl, width=180, height=28,
                font=("Segoe UI",10), fg_color=COLORS["card"],
                corner_radius=6,
                command=lambda mp=d["mountpoint"]: self._navigate(mp)
            ).pack(side="left", padx=4)

        # ── Split pane: file list | detail panel
        split = ctk.CTkFrame(self, fg_color="transparent")
        split.pack(fill="both", expand=True, padx=16, pady=8)

        # File list (scrollable)
        list_frame = ctk.CTkFrame(split, fg_color=COLORS["sidebar"], corner_radius=8)
        list_frame.pack(side="left", fill="both", expand=True)

        # Column headers
        hdr = ctk.CTkFrame(list_frame, fg_color=COLORS["card"], corner_radius=0, height=36)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        for col, w in [("Name",360),("Size",90),("Type",90),("Modified",160)]:
            ctk.CTkLabel(hdr, text=col, width=w, font=("Segoe UI",11,"bold"),
                         anchor="w").pack(side="left", padx=8)

        scroll = ctk.CTkScrollableFrame(list_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        self._list_frame = scroll
        self._rows = []

        # Status bar
        self._status_var = ctk.StringVar(value="Ready")
        ctk.CTkLabel(list_frame, textvariable=self._status_var,
                     font=("Segoe UI",10), text_color=COLORS["muted"],
                     anchor="w").pack(fill="x", padx=12, pady=6)

        # Detail / action panel
        detail = ctk.CTkFrame(split, fg_color=COLORS["sidebar"], corner_radius=8, width=300)
        detail.pack(side="right", fill="y", padx=(12,0))
        detail.pack_propagate(False)
        self._detail = detail
        ctk.CTkLabel(detail, text="File Details",
                     font=("Segoe UI",14,"bold")).pack(pady=(16,8))
        self._detail_text = ctk.CTkTextbox(detail, font=("Cascadia Code",11),
                                           fg_color=COLORS["bg"], state="disabled")
        self._detail_text.pack(fill="both", expand=True, padx=12, pady=8)

        # Action buttons
        for label, fn in [
            ("📋 Copy",    self._action_copy),
            ("✂️ Move",    self._action_move),
            ("🗑️ Shred",   self._action_shred),
            ("ℹ️ Metadata",self._action_meta),
        ]:
            ctk.CTkButton(detail, text=label, height=36,
                          command=fn).pack(fill="x", padx=12, pady=4)

    # ── Navigation ────────────────────────────────────────────────────────────
    def _navigate(self, path: str):
        p = Path(path)
        if p.is_dir():
            self._current_path = p
            self._path_var.set(str(p))
            self._scan(p)
        elif p.is_file():
            self._show_meta(p)

    def _go_up(self):
        self._navigate(str(self._current_path.parent))

    # ── Scanner ───────────────────────────────────────────────────────────────
    def _scan(self, path: Path):
        self._status_var.set("Scanning…")
        for row in self._rows: row.destroy()
        self._rows.clear()
        Scanner(path,
                progress_cb=lambda n,name: self._status_var.set(f"Scanning… {n} files  {name}"),
                done_cb=lambda r: self.after(0, lambda: self._on_scan_done(r))
                ).start()

    def _on_scan_done(self, result):
        if "error" in result:
            self._status_var.set(f"Error: {result['error']}"); return
        self._scan_result = result
        nodes = result["nodes"]
        for node in nodes:
            row = ctk.CTkFrame(self._list_frame, fg_color="transparent",
                               cursor="hand2", height=32)
            row.pack(fill="x"); row.pack_propagate(False)
            icon = "📁" if node.is_dir else "📄"
            ctk.CTkLabel(row, text=f"{icon} {node.name}", width=360,
                         font=("Segoe UI",11), anchor="w").pack(side="left",padx=8)
            ctk.CTkLabel(row, text=fmt_size(node.size) if not node.is_dir else "—",
                         width=90, font=("Segoe UI",11), anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=node.category, width=90,
                         font=("Segoe UI",11), anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=fmt_mtime(node.mtime), width=160,
                         font=("Segoe UI",11), anchor="w").pack(side="left")
            row.bind("<Button-1>", lambda e, n=node: self._select(n))
            row.bind("<Double-Button-1>", lambda e, n=node: self._open(n))
            self._rows.append(row)
        total_files = result["total_files"]
        total_size  = fmt_size(result["total_size"])
        self._status_var.set(
            f"{total_files} files  |  {result['total_dirs']} folders  |  {total_size} total"
        )

    # ── Selection / detail ────────────────────────────────────────────────────
    def _select(self, node):
        self._selected = node
        self._show_meta(node.path)

    def _open(self, node):
        if node.is_dir: self._navigate(str(node.path))
        else:
            import subprocess, sys
            try:
                if sys.platform=="win32": os.startfile(str(node.path))
                elif sys.platform=="darwin": subprocess.Popen(["open",str(node.path)])
                else: subprocess.Popen(["xdg-open",str(node.path)])
            except Exception: pass

    def _show_meta(self, fp: Path):
        meta = read_meta(fp)
        text = "\n".join(f"{k:18s}: {v}" for k,v in meta.items() if v)
        self._detail_text.configure(state="normal")
        self._detail_text.delete("1.0","end")
        self._detail_text.insert("1.0", text)
        self._detail_text.configure(state="disabled")

    # ── Actions ───────────────────────────────────────────────────────────────
    def _action_copy(self):
        if not self._selected: return
        dst = ctk.filedialog.askdirectory(title="Copy to…")
        if dst:
            threading.Thread(target=lambda:
                safe_copy(self._selected.path, Path(dst)), daemon=True).start()

    def _action_move(self):
        if not self._selected: return
        dst = ctk.filedialog.askdirectory(title="Move to…")
        if dst:
            threading.Thread(target=lambda:
                safe_move(self._selected.path, Path(dst)), daemon=True).start()

    def _action_shred(self):
        if not self._selected: return
        ok = ctk.messagebox.askyesno(
            "Confirm Shred",
            f"Permanently shred:\n{self._selected.path}\n\nThis CANNOT be undone."
        )
        if ok:
            threading.Thread(target=lambda:
                shred(self._selected.path, passes=7), daemon=True).start()

    def _action_meta(self):
        if not self._selected: self._status_var.set("Select a file first")
        else: self._show_meta(self._selected.path)
