import os
import sys
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from nifrap.config import EXPORTS_DIR
from nifrap.core.pipeline import NifrapPipeline
from nifrap.core.sniffer import get_network_interfaces
from nifrap.gui.views.sniffer_view import SnifferView
from nifrap.gui.views.scraper_view import ScraperView
from nifrap.gui.views.export_view import ExportView
from nifrap.gui.views.settings_view import SettingsView


class NifrapApp(ctk.CTk):
    """Main Application Window for NIFRAP 2.0."""

    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("NIFRAP 2.0 - Network Intelligence & Automated Web Scraper")
        self.geometry("1220x760")
        self.minsize(1040, 660)

        # Apply Modern Dark Theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Session Metrics
        self.total_packets_count = 0
        self.web_packets_count = 0
        self.scraped_targets_count = 0

        # Initialize Pipeline
        self.pipeline = NifrapPipeline(
            on_packet=self._on_packet_event,
            on_web_target=self._on_web_target_event,
            on_scrape_start=self._on_scrape_start_event,
            on_scrape_done=self._on_scrape_done_event,
            on_status=self._on_status_event,
            on_error=self._on_error_event,
        )

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _build_ui(self):
        # Configure Grid Layout (Sidebar: Col 0, Content: Col 1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_content_area()

        # Select initial view
        self._select_view("sniffer")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=("#1f1f1f", "#141414"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(9, weight=1)

        # Brand / Title
        logo_label = ctk.CTkLabel(
            self.sidebar,
            text="🛡️ NIFRAP 2.0",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffffff",
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 2), sticky="w")

        sub_label = ctk.CTkLabel(
            self.sidebar,
            text="Packet Sniffer & Web Intelligence",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        )
        sub_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # Navigation Buttons
        self.nav_btns = {}
        views = [
            ("sniffer", "📡 Live Sniffer"),
            ("scraper", "🌐 Web Scraper"),
            ("exports", "💾 Storage & Export"),
            ("settings", "⚙️ Activity Log"),
        ]
        for idx, (key, label) in enumerate(views, start=2):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                height=38,
                corner_radius=6,
                fg_color="transparent",
                text_color=("#d0d0d0", "#d0d0d0"),
                hover_color=("#2c2c2c", "#2c2c2c"),
                anchor="w",
                command=lambda k=key: self._select_view(k),
            )
            btn.grid(row=idx, column=0, padx=15, pady=4, sticky="ew")
            self.nav_btns[key] = btn

        # Divider
        divider = ctk.CTkFrame(self.sidebar, height=1, fg_color="#2c2c2c")
        divider.grid(row=6, column=0, padx=20, pady=15, sticky="ew")

        # Network Controls Section
        ctl_label = ctk.CTkLabel(
            self.sidebar,
            text="CAPTURE CONTROLS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#777777",
        )
        ctl_label.grid(row=7, column=0, padx=20, pady=(0, 5), sticky="w")

        # Interface Selector
        interfaces = get_network_interfaces()
        self.iface_map = {item["display"]: item["name"] for item in interfaces}
        iface_options = list(self.iface_map.keys()) or ["Default Interface"]

        self.iface_dropdown = ctk.CTkOptionMenu(
            self.sidebar,
            values=iface_options,
            height=30,
            font=ctk.CTkFont(size=11),
            dropdown_font=ctk.CTkFont(size=11),
        )
        self.iface_dropdown.grid(row=8, column=0, padx=15, pady=(0, 8), sticky="ew")

        # Auto-Scrape Switch
        self.auto_scrape_var = tk.BooleanVar(value=True)
        self.auto_scrape_switch = ctk.CTkSwitch(
            self.sidebar,
            text="Auto-Scrape Web Packets",
            variable=self.auto_scrape_var,
            font=ctk.CTkFont(size=11),
            command=self._on_toggle_auto_scrape,
        )
        self.auto_scrape_switch.grid(row=9, column=0, padx=18, pady=(0, 15), sticky="nw")

        # Control Buttons
        self.btn_capture = ctk.CTkButton(
            self.sidebar,
            text="▶ Start Sniffing",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            corner_radius=6,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            text_color="#ffffff",
            command=self._toggle_capture,
        )
        self.btn_capture.grid(row=10, column=0, padx=15, pady=6, sticky="ew")

        self.btn_simulation = ctk.CTkButton(
            self.sidebar,
            text="⚡ Demo Simulation",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=34,
            corner_radius=6,
            fg_color="#8e44ad",
            hover_color="#732d91",
            text_color="#ffffff",
            command=self._start_simulation,
        )
        self.btn_simulation.grid(row=11, column=0, padx=15, pady=(0, 20), sticky="ew")

    def _build_content_area(self):
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#181818", "#121212"))
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # Instantiate View Frames
        self.view_sniffer = SnifferView(self.content_frame, on_scrape_request=self._handle_manual_scrape)
        self.view_scraper = ScraperView(self.content_frame, on_scrape_request=self._handle_manual_scrape)
        self.view_export = ExportView(
            self.content_frame,
            get_session_data_cb=self._get_session_data,
            on_clear_session_cb=self._clear_session_data,
        )
        self.view_settings = SettingsView(self.content_frame)

        self.views = {
            "sniffer": self.view_sniffer,
            "scraper": self.view_scraper,
            "exports": self.view_export,
            "settings": self.view_settings,
        }

    def _select_view(self, view_name: str):
        for name, view in self.views.items():
            if name == view_name:
                view.pack(fill="both", expand=True)
                self.nav_btns[name].configure(fg_color=("#2b5b84", "#1f538d"), text_color="#ffffff")
            else:
                view.pack_forget()
                self.nav_btns[name].configure(fg_color="transparent", text_color=("#d0d0d0", "#d0d0d0"))

    def _toggle_capture(self):
        if self.pipeline.sniffer.is_running:
            self.pipeline.stop_sniffing()
            self.btn_capture.configure(text="▶ Start Sniffing", fg_color="#2ecc71", hover_color="#27ae60")
            self.btn_simulation.configure(state="normal")
            self.view_sniffer.update_metrics(
                self.total_packets_count,
                self.web_packets_count,
                self.scraped_targets_count,
                "IDLE",
                "#7f8c8d",
            )
        else:
            selected_display = self.iface_dropdown.get()
            selected_iface = self.iface_map.get(selected_display)
            self.pipeline.start_sniffing(interface=selected_iface)
            self.btn_capture.configure(text="⏹ Stop Sniffing", fg_color="#e74c3c", hover_color="#c0392b")
            self.btn_simulation.configure(state="disabled")
            self.view_sniffer.update_metrics(
                self.total_packets_count,
                self.web_packets_count,
                self.scraped_targets_count,
                "SNIFFING",
                "#2ecc71",
            )

    def _start_simulation(self):
        if self.pipeline.sniffer.is_running:
            self.pipeline.stop_sniffing()
            self.btn_capture.configure(text="▶ Start Sniffing", fg_color="#2ecc71", hover_color="#27ae60", state="normal")
            self.btn_simulation.configure(text="⚡ Demo Simulation", fg_color="#8e44ad")
            self.view_sniffer.update_metrics(
                self.total_packets_count,
                self.web_packets_count,
                self.scraped_targets_count,
                "IDLE",
                "#7f8c8d",
            )
        else:
            self.pipeline.start_simulation()
            self.btn_simulation.configure(text="⏹ Stop Demo", fg_color="#e74c3c")
            self.btn_capture.configure(state="disabled")
            self.view_sniffer.update_metrics(
                self.total_packets_count,
                self.web_packets_count,
                self.scraped_targets_count,
                "SIMULATION",
                "#9b59b6",
            )

    def _on_toggle_auto_scrape(self):
        self.pipeline.auto_scrape_enabled = self.auto_scrape_var.get()
        self.view_settings.log(f"Auto-scrape toggle set to: {self.pipeline.auto_scrape_enabled}")

    def _handle_manual_scrape(self, url: str):
        self.view_settings.log(f"Initiating targeted scrape for: {url}")
        self.pipeline.scrape_target(url)
        self._select_view("scraper")

    # Pipeline Event Handlers (Dispatched smoothly to GUI thread)
    def _on_packet_event(self, packet):
        self.total_packets_count += 1
        if packet.is_web:
            self.web_packets_count += 1

        self.after(0, lambda: self._update_packet_ui(packet))

    def _update_packet_ui(self, packet):
        self.view_sniffer.add_packet(packet)
        status_text = "SNIFFING" if self.pipeline.sniffer.mode == "live" else ("SIMULATION" if self.pipeline.sniffer.mode == "simulation" else "IDLE")
        status_color = "#2ecc71" if status_text == "SNIFFING" else ("#9b59b6" if status_text == "SIMULATION" else "#7f8c8d")
        self.view_sniffer.update_metrics(
            self.total_packets_count,
            self.web_packets_count,
            self.scraped_targets_count,
            status_text,
            status_color,
        )

    def _on_web_target_event(self, target_info):
        self.after(0, lambda: self.view_scraper.add_target(target_info))
        self.view_settings.log(f"Discovered Web Target: {target_info.get('url')} [{target_info.get('web_type')}]", "DISCOVERY")

    def _on_scrape_start_event(self, url):
        self.view_settings.log(f"Scraper worker started for: {url}", "SCRAPE")

    def _on_scrape_done_event(self, scraped_data):
        self.scraped_targets_count += 1
        self.after(0, lambda: self.view_scraper.on_scrape_completed(scraped_data))
        self.view_settings.log(f"Successfully scraped: {scraped_data.url} (Status {scraped_data.status_code}, Found {len(scraped_data.links)} links, {len(scraped_data.images)} images)", "SUCCESS")

    def _on_status_event(self, msg):
        self.after(0, lambda: self.view_settings.log(msg, "STATUS"))

    def _on_error_event(self, error_msg):
        self.after(0, lambda: self.view_settings.log(error_msg, "ERROR"))

    def _get_session_data(self):
        return self.pipeline.all_packets, self.pipeline.scraped_results

    def _clear_session_data(self):
        self.pipeline.clear_session()
        self.total_packets_count = 0
        self.web_packets_count = 0
        self.scraped_targets_count = 0
        self.view_sniffer.clear_table()
        self.view_sniffer.update_metrics(0, 0, 0, "IDLE", "#7f8c8d")
        self.view_settings.log("Session memory cleared.", "INFO")

    def _on_closing(self):
        self.pipeline.shutdown()
        self.destroy()


def run():
    app = NifrapApp()
    app.mainloop()


if __name__ == "__main__":
    run()

