import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from typing import Optional, Callable, Dict, List

from nifrap.core.scraper import ScrapedData, normalize_url
from nifrap.core.storage import export_scraped_to_excel, export_scraped_to_word, download_images_batch


class ScraperView(ctk.CTkFrame):
    """Web Intelligence & Scraping Inspector View."""

    def __init__(self, master, on_scrape_request: Optional[Callable[[str], None]] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_scrape_request = on_scrape_request

        self.scraped_data_map: Dict[str, ScrapedData] = {}
        self.targets_list: Dict[str, Dict] = {}
        self.current_selected_data: Optional[ScrapedData] = None

        self._build_header_input()
        self._build_main_split()

    def _build_header_input(self):
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(15, 10))

        label = ctk.CTkLabel(input_frame, text="Target URL:", font=ctk.CTkFont(size=13, weight="bold"))
        label.pack(side="left", padx=(0, 10))

        self.url_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter website URL (e.g., https://example.com or captured host)...",
            height=36,
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.url_entry.bind("<Return>", lambda e: self._on_manual_scrape())

        self.manual_scrape_btn = ctk.CTkButton(
            input_frame,
            text="⚡ Scrape Now",
            width=130,
            height=36,
            fg_color="#1f538d",
            hover_color="#163f6b",
            font=ctk.CTkFont(weight="bold"),
            command=self._on_manual_scrape,
        )
        self.manual_scrape_btn.pack(side="right")

    def _build_main_split(self):
        split_container = ctk.CTkFrame(self, fg_color="transparent")
        split_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Left Panel: Targets List
        left_panel = ctk.CTkFrame(split_container, width=320, corner_radius=8, fg_color=("#222222", "#191919"))
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)

        left_header = ctk.CTkLabel(
            left_panel,
            text="Sniffed Web Targets",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#ffffff",
        )
        left_header.pack(anchor="w", padx=12, pady=10)

        # Targets Treeview
        tree_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        columns = ("host", "status")
        self.target_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Sniffer.Treeview",
            selectmode="browse",
        )
        self.target_tree.heading("host", text="Host / Target", anchor="w")
        self.target_tree.heading("status", text="Status", anchor="center")
        self.target_tree.column("host", width=200, anchor="w")
        self.target_tree.column("status", width=80, anchor="center")

        self.target_tree.tag_configure("Pending", foreground="#f39c12")
        self.target_tree.tag_configure("Scraping", foreground="#00d2d3")
        self.target_tree.tag_configure("Scraped", foreground="#2ecc71")
        self.target_tree.tag_configure("Error", foreground="#e74c3c")

        tree_scroll = ctk.CTkScrollbar(tree_frame, command=self.target_tree.yview)
        self.target_tree.configure(yscrollcommand=tree_scroll.set)

        self.target_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        self.target_tree.bind("<<TreeviewSelect>>", self._on_target_selected)

        # Right Panel: Intelligence Inspector
        self.right_panel = ctk.CTkFrame(split_container, corner_radius=8, fg_color=("#252525", "#1c1c1c"))
        self.right_panel.pack(side="right", fill="both", expand=True)

        self._build_inspector_tabs()

    def _build_inspector_tabs(self):
        self.tabview = ctk.CTkTabview(self.right_panel, corner_radius=8)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_overview = self.tabview.add("📊 Overview")
        self.tab_tables = self.tabview.add("📑 Tables")
        self.tab_links = self.tabview.add("🔗 Links")
        self.tab_images = self.tabview.add("🖼️ Images")
        self.tab_text = self.tabview.add("📝 Headings & Text")
        self.tab_html = self.tabview.add("💻 Raw HTML")

        self._init_overview_tab()
        self._init_tables_tab()
        self._init_links_tab()
        self._init_images_tab()
        self._init_text_tab()
        self._init_html_tab()

    def _init_overview_tab(self):
        self.overview_container = ctk.CTkScrollableFrame(self.tab_overview, fg_color="transparent")
        self.overview_container.pack(fill="both", expand=True, padx=5, pady=5)

        self.lbl_empty_state = ctk.CTkLabel(
            self.overview_container,
            text="No target selected or scraped yet.\nStart sniffing or enter a URL above to inspect extracted intelligence.",
            font=ctk.CTkFont(size=13),
            text_color="#888888",
            justify="center",
        )
        self.lbl_empty_state.pack(pady=60)

        # Info Card
        self.info_card = ctk.CTkFrame(self.overview_container, fg_color="#1e1e1e", corner_radius=8)
        self.title_val = ctk.CTkLabel(self.info_card, text="", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff", wraplength=550)
        self.url_val = ctk.CTkLabel(self.info_card, text="", font=ctk.CTkFont(size=12), text_color="#00d2d3", wraplength=550)
        self.status_val = ctk.CTkLabel(self.info_card, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="#2ecc71")
        self.desc_val = ctk.CTkLabel(self.info_card, text="", font=ctk.CTkFont(size=11), text_color="#bbbbbb", wraplength=550, justify="left")

        # Action Buttons Row
        self.action_bar = ctk.CTkFrame(self.overview_container, fg_color="transparent")
        self.btn_export_excel = ctk.CTkButton(self.action_bar, text="📊 Save Excel", width=120, command=self._export_excel_current)
        self.btn_export_word = ctk.CTkButton(self.action_bar, text="📝 Save Word", width=120, command=self._export_word_current)
        self.btn_download_imgs = ctk.CTkButton(self.action_bar, text="🖼️ Download Images", width=140, command=self._download_images_current)

    def _init_tables_tab(self):
        self.tables_container = ctk.CTkScrollableFrame(self.tab_tables, fg_color="transparent")
        self.tables_container.pack(fill="both", expand=True, padx=5, pady=5)
        self.lbl_tables_empty = ctk.CTkLabel(self.tables_container, text="No HTML tables found on this page.", text_color="#888888")
        self.lbl_tables_empty.pack(pady=40)

    def _init_links_tab(self):
        top_bar = ctk.CTkFrame(self.tab_links, fg_color="transparent")
        top_bar.pack(fill="x", padx=5, pady=(5, 8))

        self.lbl_links_count = ctk.CTkLabel(top_bar, text="Discovered Links: 0", font=ctk.CTkFont(weight="bold"))
        self.lbl_links_count.pack(side="left")

        self.links_textbox = ctk.CTkTextbox(self.tab_links, font=ctk.CTkFont(family="Consolas", size=11), wrap="none")
        self.links_textbox.pack(fill="both", expand=True, padx=5, pady=(0, 5))

    def _init_images_tab(self):
        top_bar = ctk.CTkFrame(self.tab_images, fg_color="transparent")
        top_bar.pack(fill="x", padx=5, pady=(5, 8))

        self.lbl_images_count = ctk.CTkLabel(top_bar, text="Discovered Images: 0", font=ctk.CTkFont(weight="bold"))
        self.lbl_images_count.pack(side="left")

        btn_dl = ctk.CTkButton(top_bar, text="Download All Images", width=140, height=28, command=self._download_images_current)
        btn_dl.pack(side="right")

        self.images_textbox = ctk.CTkTextbox(self.tab_images, font=ctk.CTkFont(family="Consolas", size=11), wrap="none")
        self.images_textbox.pack(fill="both", expand=True, padx=5, pady=(0, 5))

    def _init_text_tab(self):
        self.text_textbox = ctk.CTkTextbox(self.tab_text, font=ctk.CTkFont(size=12), wrap="word")
        self.text_textbox.pack(fill="both", expand=True, padx=5, pady=5)

    def _init_html_tab(self):
        self.html_textbox = ctk.CTkTextbox(self.tab_html, font=ctk.CTkFont(family="Consolas", size=11), wrap="none")
        self.html_textbox.pack(fill="both", expand=True, padx=5, pady=5)

    def _on_manual_scrape(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a valid URL.")
            return
        normalized = normalize_url(url)
        if self.on_scrape_request:
            self.on_scrape_request(normalized)

    def add_target(self, target_info: Dict):
        host = target_info.get("host") or target_info.get("url")
        status = target_info.get("status", "Pending")
        self.targets_list[host] = target_info

        # Insert or update in tree
        if self.target_tree.exists(host):
            self.target_tree.item(host, values=(host, status), tags=(status,))
        else:
            self.target_tree.insert("", "end", iid=host, values=(host, status), tags=(status,))

    def update_target_status(self, host: str, status: str):
        if host in self.targets_list:
            self.targets_list[host]["status"] = status
        if self.target_tree.exists(host):
            self.target_tree.item(host, values=(host, status), tags=(status,))

    def on_scrape_completed(self, data: ScrapedData):
        self.scraped_data_map[data.url] = data
        if data.host:
            self.scraped_data_map[data.host] = data
            self.update_target_status(data.host, "Scraped" if not data.error else "Error")

        # If this is the currently viewed target or first target, display it
        if not self.current_selected_data or self.current_selected_data.url == data.url:
            self.display_scraped_data(data)

    def _on_target_selected(self, event):
        selected = self.target_tree.selection()
        if not selected:
            return
        host = selected[0]
        data = self.scraped_data_map.get(host)
        if data:
            self.display_scraped_data(data)
        else:
            target_info = self.targets_list.get(host, {})
            url = target_info.get("url", f"https://{host}/")
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, url)

    def display_scraped_data(self, data: ScrapedData):
        self.current_selected_data = data
        self.lbl_empty_state.pack_forget()

        # Render Overview Card
        self.info_card.pack(fill="x", padx=10, pady=10)
        self.title_val.configure(text=data.title or "No Title Available")
        self.title_val.pack(anchor="w", padx=15, pady=(15, 4))

        self.url_val.configure(text=data.url)
        self.url_val.pack(anchor="w", padx=15, pady=(0, 6))

        status_text = f"HTTP {data.status_code} | Server: {data.server} | Response Time: {data.response_time_ms} ms"
        if data.error:
            status_text += f" | ERROR: {data.error}"
            self.status_val.configure(text=status_text, text_color="#e74c3c")
        else:
            self.status_val.configure(text=status_text, text_color="#2ecc71")
        self.status_val.pack(anchor="w", padx=15, pady=(0, 6))

        if data.description:
            self.desc_val.configure(text=f"Description: {data.description}")
            self.desc_val.pack(anchor="w", padx=15, pady=(0, 15))
        else:
            self.desc_val.pack_forget()

        # Render Action Bar
        self.action_bar.pack(fill="x", padx=10, pady=(5, 15))
        self.btn_export_excel.pack(side="left", padx=(0, 10))
        self.btn_export_word.pack(side="left", padx=10)
        self.btn_download_imgs.pack(side="left", padx=10)

        # Render Links
        self.lbl_links_count.configure(text=f"Discovered Links ({len(data.links)})")
        self.links_textbox.delete("1.0", "end")
        self.links_textbox.insert("1.0", "\n".join(data.links))

        # Render Images
        self.lbl_images_count.configure(text=f"Discovered Images ({len(data.images)})")
        self.images_textbox.delete("1.0", "end")
        img_lines = [f"[{img.get('filename')}] {img.get('url')} (Alt: '{img.get('alt')}')" for img in data.images]
        self.images_textbox.insert("1.0", "\n".join(img_lines))

        # Render Tables
        for widget in self.tables_container.winfo_children():
            widget.destroy()

        if data.tables:
            for idx, tbl in enumerate(data.tables, 1):
                lbl = ctk.CTkLabel(self.tables_container, text=f"Table #{idx} ({len(tbl)} rows)", font=ctk.CTkFont(weight="bold"))
                lbl.pack(anchor="w", padx=5, pady=(10, 4))

                table_str = "\n".join(["\t|\t".join(row) for row in tbl[:15]])
                txt = ctk.CTkTextbox(self.tables_container, height=120, font=ctk.CTkFont(family="Consolas", size=10))
                txt.insert("1.0", table_str)
                txt.pack(fill="x", padx=5, pady=(0, 10))
        else:
            lbl_none = ctk.CTkLabel(self.tables_container, text="No HTML tables found on this page.", text_color="#888888")
            lbl_none.pack(pady=40)

        # Render Text & Headings
        self.text_textbox.delete("1.0", "end")
        body = []
        if data.headings:
            body.append("=== HEADINGS & OUTLINE ===")
            for h in data.headings:
                body.append(f"[{h['tag']}] {h['text']}")
            body.append("\n=== PARAGRAPH TEXT ===")
        for p in data.paragraphs:
            body.append(p)
            body.append("")
        self.text_textbox.insert("1.0", "\n".join(body))

        # Render Raw HTML
        self.html_textbox.delete("1.0", "end")
        self.html_textbox.insert("1.0", data.raw_html[:100000])

    def _export_excel_current(self):
        if not self.current_selected_data:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
            initialfile=f"{self.current_selected_data.host or 'scrape'}_data.xlsx",
            title="Save Scraped Data as Excel",
        )
        if path:
            export_scraped_to_excel(self.current_selected_data, path)
            messagebox.showinfo("Success", f"Data exported successfully to:\n{path}")

    def _export_word_current(self):
        if not self.current_selected_data:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx")],
            initialfile=f"{self.current_selected_data.host or 'scrape'}_report.docx",
            title="Save Scraped Report as Word Document",
        )
        if path:
            export_scraped_to_word(self.current_selected_data, path)
            messagebox.showinfo("Success", f"Word report created successfully at:\n{path}")

    def _download_images_current(self):
        if not self.current_selected_data or not self.current_selected_data.images:
            messagebox.showinfo("Info", "No images available to download.")
            return
        folder = filedialog.askdirectory(title="Select Destination Folder for Images")
        if folder:
            count = download_images_batch(self.current_selected_data.images, folder)
            messagebox.showinfo("Success", f"Successfully downloaded {count} images to:\n{folder}")

