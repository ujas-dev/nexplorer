"""NexPlorer — Settings Page"""
import customtkinter as ctk
class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, colors):
        super().__init__(parent, fg_color=colors["bg"])
        self._c = colors; self._build()
    def _build(self):
        ctk.CTkLabel(self, text="⚙️ Settings",
            font=("Segoe UI",22,"bold")).pack(pady=(24,4),padx=24,anchor="w")
        ctk.CTkLabel(self, text="Themes · Exclude patterns · Default algorithms · EXIF rules",
            font=("Segoe UI",12), text_color=self._c["muted"]
            ).pack(padx=24,anchor="w")
        ctk.CTkLabel(self,
            text="🚧  Full UI coming in v1.1.0 — core engine already wired",
            font=("Segoe UI",14), text_color=self._c["muted"]
            ).pack(expand=True)
