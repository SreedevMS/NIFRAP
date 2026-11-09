import os
import datetime
from tkinter import messagebox, filedialog
import customtkinter as ctk
from typing import Optional, List, Dict

from nifrap.config import EXPORTS_DIR, DOWNLOADS_DIR
from nifrap.core.packet_parser import PacketInfo
from nifrap.core.scraper import ScrapedData
from nifrap.core.storage import (
    export_packets_to_csv,
    export_scraped_to_json,
    export_scraped_to_excel,
    export_scraped_to_word,
)


class ExportView(ctk.CTkFrame):
    """Centralized Storage and Export Management View."""

    def __init__(self, master, get_session_data_cb, on_clear_session_cb=None, **kwargs):
        super().__init__(master, **kwargs)
        self.get_session_data = get_session_data_cb
        self.on_clear_session = on_clear_session_cb

        self._build_header()
        self._build_action_grid()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 15))

        title = ctk.CTkLabel(
            header_frame,
            text="Session Storage & Intelligence Export",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff",
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text=f"Default Storage Location: {EXPORTS_DIR}",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        )
        subtitle.pack(anchor="w", pady=(2, 0))

    def _build_action_grid(self):
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Grid of cards
        cards_data = [
            (
                "📊 Export Packets to CSV",
                "Export all captured network packets with IP addresses, ports, protocols, and payload summaries.",
                "Export CSV",
                "#3a7ebf",
                self._export_csv,
            ),
            (
                "📁 Export Intelligence to JSON",
                "Complete structured session dump containing all sniffed packets and parsed web target data.",
                "Export JSON",
                "#2fa572",
                self._export_json,
            ),
            (
                "📑 Export Scraped Targets to Excel (.xlsx)",
                "Creates multi-sheet Excel workbooks containing overview data, tables, links, and discovered images.",
                "Export Excel",
                "#16a085",
                self._export_excel,
            ),
            (
                "📝 Export Scraped Reports to Word (.docx)",
                "Generates executive-ready Microsoft Word intelligence reports with tables, outlines, and text.",
                "Export Word",
                "#2980b9",
                self._export_word,
            ),
            (
                "📂 Open Exports Directory",
                "Open the local storage folder where all exports, downloads, and sessions are automatically saved.",
                "Open Folder",
                "#505050",
                self._open_folder,
            ),
            (
                "🗑️ Reset Session Data",
                "Clear current in-memory packet logs and scraped targets to start a completely fresh session.",
                "Reset Session",
                "#c0392b",
                self._clear_session,
            ),
        ]

        for title, desc, btn_text, color, command in cards_data:
            self._create_card(container, title, desc, btn_text, color, command)

    def _create_card(self, parent, title, desc, btn_text, color, command):
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color=("#222222", "#1a1a1a"), border_width=1, border_color="#333333")
        card.pack(fill="x", pady=8)

        text_frame = ctk.CTkFrame(card, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, padx=15, pady=12)

        lbl_title = ctk.CTkLabel(text_frame, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff")
        lbl_title.pack(anchor="w")

        lbl_desc = ctk.CTkLabel(text_frame, text=desc, font=ctk.CTkFont(size=11), text_color="#aaaaaa", wraplength=520, justify="left")
        lbl_desc.pack(anchor="w", pady=(4, 0))

        btn = ctk.CTkButton(
            card,
            text=btn_text,
            width=130,
            height=34,
            fg_color=color,
            hover_color="#333333",
            font=ctk.CTkFont(weight="bold"),
            command=command,
        )
        btn.pack(side="right", padx=15, pady=12)

    def _export_csv(self):
        packets, _ = self.get_session_data()
        if not packets:
            messagebox.showinfo("Info", "No packet capture data available to export.")
            return

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_file = EXPORTS_DIR / f"nifrap_packets_{ts}.csv"
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialdir=str(EXPORTS_DIR),
            initialfile=default_file.name,
            title="Save Packets as CSV",
        )
        if path:
            export_packets_to_csv(packets, path)
            messagebox.showinfo("Export Complete", f"Exported {len(packets)} packets to:\n{path}")

    def _export_json(self):
        _, scraped_dict = self.get_session_data()
        if not scraped_dict:
            messagebox.showinfo("Info", "No scraped web target data available to export.")
            return

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_file = EXPORTS_DIR / f"nifrap_intelligence_{ts}.json"
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialdir=str(EXPORTS_DIR),
            initialfile=default_file.name,
            title="Save Intelligence as JSON",
        )
        if path:
            export_scraped_to_json(list(scraped_dict.values()), path)
            messagebox.showinfo("Export Complete", f"Exported {len(scraped_dict)} targets to:\n{path}")

    def _export_excel(self):
        _, scraped_dict = self.get_session_data()
        if not scraped_dict:
            messagebox.showinfo("Info", "No scraped web target data available to export.")
            return

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        count = 0
        for item in scraped_dict.values():
            safe_host = "".join([c if c.isalnum() else "_" for c in item.host]) or "target"
            filename = EXPORTS_DIR / f"{safe_host}_{ts}.xlsx"
            export_scraped_to_excel(item, str(filename))
            count += 1

        messagebox.showinfo("Export Complete", f"Exported {count} Excel workbook(s) into:\n{EXPORTS_DIR}")

    def _export_word(self):
        _, scraped_dict = self.get_session_data()
        if not scraped_dict:
            messagebox.showinfo("Info", "No scraped web target data available to export.")
            return

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        count = 0
        for item in scraped_dict.values():
            safe_host = "".join([c if c.isalnum() else "_" for c in item.host]) or "target"
            filename = EXPORTS_DIR / f"{safe_host}_report_{ts}.docx"
            export_scraped_to_word(item, str(filename))
            count += 1

        messagebox.showinfo("Export Complete", f"Exported {count} Word report(s) into:\n{EXPORTS_DIR}")

    def _open_folder(self):
        try:
            os.startfile(str(EXPORTS_DIR))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open directory:\n{e}")

    def _clear_session(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to clear all current session data?"):
            if self.on_clear_session:
                self.on_clear_session()
            messagebox.showinfo("Reset", "Session data cleared.")

