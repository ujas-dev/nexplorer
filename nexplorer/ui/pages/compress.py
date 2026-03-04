"""NexPlorer — Compress Page — full algorithm picker + smart auto-select"""
import threading
from pathlib import Path
import customtkinter as ctk
from nexplorer.core.compressor import compress, decompress, smart_algorithm
from nexplorer.core.constants  import COMPRESSORS

def fmt_size(n):
    for u in ("B","KB","MB","GB","TB"):
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024

class CompressPage(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg"])
        self._c = colors; self._build()

    def _build(self):
        ctk.CTkLabel(self, text="🗜️ Compress / Decompress",
                     font=("Segoe UI",22,"bold")).pack(pady=(24,4),padx=24,anchor="w")
        ctk.CTkLabel(self, text="11 algorithms · Smart auto-select · Progress meter",
                     font=("Segoe UI",12), text_color=self._c["muted"]
                     ).pack(padx=24, anchor="w")

        card = ctk.CTkFrame(self, fg_color=self._c["sidebar"], corner_radius=12)
        card.pack(fill="x", padx=24, pady=20)

        # Source file
        sr = ctk.CTkFrame(card, fg_color="transparent")
        sr.pack(fill="x", padx=16, pady=(16,4))
        ctk.CTkLabel(sr, text="File:", width=100).pack(side="left")
        self._src_var = ctk.StringVar()
        ctk.CTkEntry(sr, textvariable=self._src_var, width=480,
                     font=("Cascadia Code",11)).pack(side="left", padx=8)
        ctk.CTkButton(sr, text="Browse", width=90,
                      command=lambda: self._browse()).pack(side="left")

        # Algorithm selector
        ar = ctk.CTkFrame(card, fg_color="transparent")
        ar.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(ar, text="Algorithm:", width=100).pack(side="left")
        self._algo_var = ctk.StringVar(value="auto")
        algo_choices = ["auto"] + list(COMPRESSORS.keys())
        ctk.CTkOptionMenu(ar, variable=self._algo_var, values=algo_choices,
                          command=self._on_algo_change, width=180
                          ).pack(side="left", padx=8)
        self._algo_info = ctk.StringVar(value="Auto-select best algorithm for this file type")
        ctk.CTkLabel(ar, textvariable=self._algo_info,
                     font=("Segoe UI",11), text_color=self._c["muted"]
                     ).pack(side="left", padx=12)

        # Priority
        pr = ctk.CTkFrame(card, fg_color="transparent")
        pr.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(pr, text="Priority:", width=100).pack(side="left")
        self._priority = ctk.StringVar(value="balanced")
        for v, lbl in [("speed","⚡ Speed"),("balanced","⚖️ Balanced"),("max_ratio","🗜️ Max Ratio")]:
            ctk.CTkRadioButton(pr, text=lbl, variable=self._priority, value=v
                               ).pack(side="left", padx=12)

        # Dry run + password
        ex = ctk.CTkFrame(card, fg_color="transparent")
        ex.pack(fill="x", padx=16, pady=4)
        self._dry  = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(ex, text="Dry Run", variable=self._dry).pack(side="left",padx=8)
        ctk.CTkLabel(ex, text="Password (7z/zip):", width=140).pack(side="left",padx=16)
        self._pwd_var = ctk.StringVar()
        ctk.CTkEntry(ex, textvariable=self._pwd_var, show="*", width=180).pack(side="left")

        # Progress
        self._prog = ctk.CTkProgressBar(card, width=700)
        self._prog.pack(padx=16, pady=8); self._prog.set(0)
        self._prog_lbl = ctk.StringVar(value="Ready")
        ctk.CTkLabel(card, textvariable=self._prog_lbl,
                     font=("Cascadia Code",11)).pack(padx=16, anchor="w", pady=(0,12))

        # Buttons
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(pady=8)
        ctk.CTkButton(btns, text="🗜️ Compress", height=44, width=200,
                      font=("Segoe UI",13,"bold"),
                      fg_color=self._c["accent"],
                      command=self._compress).pack(side="left", padx=12)
        ctk.CTkButton(btns, text="📂 Decompress", height=44, width=200,
                      font=("Segoe UI",13,"bold"),
                      fg_color=self._c["card"],
                      command=self._decompress).pack(side="left", padx=12)

        # Result
        self._result_box = ctk.CTkTextbox(self, font=("Cascadia Code",11),
                                          height=140, fg_color=self._c["sidebar"])
        self._result_box.pack(fill="x", padx=24, pady=8)

    def _browse(self):
        v = ctk.filedialog.askopenfilename()
        if v:
            self._src_var.set(v)
            algo = smart_algorithm(Path(v), self._priority.get())
            if self._algo_var.get() == "auto":
                info = COMPRESSORS.get(algo,{})
                self._algo_info.set(
                    f"Recommended: {algo}  {info.get('speed','')} speed  "
                    f"{info.get('ratio','')} ratio  — {info.get('best_for','')}"
                )

    def _on_algo_change(self, v):
        info = COMPRESSORS.get(v,{})
        if info:
            self._algo_info.set(
                f"{info['speed']} speed  {info['ratio']} ratio  — {info['best_for']}"
            )
        else:
            self._algo_info.set("Auto-select best algorithm for this file type")

    def _compress(self):
        src = Path(self._src_var.get())
        if not src.exists(): self._prog_lbl.set("❌ Select a file first"); return
        self._prog.set(0); self._result_box.delete("1.0","end")
        algo = self._algo_var.get()
        if algo == "auto": algo = "auto"

        def progress(done, total):
            if total:
                self.after(0, lambda: self._prog.set(done/total))
                self.after(0, lambda: self._prog_lbl.set(f"Compressing… {done/total*100:.1f}%"))

        def run():
            try:
                r = compress(src, algorithm=algo, priority=self._priority.get(),
                             password=self._pwd_var.get() or None,
                             progress_cb=progress, dry_run=self._dry.get())
                self.after(0, lambda: self._show_result(r))
            except Exception as e:
                self.after(0, lambda: self._prog_lbl.set(f"❌ {e}"))
        threading.Thread(target=run, daemon=True).start()

    def _decompress(self):
        src = Path(self._src_var.get())
        if not src.exists(): self._prog_lbl.set("❌ Select a file first"); return
        dst = ctk.filedialog.askdirectory(title="Extract to…")
        if not dst: return
        def run():
            try:
                r = decompress(src, Path(dst), password=self._pwd_var.get() or None)
                self.after(0, lambda: self._show_result(r))
            except Exception as e:
                self.after(0, lambda: self._prog_lbl.set(f"❌ {e}"))
        threading.Thread(target=run, daemon=True).start()

    def _show_result(self, r: dict):
        self._prog.set(1)
        lines = [f"{k:20s}: {v}" for k,v in r.items()]
        self._result_box.insert("end", "\n".join(lines)+"\n")
        self._prog_lbl.set("✅ Done")
