import sys
import datetime
import customtkinter as ctk
from typing import Optional

from nifrap.config import DEFAULT_HEADERS, DEFAULT_TIMEOUT


class SettingsView(ctk.CTkFrame):
    """System Diagnostics and Real-time Activity Log View."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._build_layout()

    def _build_layout(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Top: Diagnostics & Config
        top_frame = ctk.CTkFrame(container, fg_color=("#222222", "#1a1a1a"), corner_radius=8, border_width=1, border_color="#333333")
        top_frame.pack(fill="x", pady=(0, 15))

        lbl_top = ctk.CTkLabel(top_frame, text="System Environment & Configuration", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_top.pack(anchor="w", padx=15, pady=(12, 6))

        # Check Scapy
        try:
            import scapy.all as scapy
            scapy_status = f"Available (Scapy {scapy.__version__})"
            scapy_color = "#2ecc71"
        except Exception:
            scapy_status = "Not installed"
            scapy_color = "#e74c3c"

        diag_text = (
            f"• Python Version: {sys.version.split()[0]} ({sys.platform})\n"
            f"• Packet Sniffing Engine: {scapy_status}\n"
            f"• Network Sniffing Mode: Scapy Native / Multi-Threaded Capture with Fallback Simulation\n"
            f"• Default Request Timeout: {DEFAULT_TIMEOUT}s\n"
            f"• User-Agent: {DEFAULT_HEADERS['User-Agent'][:60]}..."
        )
        lbl_diag = ctk.CTkLabel(top_frame, text=diag_text, font=ctk.CTkFont(size=11), text_color="#bbbbbb", justify="left")
        lbl_diag.pack(anchor="w", padx=15, pady=(0, 12))

        # Bottom: Activity Log Console
        log_frame = ctk.CTkFrame(container, fg_color=("#222222", "#1a1a1a"), corner_radius=8, border_width=1, border_color="#333333")
        log_frame.pack(fill="both", expand=True)

        header_bar = ctk.CTkFrame(log_frame, fg_color="transparent")
        header_bar.pack(fill="x", padx=15, pady=10)

        lbl_log = ctk.CTkLabel(header_bar, text="Real-time Activity & Pipeline Console", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_log.pack(side="left")

        btn_clear = ctk.CTkButton(header_bar, text="Clear Console", width=100, height=28, fg_color="#3a3a3a", hover_color="#505050", command=self.clear_logs)
        btn_clear.pack(side="right")

        self.log_textbox = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="Consolas", size=10), wrap="none")
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def log(self, message: str, level: str = "INFO"):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        prefix = f"[{ts}] [{level}] "
        self.log_textbox.insert("end", prefix + message + "\n")
        self.log_textbox.see("end")

    def clear_logs(self):
        self.log_textbox.delete("1.0", "end")

