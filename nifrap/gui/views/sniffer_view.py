import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Optional, Callable
from nifrap.core.packet_parser import PacketInfo


class SnifferView(ctk.CTkFrame):
    """Live Packet Sniffing and Web Packet Detection Dashboard View."""

    def __init__(self, master, on_scrape_request: Optional[Callable[[str], None]] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_scrape_request = on_scrape_request

        self.packet_records = []
        self._max_display_rows = 1500

        self._build_metrics_row()
        self._build_toolbar()
        self._build_packet_table()
        self._build_detail_inspector()

    def _build_metrics_row(self):
        metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=15, pady=(15, 10))

        # Card 1: Total Packets
        self.card_total = self._create_metric_card(metrics_frame, "Total Packets", "0", "#3a7ebf")
        self.card_total.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Card 2: Web Packets
        self.card_web = self._create_metric_card(metrics_frame, "Web Packets (HTTP/HTTPS)", "0", "#2fa572")
        self.card_web.pack(side="left", fill="both", expand=True, padx=8)

        # Card 3: Targets Scraped
        self.card_scraped = self._create_metric_card(metrics_frame, "Scraped Targets", "0", "#9b59b6")
        self.card_scraped.pack(side="left", fill="both", expand=True, padx=8)

        # Card 4: Capture Status
        self.card_status = self._create_metric_card(metrics_frame, "Capture Engine", "IDLE", "#7f8c8d")
        self.card_status.pack(side="left", fill="both", expand=True, padx=(8, 0))

    def _create_metric_card(self, parent, label_text: str, default_val: str, accent_color: str):
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color=("#2b2b2b", "#1e1e1e"), border_width=1, border_color="#333333")
        label = ctk.CTkLabel(card, text=label_text, font=ctk.CTkFont(size=12, weight="bold"), text_color="#a0a0a0")
        label.pack(anchor="w", padx=12, pady=(8, 2))
        val_label = ctk.CTkLabel(card, text=default_val, font=ctk.CTkFont(size=22, weight="bold"), text_color=accent_color)
        val_label.pack(anchor="w", padx=12, pady=(0, 8))
        card.value_label = val_label
        return card

    def _build_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=15, pady=(0, 8))

        # Search box
        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Search packets by IP, Host, or Protocol...",
            width=320,
            height=32,
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_table())

        # Web Only toggle
        self.web_only_var = tk.BooleanVar(value=False)
        self.web_only_check = ctk.CTkCheckBox(
            toolbar,
            text="Show Web Packets Only",
            variable=self.web_only_var,
            command=self._filter_table,
            font=ctk.CTkFont(size=12),
        )
        self.web_only_check.pack(side="left", padx=10)

        # Clear button
        self.clear_btn = ctk.CTkButton(
            toolbar,
            text="Clear Log",
            width=90,
            height=32,
            fg_color="#3a3a3a",
            hover_color="#505050",
            command=self.clear_table,
        )
        self.clear_btn.pack(side="right")

    def _build_packet_table(self):
        table_container = ctk.CTkFrame(self, corner_radius=8, fg_color=("#1e1e1e", "#181818"))
        table_container.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Setup ttk style for dark Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Sniffer.Treeview",
            background="#1e1e1e",
            foreground="#dcdcdc",
            fieldbackground="#1e1e1e",
            rowheight=24,
            font=("Segoe UI", 9),
            borderwidth=0,
        )
        style.configure(
            "Sniffer.Treeview.Heading",
            background="#282828",
            foreground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Sniffer.Treeview",
            background=[("selected", "#1f538d")],
            foreground=[("selected", "#ffffff")],
        )

        columns = ("id", "time", "proto", "src", "dst", "web_type", "summary")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            style="Sniffer.Treeview",
            selectmode="browse",
        )

        self.tree.heading("id", text="#", anchor="center")
        self.tree.heading("time", text="Time", anchor="w")
        self.tree.heading("proto", text="Proto", anchor="center")
        self.tree.heading("src", text="Source", anchor="w")
        self.tree.heading("dst", text="Destination", anchor="w")
        self.tree.heading("web_type", text="Web Type", anchor="center")
        self.tree.heading("summary", text="Summary / URL", anchor="w")

        self.tree.column("id", width=50, stretch=False, anchor="center")
        self.tree.column("time", width=90, stretch=False, anchor="w")
        self.tree.column("proto", width=65, stretch=False, anchor="center")
        self.tree.column("src", width=140, stretch=False, anchor="w")
        self.tree.column("dst", width=140, stretch=False, anchor="w")
        self.tree.column("web_type", width=80, stretch=False, anchor="center")
        self.tree.column("summary", width=400, stretch=True, anchor="w")

        # Color Tags
        self.tree.tag_configure("http", foreground="#2ecc71")
        self.tree.tag_configure("https", foreground="#00d2d3")
        self.tree.tag_configure("dns", foreground="#f39c12")
        self.tree.tag_configure("other", foreground="#95a5a6")

        scrollbar = ctk.CTkScrollbar(table_container, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_packet_selected)

    def _build_detail_inspector(self):
        inspector = ctk.CTkFrame(self, height=80, corner_radius=8, fg_color=("#252525", "#1c1c1c"))
        inspector.pack(fill="x", padx=15, pady=(0, 15))

        self.detail_label = ctk.CTkLabel(
            inspector,
            text="Select any packet above to inspect details and initiate targeted scraping.",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa",
            anchor="w",
            justify="left",
        )
        self.detail_label.pack(side="left", padx=15, pady=12, fill="x", expand=True)

        self.action_scrape_btn = ctk.CTkButton(
            inspector,
            text="⚡ Scrape Target",
            width=140,
            height=34,
            fg_color="#1f538d",
            hover_color="#163f6b",
            state="disabled",
            command=self._on_scrape_clicked,
        )
        self.action_scrape_btn.pack(side="right", padx=15, pady=12)

        self.selected_target_url = None

    def add_packet(self, packet: PacketInfo):
        """Append new packet to records and table."""
        self.packet_records.append(packet)
        if len(self.packet_records) > self._max_display_rows:
            self.packet_records.pop(0)

        # Check if visible under current filter
        query = self.search_entry.get().strip().lower()
        if self.web_only_var.get() and not packet.is_web:
            return
        if query and not (query in packet.summary.lower() or query in packet.src_ip or query in packet.dst_ip or query in packet.protocol.lower()):
            return

        tag = "other"
        if packet.web_type == "HTTP":
            tag = "http"
        elif packet.web_type == "HTTPS":
            tag = "https"
        elif packet.web_type == "DNS":
            tag = "dns"

        src_str = f"{packet.src_ip}:{packet.src_port}" if packet.src_port else packet.src_ip
        dst_str = f"{packet.dst_ip}:{packet.dst_port}" if packet.dst_port else packet.dst_ip

        self.tree.insert(
            "",
            "end",
            iid=str(packet.id),
            values=(packet.id, packet.timestamp, packet.protocol, src_str, dst_str, packet.web_type or "-", packet.summary),
            tags=(tag,),
        )

        # Auto-scroll to latest packet
        children = self.tree.get_children()
        if children:
            self.tree.see(children[-1])

    def _filter_table(self):
        """Re-render visible table rows based on search and web-only filter."""
        query = self.search_entry.get().strip().lower()
        web_only = self.web_only_var.get()

        self.tree.delete(*self.tree.get_children())
        for packet in self.packet_records:
            if web_only and not packet.is_web:
                continue
            if query and not (query in packet.summary.lower() or query in packet.src_ip or query in packet.dst_ip or query in packet.protocol.lower()):
                continue

            tag = "other"
            if packet.web_type == "HTTP":
                tag = "http"
            elif packet.web_type == "HTTPS":
                tag = "https"
            elif packet.web_type == "DNS":
                tag = "dns"

            src_str = f"{packet.src_ip}:{packet.src_port}" if packet.src_port else packet.src_ip
            dst_str = f"{packet.dst_ip}:{packet.dst_port}" if packet.dst_port else packet.dst_ip

            self.tree.insert(
                "",
                "end",
                iid=str(packet.id),
                values=(packet.id, packet.timestamp, packet.protocol, src_str, dst_str, packet.web_type or "-", packet.summary),
                tags=(tag,),
            )

    def _on_packet_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        pkt_id = int(selected[0])
        pkt = next((p for p in self.packet_records if p.id == pkt_id), None)
        if not pkt:
            return

        if pkt.is_web and pkt.target_url:
            self.selected_target_url = pkt.target_url
            self.detail_label.configure(
                text=f"🌐 Detected Web Target: {pkt.target_url} [{pkt.web_type}] | Method: {pkt.method or 'GET'} | Host: {pkt.host}",
                text_color="#2ecc71",
            )
            self.action_scrape_btn.configure(state="normal", text=f"⚡ Scrape {pkt.host[:20]}")
        else:
            self.selected_target_url = None
            self.detail_label.configure(
                text=f"Packet #{pkt.id} | {pkt.protocol} | {pkt.src_ip}:{pkt.src_port} -> {pkt.dst_ip}:{pkt.dst_port} | Size: {pkt.length} B",
                text_color="#aaaaaa",
            )
            self.action_scrape_btn.configure(state="disabled", text="⚡ Scrape Target")

    def _on_scrape_clicked(self):
        if self.selected_target_url and self.on_scrape_request:
            self.on_scrape_request(self.selected_target_url)

    def update_metrics(self, total: int, web: int, scraped: int, status: str, status_color: str = "#7f8c8d"):
        self.card_total.value_label.configure(text=str(total))
        self.card_web.value_label.configure(text=str(web))
        self.card_scraped.value_label.configure(text=str(scraped))
        self.card_status.value_label.configure(text=status, text_color=status_color)

    def clear_table(self):
        self.packet_records.clear()
        self.tree.delete(*self.tree.get_children())
        self.detail_label.configure(text="Packet table cleared.", text_color="#aaaaaa")
        self.action_scrape_btn.configure(state="disabled")

