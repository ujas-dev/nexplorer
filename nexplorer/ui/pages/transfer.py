"""Transfer Page — copy/move with real-time speed meter + integrity gate"""
import threading, time
from pathlib import Path
import customtkinter as ctk
from nexplorer.core.transfer import safe_copy, safe_move
from nexplorer.core.drive    import detect_drive_type

def fmt_size(n):
    for u in ("B","KB","MB","GB","TB"):
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024


class TransferPage(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg"])
        self._c = colors
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="📦 Transfer",
                     font=("Segoe UI",22,"bold")).pack(pady=(24,4), padx=24, anchor="w")
        ctk.CTkLabel(self, text="Kernel-space copy · Atomic rename · Copy integrity gate",
                     font=("Segoe UI",12), text_color=self._c["muted"]
                     ).pack(padx=24, anchor="w")

        card = ctk.CTkFrame(self, fg_color=self._c["sidebar"], corner_radius=12)
        card.pack(fill="x", padx=24, pady=20)

        # Source
        sr = ctk.CTkFrame(card, fg_color="transparent")
        sr.pack(fill="x", padx=16, pady=(16,4))
        ctk.CTkLabel(sr, text="Source:", width=80).pack(side="left")
        self._src_var = ctk.StringVar()
        ctk.CTkEntry(sr, textvariable=self._src_var, width=500,
                     font=("Cascadia Code",11)).pack(side="left", padx=8)
        ctk.CTkButton(sr, text="Browse", width=90,
                      command=lambda: self._browse_src()).pack(side="left")

        # Destination
        dr = ctk.CTkFrame(card, fg_color="transparent")
        dr.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(dr, text="Destination:", width=80).pack(side="left")
        self._dst_var = ctk.StringVar()
        ctk.CTkEntry(dr, textvariable=self._dst_var, width=500,
                     font=("Cascadia Code",11)).pack(side="left", padx=8)
        ctk.CTkButton(dr, text="Browse", width=90,
                      command=lambda: self._browse_dst()).pack(side="left")

        # Options
        opts = ctk.CTkFrame(card, fg_color="transparent")
        opts.pack(fill="x", padx=16, pady=8)
        self._mode   = ctk.StringVar(value="copy")
        self._shred  = ctk.BooleanVar(value=False)
        self._dry    = ctk.BooleanVar(value=False)
        ctk.CTkRadioButton(opts, text="Copy", variable=self._mode, value="copy").pack(side="left",padx=8)
        ctk.CTkRadioButton(opts, text="Move", variable=self._mode, value="move").pack(side="left",padx=8)
        ctk.CTkCheckBox(opts, text="Shred source after move",
                        variable=self._shred).pack(side="left", padx=24)
        ctk.CTkCheckBox(opts, text="Dry Run",
                        variable=self._dry).pack(side="left", padx=12)

        # Drive info banner
        self._drive_info = ctk.StringVar(value="")
        ctk.CTkLabel(card, textvariable=self._drive_info,
                     font=("Segoe UI",11), text_color=self._c["warning"]
                     ).pack(padx=16, pady=4, anchor="w")

        # Progress
        self._prog = ctk.CTkProgressBar(card, width=700)
        self._prog.pack(padx=16, pady=8); self._prog.set(0)
        self._prog_lbl = ctk.StringVar(value="Ready")
        ctk.CTkLabel(card, textvariable=self._prog_lbl,
                     font=("Cascadia Code",11)).pack(padx=16, anchor="w", pady=(0,12))

        # Start button
        ctk.CTkButton(self, text="🚀 Start Transfer", height=44,
                      font=("Segoe UI",14,"bold"),
                      fg_color=self._c["accent"],
                      hover_color=self._c["accent2"],
                      command=self._start).pack(pady=8)

        self._result_box = ctk.CTkTextbox(self, font=("Cascadia Code",11),
                                          height=160, fg_color=self._c["sidebar"])
        self._result_box.pack(fill="x", padx=24, pady=8)

    def _browse_src(self):
        v = ctk.filedialog.askopenfilename()
        if v: self._src_var.set(v); self._update_drive_info()

    def _browse_dst(self):
        v = ctk.filedialog.askdirectory()
        if v: self._dst_var.set(v); self._update_drive_info()

    def _update_drive_info(self):
        src = self._src_var.get(); dst = self._dst_var.get()
        info = []
        if src: info.append(f"Source: {detect_drive_type(src).upper()}")
        if dst: info.append(f"Destination: {detect_drive_type(dst).upper()}")
        if src and dst:
            from nexplorer.core.drive import same_device
            from pathlib import Path as P
            sp = P(src)
            if sp.exists() and P(dst).exists():
                if same_device(sp, P(dst)):
                    info.append("✅ Same device — atomic rename (instant)")
                else:
                    info.append("🔄 Cross-device — kernel copy + integrity gate")
        self._drive_info.set("  |  ".join(info))

    def _start(self):
        src = Path(self._src_var.get()); dst = Path(self._dst_var.get())
        if not src.exists() or not dst:
            self._prog_lbl.set("❌ Invalid source or destination"); return
        self._prog.set(0); self._result_box.delete("1.0","end")

        def progress(done, total):
            if total:
                pct = done / total
                self.after(0, lambda: self._prog.set(pct))
                spd = ""
                self.after(0, lambda: self._prog_lbl.set(
                    f"{fmt_size(done)} / {fmt_size(total)}  {pct*100:.1f}%"))

        def run():
            mode = self._mode.get()
            dry  = self._dry.get()
            try:
                if mode == "copy":
                    r = safe_copy(src, dst, progress_cb=progress, dry_run=dry)
                else:
                    r = safe_move(src, dst, shred_source=self._shred.get(),
                                  progress_cb=progress, dry_run=dry)
                self.after(0, lambda: self._show_result(r))
            except Exception as e:
                self.after(0, lambda: self._prog_lbl.set(f"❌ {e}"))

        threading.Thread(target=run, daemon=True).start()

    def _show_result(self, r: dict):
        self._prog.set(1)
        lines = [f"Status  : {r.get('status','?').upper()}"]
        for k, v in r.items():
            if k != "status": lines.append(f"{k:14s}: {v}")
        self._result_box.insert("end", "\n".join(lines) + "\n")
        self._prog_lbl.set(f"✅ Done  —  Speed: {r.get('speed_mbps','?')} MB/s")
