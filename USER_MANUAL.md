# NIFRAP 2.0 — Complete User Manual & Operation Guide

Welcome to **NIFRAP 2.0** (*Network Intelligence Framework & Reconnaissance Automation Platform*). This manual provides step-by-step instructions on setting up, running, and utilizing NIFRAP to capture live network traffic, detect web activity, scrape website content automatically, and export intelligence reports.

---

## 📑 Table of Contents

1. [System Requirements & Prerequisites](#1-system-requirements--prerequisites)
2. [Getting Started & Installation](#2-getting-started--installation)
   - [Option A: Running the Standalone Executable (No Python Required)](#option-a-running-the-standalone-executable-no-python-required)
   - [Option B: Running from Python Source Code](#option-b-running-from-python-source-code)
3. [Understanding the Core Workflow](#3-understanding-the-core-workflow)
4. [Dashboard Walkthrough & Features](#4-dashboard-walkthrough--features)
   - [Left Sidebar (Global Controls)](#left-sidebar-global-controls)
   - [Tab 1: Live Sniffer Dashboard](#tab-1-live-sniffer-dashboard)
   - [Tab 2: Web Intelligence & Scraper](#tab-2-web-intelligence--scraper)
   - [Tab 3: Storage & Export Center](#tab-3-storage--export-center)
   - [Tab 4: Activity Log & Diagnostics](#tab-4-activity-log--diagnostics)
5. [Demo Simulation Mode (Testing Without Admin Rights)](#5-demo-simulation-mode-testing-without-admin-rights)
6. [Export Formats & Where Data is Stored](#6-export-formats--where-data-is-stored)
7. [Troubleshooting & FAQs](#7-troubleshooting--faqs)

---

## 1. System Requirements & Prerequisites

- **Operating System:** Windows 10 or Windows 11 (64-bit).
- **For Live Packet Sniffing on Windows:**
  - Install the free [Npcap Driver](https://npcap.com/#download).
  - **Important:** During Npcap setup, check the box: **"Install Npcap in WinPcap API-compatible Mode"**.
  - Run the application or terminal **as Administrator** to permit raw socket / promiscuous packet capture.
- **For Testing / Simulation:**
  - **Zero setup required.** NIFRAP includes an automated **Demo Simulation** engine that generates realistic web traffic events without needing Npcap or administrator privileges.

---

## 2. Getting Started & Installation

### Option A: Running the Standalone Executable (No Python Required)

1. Download `NIFRAP-2.0-Windows-Portable.zip` from the [GitHub Releases](https://github.com/SreedevMS/NIFRAP/releases) page or from `dist/`.
2. Extract the ZIP archive to any folder on your computer.
3. Right-click `NIFRAP_2.0.exe` and select **"Run as Administrator"** (recommended for live packet sniffing).
4. The modern dark-themed dashboard will open immediately.

### Option B: Running from Python Source Code

1. Clone the repository:
   ```powershell
   git clone https://github.com/SreedevMS/NIFRAP.git
   cd NIFRAP
   ```
2. Install the required Python libraries:
   ```powershell
   pip install -r requirements.txt
   ```
3. Launch the application:
   ```powershell
   python run.py
   ```
   *(Or open `GUI NEW.sln` in Visual Studio and press **F5 / Start**).*

---

## 3. Understanding the Core Workflow

NIFRAP integrates a continuous four-stage automated pipeline:

```
[ 1. Sniff Traffic ]  ──►  [ 2. Detect Web Packets ]  ──►  [ 3. Auto-Scrape Site ]  ──►  [ 4. Store Intelligence ]
  Wi-Fi / Ethernet           HTTP Requests & TLS SNI         Tables, Links, Images        Excel, Word, JSON, CSV
```

1. **Sniff:** Monitors incoming and outgoing IP packets across your chosen network adapter.
2. **Detect:** Deep-inspects packet headers:
   - Plain **HTTP** requests (`GET`/`POST`, Host headers, and requested paths).
   - Encrypted **HTTPS** traffic by extracting the domain from the **TLS Client Hello SNI** (*Server Name Indication*).
   - **DNS** queries resolving website domains.
3. **Scrape:** When a new web target is discovered, a background worker automatically scrapes the page (page title, description, tables, links, images, headings, and paragraphs) without freezing the user interface.
4. **Store:** Automatically organizes the collected intelligence into formatted reports and files in `data/exports/`.

---

## 4. Dashboard Walkthrough & Features

### Left Sidebar (Global Controls)

- **Network Adapter Dropdown:** Lists all active network cards (e.g. Wi-Fi, Ethernet, Loopback) along with their IP addresses and up/down status.
- **Auto-Scrape Web Packets Toggle:**
  - **Enabled (Default):** Any discovered web host is automatically queued and scraped in the background.
  - **Disabled:** Packets are logged, but scraping only happens when you explicitly click **"Scrape Target"**.
- **▶ Start Sniffing / ⏹ Stop Sniffing Button:** Starts or stops live packet capture.
- **⚡ Demo Simulation Button:** Generates test network packets to demonstrate the full capture ➔ scrape ➔ export pipeline safely.
- **Navigation Menu:** Switch between the four main views:
  - 📡 Live Sniffer
  - 🌐 Web Scraper
  - 💾 Storage & Export
  - ⚙️ Activity Log

---

### Tab 1: Live Sniffer Dashboard

The **Live Sniffer** view is your real-time packet monitoring station:

1. **Top Metric Cards:**
   - **Total Packets:** Total raw network packets captured in the current session.
   - **Web Packets:** Count of HTTP, HTTPS, or DNS packets identified.
   - **Scraped Targets:** Number of websites successfully crawled and parsed.
   - **Capture Engine:** Current operational status (`IDLE`, `SNIFFING`, or `SIMULATION`).
2. **Real-time Filter & Search Bar:**
   - Type in the search box to filter live packets instantly by IP address, host name, or protocol.
   - Check **"Show Web Packets Only"** to hide background non-web traffic.
   - Click **"Clear Log"** to reset the live table display.
3. **Packet Stream Table:**
   - Displays packets with color-coded tags:
     - 🟩 **Green (`HTTP`):** Plaintext web requests.
     - 🟦 **Cyan (`HTTPS`):** TLS handshakes with extracted SNI hostnames.
     - 🟧 **Orange (`DNS`):** Domain resolution queries.
     - ⬜ **Gray (`Other`):** Background TCP, UDP, or ICMP traffic.
4. **Detail Inspector & Manual Action:**
   - Click any packet in the table to view its full details in the bottom bar.
   - If the packet contains a web target, click the **"⚡ Scrape Target"** button to jump straight into scraping that site.

---

### Tab 2: Web Intelligence & Scraper

The **Web Scraper** view allows deep inspection of all intelligence gathered from sniffed or manually entered websites:

1. **Top URL Bar:**
   - Enter any URL manually (e.g., `https://example.com`) and click **"⚡ Scrape Now"** to scrape on demand.
2. **Left Panel (Sniffed Web Targets):**
   - Shows all unique websites caught by the sniffer.
   - Status indicators:
     - 🟧 `Pending`: In queue for scraping.
     - 🟦 `Scraping`: Actively being fetched by background workers.
     - 🟩 `Scraped`: Successfully scraped and ready to view.
     - 🟥 `Error`: Request timed out or site blocked connection.
3. **Right Panel (6-Tab Intelligence Inspector):**
   - **📊 Overview:** Shows Page Title, Meta Description, HTTP Status Code, Server Header, Response Time (ms), and quick export buttons.
   - **📑 Tables:** Lists all HTML tables found on the page, displaying their rows and columns.
   - **🔗 Links:** Lists all internal and external hyperlinks (`<a href>`) extracted from the page.
   - **🖼️ Images:** Lists all image assets (`<img src>`) with filename, alt text, and direct URLs. Click **"Download All Images"** to batch-save them locally.
   - **📝 Headings & Text:** Structured text outline including `<h1>`–`<h6>` headings and paragraph content.
   - **💻 Raw HTML:** Prettified HTML source code of the page.

---

### Tab 3: Storage & Export Center

The **Storage & Export** view gives you one-click export actions for your session:

| Action Card | Output Format | Description |
| :--- | :--- | :--- |
| **📊 Export Packets to CSV** | `.csv` | Exports all captured packets with timestamps, IPs, ports, protocols, and URLs into a spreadsheet. |
| **📁 Export Intelligence to JSON** | `.json` | Full structured JSON database of all captured targets, metadata, tables, links, and paragraphs. |
| **📑 Export Targets to Excel** | `.xlsx` | Formatted multi-sheet Excel file with dedicated sheets for **Overview**, **Tables**, **Links**, and **Images**. |
| **📝 Export Reports to Word** | `.docx` | Executive-ready Microsoft Word intelligence briefing with styled tables, outlines, and summaries. |
| **📂 Open Exports Directory** | Local Folder | Opens `data/exports/` in Windows File Explorer. |
| **🗑️ Reset Session Data** | Memory | Clears current in-memory packet logs and scraped targets to start fresh. |

---

### Tab 4: Activity Log & Diagnostics

- **Environment Diagnostics:** Displays active Python version, Scapy engine status, Npcap integration, request timeout settings, and User-Agent headers.
- **Pipeline Console:** Real-time stream of all internal application events:
  - `[DISCOVERY]` events when a web target is intercepted.
  - `[SCRAPE]` events when worker threads initiate HTTP requests.
  - `[SUCCESS]` events when tables, links, and text are harvested.
  - `[ERROR]` notifications with troubleshooting details if a target fails.

---

## 5. Demo Simulation Mode (Testing Without Admin Rights)

To see NIFRAP in action immediately without configuring physical network adapters or needing administrative rights:

1. Launch NIFRAP 2.0.
2. Click the purple **"⚡ Demo Simulation"** button in the left sidebar.
3. Watch the dashboard:
   - Synthetic background network traffic and web packets (HTTP requests, TLS handshakes) appear in the table.
   - Web targets (such as `quotes.toscrape.com`, `httpbin.org`, `example.com`, `wikipedia.org`) are detected.
   - The auto-scraper automatically crawls the targets in real time.
   - Click over to the **Web Scraper** tab to browse the extracted tables, quotes, links, and page structures.
4. Click **"⏹ Stop Demo"** when done, then head to **Storage & Export** to generate your reports.

---

## 6. Export Formats & Where Data is Stored

All data exported through NIFRAP is saved locally on your computer:

```
F:\GUI NEW\
├── data/
│   ├── exports/      <── Excel (.xlsx), Word (.docx), JSON (.json), CSV (.csv) reports
│   └── downloads/    <── Batch downloaded images from scraped websites
```

---

## 7. Troubleshooting & FAQs

### Q1: The sniffer shows an error: *"Npcap/WinPcap driver required"*
- **Fix:** Windows requires the Npcap packet capture driver for raw packet inspection. Download and install [Npcap](https://npcap.com/#download). Make sure to check **"Install Npcap in WinPcap API-compatible Mode"** during setup.

### Q2: I don't have Administrator rights on my PC. Can I still use NIFRAP?
- **Yes!** Click **"⚡ Demo Simulation"** in the sidebar. The entire web detection, multi-threaded scraper, and export engine function without administrator privileges. You can also manually type any URL into the **Web Scraper** tab to scrape any live website.

### Q3: Some background Windows traffic is flooding the packet log.
- **Fix:** In the **Live Sniffer** view, check **"Show Web Packets Only"**. NIFRAP also includes an integrated telemetry filter in `nifrap/config.py` that prevents background OS noise (like `windowsupdate.com` or `telemetry.microsoft.com`) from triggering unnecessary scraping.

### Q4: How do I open the generated reports?
- In the **Storage & Export** view, click **"Open Folder"** to directly open the `data/exports/` directory in Windows Explorer. Excel files can be opened in Microsoft Excel or Google Sheets; Word reports can be opened in Microsoft Word or LibreOffice.

---

*Developed for the NIFRAP Project.*
