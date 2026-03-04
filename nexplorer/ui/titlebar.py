"""
NexPlorer Custom Title Bar
- Renders native-style window controls per OS (Windows / macOS traffic light / Linux)
- Supports window drag, minimize, maximize/restore, close
- Works inside VNC where OS window manager is absent
"""
import sys
import customtkinter as ctk

class TitleBar(ctk.CTkFrame):
    """
    Drop-in custom title bar.
    Pass `window` = the CTk root, `cfg` = get_title_bar_config() result.
    """
    def __init__(self, parent, window, cfg: dict, colors: dict, title: str = "NexPlorer"):
        super().__init__(parent, height=cfg["btn_height"] + 8,
                         fg_color=colors["sidebar"], corner_radius=0)
        self.pack_propagate(False)
        self._win      = window
        self._cfg      = cfg
        self._colors   = colors
        self._is_max   = False
        self._prev_geo = None
        self._drag_x   = self._drag_y = 0
        self._build(title)

    def _build(self, title: str):
        cfg = self._cfg

        # ── macOS: buttons LEFT, then title center ────────────────────────
        if cfg["btn_side"] == "left":
            self._build_buttons_left(cfg)
            ctk.CTkLabel(self, text=f" {title}",
                         font=("SF Pro Display" if sys.platform == "darwin"
                               else "Segoe UI", 12),
                         text_color=self._colors["muted"],
                         anchor="w").pack(side="left", padx=8)
        else:
            # ── Windows/Linux/VNC: title LEFT, buttons RIGHT ──────────────
            ctk.CTkLabel(self, text=f"  🗂️  {title}",
                         font=("Segoe UI", 12),
                         text_color=self._colors["text"],
                         anchor="w").pack(side="left", padx=8)
            self._build_buttons_right(cfg)

        # Enable window drag via title bar
        if cfg["drag_allowed"]:
            self.bind("<ButtonPress-1>",   self._on_drag_start)
            self.bind("<B1-Motion>",       self._on_drag)
            self.bind("<Double-Button-1>", self._toggle_maximize)

    def _btn(self, parent, icon, color, hover, action, w, h, radius):
        btn = ctk.CTkButton(
            parent,
            text=icon,
            width=w, height=h,
            fg_color=color,
            hover_color=hover,
            text_color="#ffffff",
            font=("Segoe UI", 10),
            corner_radius=radius,
            command=action,
        )
        return btn

    def _build_buttons_left(self, cfg):
        """macOS traffic light: close · min · max"""
        frm = ctk.CTkFrame(self, fg_color="transparent")
        frm.pack(side="left", padx=8, pady=4)
        sz = cfg["btn_size"]; h = cfg["btn_height"]; r = cfg["btn_radius"]
        self._btn(frm, cfg["icon_close"], cfg["close_color"],
                  cfg["hover_close"], self._close, sz, h, r).pack(side="left", padx=3)
        self._btn(frm, cfg["icon_min"],   cfg["min_color"],
                  cfg["hover_min"],   self._minimize, sz, h, r).pack(side="left", padx=3)
        self._max_btn = self._btn(frm, cfg["icon_max"], cfg["max_color"],
                  cfg["hover_max"], self._toggle_maximize, sz, h, r)
        self._max_btn.pack(side="left", padx=3)

    def _build_buttons_right(self, cfg):
        """Windows/Linux: min · max · close, right-aligned"""
        frm = ctk.CTkFrame(self, fg_color="transparent")
        frm.pack(side="right", padx=4, pady=4)
        sz = cfg["btn_size"]; h = cfg["btn_height"]; r = cfg["btn_radius"]
        self._btn(frm, cfg["icon_min"],   cfg["min_color"],
                  cfg["hover_min"],   self._minimize, sz, h, r).pack(side="left", padx=2)
        self._max_btn = self._btn(frm, cfg["icon_max"], cfg["max_color"],
                  cfg["hover_max"], self._toggle_maximize, sz, h, r)
        self._max_btn.pack(side="left", padx=2)
        self._btn(frm, cfg["icon_close"], cfg["close_color"],
                  cfg["hover_close"], self._close, sz, h, r).pack(side="left", padx=2)

    # ── Window actions ────────────────────────────────────────────────────────
    def _close(self):
        self._win.destroy()

    def _minimize(self):
        self._win.iconify()

    def _toggle_maximize(self, event=None):
        if not self._is_max:
            self._prev_geo = self._win.geometry()
            # Platform-specific maximize
            import platform
            if platform.system() == "Windows":
                self._win.state("zoomed")
            elif platform.system() == "Darwin":
                self._win.attributes("-zoomed", True)
            else:
                # Linux / VNC — get full screen dims and set geometry manually
                sw = self._win.winfo_screenwidth()
                sh = self._win.winfo_screenheight()
                self._win.geometry(f"{sw}x{sh}+0+0")
            self._is_max = True
            self._max_btn.configure(text=self._cfg["icon_restore"])
        else:
            import platform
            if platform.system() == "Windows":
                self._win.state("normal")
            elif platform.system() == "Darwin":
                self._win.attributes("-zoomed", False)
            else:
                if self._prev_geo:
                    self._win.geometry(self._prev_geo)
            self._is_max = False
            self._max_btn.configure(text=self._cfg["icon_max"])

    # ── Drag ─────────────────────────────────────────────────────────────────
    def _on_drag_start(self, e):
        self._drag_x = e.x_root - self._win.winfo_x()
        self._drag_y = e.y_root - self._win.winfo_y()

    def _on_drag(self, e):
        if not self._is_max:
            self._win.geometry(
                f"+{e.x_root - self._drag_x}+{e.y_root - self._drag_y}"
            )
