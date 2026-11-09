import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = DATA_DIR / "exports"
DOWNLOADS_DIR = DATA_DIR / "downloads"

# Ensure directories exist
for directory in [DATA_DIR, EXPORTS_DIR, DOWNLOADS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Default Scraping Headers
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

# Network Sniffing Defaults
DEFAULT_BPF_FILTER = "ip"
DEFAULT_TIMEOUT = 10  # HTTP request timeout in seconds
MAX_AUTO_SCRAPE_QUEUE = 50  # Max queued targets to prevent overflow

# Background Telemetry & OS noise domains (optional filter for auto-scraper)
NOISE_DOMAINS = {
    "connectivitycheck.gstatic.com",
    "dns.google",
    "vortex.data.microsoft.com",
    "watson.telemetry.microsoft.com",
    "settings-win.data.microsoft.com",
    "windowsupdate.com",
    "msftconnecttest.com",
    "telemetry.microsoft.com",
    "ocsp.digicert.com",
    "ocsp.sectigo.com",
    "in-addr.arpa",
    "ip6.arpa",
}
