# NIFRAP 2.0 (Network Intelligence Framework & Reconnaissance Automation Platform)

**NIFRAP 2.0** is a modernized, dark-themed desktop reconnaissance platform that unifies **live network packet sniffing**, **automatic HTTP/HTTPS web target detection**, **targeted multi-threaded web scraping**, and **multi-format intelligence reporting**.

---

## 🌟 The Core Workflow: Sniff ➔ Detect ➔ Scrape ➔ Store

```
+-------------------------------------------------------------------------+
|                         1. LIVE NETWORK SNIFFER                         |
|  Captures raw IP packets across network interfaces (Wi-Fi, Ethernet...) |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                      2. WEB PACKET DETECTION ENGINE                     |
|  - HTTP: Extracts GET/POST, Host header, and requested paths            |
|  - HTTPS: Deep-inspects TLS Client Hello SNI (Server Name Indication)   |
|  - DNS: Intercepts web domain lookups (A/AAAA queries)                  |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                      3. AUTOMATED WEB SCRAPER (ASYNC)                   |
|  - Queues detected web targets automatically or on user demand          |
|  - Extracts Title, Meta Description, HTTP Status, Response Time         |
|  - Parses all HTML Tables into structured matrices                      |
|  - Harvests all Internal/External Links & Discovered Images             |
|  - Extracts Headings (H1-H6) & Body Text                                |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                      4. STORAGE & INTELLIGENCE EXPORT                   |
|  - Excel (.xlsx): Multi-sheet workbook (Overview, Tables, Links, Images)|
|  - Word (.docx): Formatted intelligence briefing report                 |
|  - JSON (.json): Full structured session dump                           |
|  - CSV (.csv): Packet stream log                                        |
|  - Batch image downloader to local folders                              |
+-------------------------------------------------------------------------+
```

---

## 🚀 Key Improvements in Version 2.0

1. **Integrated Automated Pipeline:**
   - Sniffs network traffic, catches web packets in real time (HTTP requests, TLS SNI domain handshakes, DNS queries), and automatically queues the discovered web targets for scraping.
2. **Modern CustomTkinter Dashboard:**
   - Clean, dark-themed desktop UI with sidebar navigation.
   - Live metrics cards (Total Packets, Web Targets, Scraped Targets, Engine Status).
   - Real-time searchable packet table with color-coded protocol tags (HTTP in green, HTTPS in cyan, DNS in orange).
3. **Non-Blocking Multi-Threaded Architecture:**
   - Packet capture and web scraping run in independent worker threads (`threading.Thread` and `ThreadPoolExecutor`).
   - The UI never hangs or freezes ("Not Responding") during network operations.
4. **Interactive Intelligence Inspector:**
   - Tabbed inspector for each scraped target: Overview, Tables, Links, Images, Headings & Text, and Raw HTML.
5. **Multi-Format Storage Engine:**
   - Exports directly to `.xlsx` (Excel), `.docx` (Word), `.csv`, and `.json`, and batch downloads discovered images into `data/downloads/`.
6. **Built-in Demo Simulation Mode:**
   - Allows testing the full capture ➔ scrape ➔ store pipeline without requiring administrative privileges or active network traffic.
7. **Zero Hardcoded Paths:**
   - Completely portable; works on any machine without path errors.

---

## 🛠️ Installation & Requirements

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Network Sniffing Driver (Windows)
For live raw packet capture on Windows, install [Npcap](https://npcap.com/) with **"WinPcap API-compatible Mode"** enabled. (If Npcap is not installed or administrator access is not available, use the built-in **Demo Simulation** button to test).

---

## 🖥️ Running the Application

Launch NIFRAP 2.0 with:
```bash
python run.py
```
Or via the Visual Studio solution `GUI NEW.sln` / `GUI NEW/GUI_NEW.py`.

---

## 📁 Project Structure

```
F:\GUI NEW\
├── nifrap/                     # Core application package
│   ├── config.py              # Configuration & default paths
│   ├── core/                  # Engine layer
│   │   ├── packet_parser.py   # Protocol decoders (HTTP, TLS SNI, DNS)
│   │   ├── sniffer.py         # Threaded packet capture & simulation
│   │   ├── scraper.py         # Threaded BeautifulSoup scraper
│   │   ├── storage.py         # Excel, Word, CSV, JSON export & image downloader
│   │   └── pipeline.py        # Sniff ➔ Detect ➔ Scrape ➔ Store orchestrator
│   └── gui/                   # CustomTkinter interface
│       ├── app.py             # Main application window & sidebar
│       └── views/             # Dashboard views
│           ├── sniffer_view.py# Live packet capture stream & metrics
│           ├── scraper_view.py# Scraped targets & intelligence inspector
│           ├── export_view.py # Centralized storage & export manager
│           └── settings_view.py# Activity console & diagnostics
├── data/                      # Output storage
│   ├── exports/               # Exported Excel, Word, CSV, JSON files
│   └── downloads/             # Downloaded images
├── run.py                     # Main runner
├── requirements.txt           # Dependencies
└── README.md                  # Documentation
```

