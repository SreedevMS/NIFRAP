import os
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import requests
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from nifrap.core.packet_parser import PacketInfo
from nifrap.core.scraper import ScrapedData


def export_packets_to_pcap(scapy_packets: List[Any], filepath: str) -> str:
    """Export raw captured packets to standard Wireshark PCAP format."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    import scapy.all as scapy
    scapy.wrpcap(filepath, scapy_packets)
    return filepath


def export_packets_to_csv(packets: List[PacketInfo], filepath: str) -> str:
    """Export list of PacketInfo objects to a CSV file."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ID", "Timestamp", "Source IP", "Source Port",
            "Destination IP", "Destination Port", "Protocol",
            "Length (Bytes)", "Is Web", "Web Type", "Host",
            "Method", "Target URL", "Summary"
        ])
        for p in packets:
            writer.writerow([
                p.id, p.timestamp, p.src_ip, p.src_port,
                p.dst_ip, p.dst_port, p.protocol,
                p.length, p.is_web, p.web_type, p.host,
                p.method, p.target_url, p.summary
            ])
    return filepath


def export_scraped_to_json(scraped_items: List[ScrapedData], filepath: str) -> str:
    """Export all scraped target data to structured JSON."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    data = []
    for item in scraped_items:
        data.append({
            "url": item.url,
            "host": item.host,
            "status_code": item.status_code,
            "content_type": item.content_type,
            "title": item.title,
            "description": item.description,
            "server": item.server,
            "response_time_ms": item.response_time_ms,
            "scraped_at": item.scraped_at,
            "error": item.error,
            "headings": item.headings,
            "paragraphs_count": len(item.paragraphs),
            "paragraphs": item.paragraphs[:20],  # preview top paragraphs
            "links_count": len(item.links),
            "links": item.links,
            "images_count": len(item.images),
            "images": item.images,
            "tables_count": len(item.tables),
            "tables": item.tables,
        })
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def export_scraped_to_excel(scraped: ScrapedData, filepath: str) -> str:
    """Export single or multi-target scraped data into a formatted multi-sheet Excel file."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()

    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    regular_font = Font(name="Segoe UI", size=10)

    # 1. Sheet: Overview
    ws_over = wb.active
    ws_over.title = "Overview"
    ws_over.append(["Field", "Value"])
    overview_fields = [
        ("Target URL", scraped.url),
        ("Host", scraped.host),
        ("Title", scraped.title),
        ("Description", scraped.description),
        ("HTTP Status", str(scraped.status_code)),
        ("Server", scraped.server),
        ("Content Type", scraped.content_type),
        ("Response Time", f"{scraped.response_time_ms} ms"),
        ("Scraped At", scraped.scraped_at),
        ("Total Links Found", str(len(scraped.links))),
        ("Total Images Found", str(len(scraped.images))),
        ("Total Tables Found", str(len(scraped.tables))),
    ]
    for k, v in overview_fields:
        ws_over.append([k, v])

    # 2. Sheet: Links
    ws_links = wb.create_sheet("Links")
    ws_links.append(["#", "URL"])
    for idx, link in enumerate(scraped.links, 1):
        ws_links.append([idx, link])

    # 3. Sheet: Images
    ws_imgs = wb.create_sheet("Images")
    ws_imgs.append(["#", "Filename", "Alt Text", "Direct URL"])
    for idx, img in enumerate(scraped.images, 1):
        ws_imgs.append([idx, img.get("filename", ""), img.get("alt", ""), img.get("url", "")])

    # 4. Sheet: Tables
    if scraped.tables:
        ws_tabs = wb.create_sheet("Tables")
        row_counter = 1
        for t_idx, table in enumerate(scraped.tables, 1):
            ws_tabs.cell(row=row_counter, column=1, value=f"Table #{t_idx}").font = Font(bold=True, size=12)
            row_counter += 1
            for row in table:
                ws_tabs.append(row)
                row_counter += 1
            row_counter += 1

    # Style header rows across all sheets
    for ws in wb.worksheets:
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="left", vertical="center")
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = min(max_len + 4, 80)

    wb.save(filepath)
    return filepath


def export_scraped_to_word(scraped: ScrapedData, filepath: str) -> str:
    """Generate a clean Microsoft Word (.docx) report for scraped intelligence."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    doc = Document()

    # Document Title
    title = doc.add_heading("NIFRAP Intelligence Report", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(f"Generated at: {scraped.scraped_at} | Target: {scraped.host}")

    # Section 1: Overview
    doc.add_heading("Target Overview", level=1)
    overview_table = doc.add_table(rows=1, cols=2)
    overview_table.style = "Table Grid"
    hdr_cells = overview_table.rows[0].cells
    hdr_cells[0].text = "Parameter"
    hdr_cells[1].text = "Details"

    params = [
        ("URL", scraped.url),
        ("Title", scraped.title),
        ("Status Code", str(scraped.status_code)),
        ("Server", scraped.server),
        ("Response Time", f"{scraped.response_time_ms} ms"),
        ("Description", scraped.description or "N/A"),
    ]
    for param, val in params:
        row = overview_table.add_row().cells
        row[0].text = param
        row[1].text = val

    # Section 2: Headings & Key Content
    if scraped.headings:
        doc.add_heading("Headings & Outline", level=1)
        for h in scraped.headings[:20]:
            doc.add_paragraph(f"[{h['tag']}] {h['text']}", style="List Bullet")

    if scraped.paragraphs:
        doc.add_heading("Key Text Excerpts", level=1)
        for p in scraped.paragraphs[:10]:
            doc.add_paragraph(p)

    # Section 3: Extracted Tables
    if scraped.tables:
        doc.add_heading("Extracted Tables", level=1)
        for t_idx, tbl_data in enumerate(scraped.tables[:5], 1):
            doc.add_heading(f"Table {t_idx}", level=2)
            if tbl_data:
                cols = len(tbl_data[0])
                table = doc.add_table(rows=len(tbl_data), cols=cols)
                table.style = "Table Grid"
                for r_idx, row in enumerate(tbl_data):
                    for c_idx, val in enumerate(row):
                        if c_idx < cols:
                            table.cell(r_idx, c_idx).text = str(val)

    # Section 4: Extracted Links
    if scraped.links:
        doc.add_heading(f"Discovered Links ({len(scraped.links)})", level=1)
        for link in scraped.links[:50]:
            doc.add_paragraph(link, style="List Bullet")

    doc.save(filepath)
    return filepath


def download_images_batch(
    images: List[Dict[str, str]],
    destination_folder: str,
    on_progress: Optional[Callable[[int, int, str], None]] = None,
) -> int:
    """Download images into destination directory."""
    dest = Path(destination_folder)
    dest.mkdir(parents=True, exist_ok=True)
    count = 0
    total = len(images)

    for idx, img in enumerate(images, 1):
        url = img.get("url", "")
        filename = img.get("filename") or f"image_{idx}.png"
        save_path = dest / filename

        # Ensure unique filename if collision occurs
        if save_path.exists():
            save_path = dest / f"{idx}_{filename}"

        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(resp.content)
                count += 1
                if on_progress:
                    on_progress(idx, total, f"Saved {filename}")
        except Exception:
            pass

    return count

