import os
import re
import time
import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

from nifrap.config import DEFAULT_HEADERS, DEFAULT_TIMEOUT


@dataclass
class ScrapedData:
    url: str
    host: str = ""
    status_code: int = 0
    content_type: str = ""
    title: str = ""
    description: str = ""
    server: str = ""
    response_time_ms: float = 0.0
    scraped_at: str = ""
    links: List[str] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)
    tables: List[List[List[str]]] = field(default_factory=list)
    headings: List[Dict[str, str]] = field(default_factory=list)
    paragraphs: List[str] = field(default_factory=list)
    raw_html: str = ""
    error: Optional[str] = None


def normalize_url(url: str) -> str:
    """Ensure URL has a valid scheme and strip fragments."""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def scrape_url(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = DEFAULT_TIMEOUT) -> ScrapedData:
    """Fetch and scrape all key elements from a web page."""
    normalized_url = normalize_url(url)
    parsed = urlparse(normalized_url)
    host = parsed.netloc

    req_headers = dict(DEFAULT_HEADERS)
    if headers:
        req_headers.update(headers)

    start_time = time.time()
    scraped_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        response = requests.get(normalized_url, headers=req_headers, timeout=timeout, allow_redirects=True)
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        content_type = response.headers.get("Content-Type", "")
        server = response.headers.get("Server", "Unknown")

        # Parse HTML if applicable
        if "html" in content_type.lower() or not content_type:
            soup = BeautifulSoup(response.text, "html.parser")

            # 1. Page Title
            title = soup.title.string.strip() if soup.title and soup.title.string else host

            # 2. Meta description
            desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            description = desc_tag.get("content", "").strip() if desc_tag else ""

            # 3. Headings (h1 - h6)
            headings = []
            for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                text = h.get_text(strip=True)
                if text:
                    headings.append({"tag": h.name.upper(), "text": text})

            # 4. Paragraphs
            paragraphs = []
            for p in soup.find_all("p"):
                text = p.get_text(strip=True)
                if text:
                    paragraphs.append(text)

            # 5. Links
            links = []
            seen_links = set()
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                abs_url = urljoin(normalized_url, href)
                if abs_url.startswith(("http://", "https://")) and abs_url not in seen_links:
                    seen_links.add(abs_url)
                    links.append(abs_url)

            # 6. Images
            images = []
            seen_imgs = set()
            for img in soup.find_all("img", src=True):
                src = img["src"].strip()
                abs_src = urljoin(normalized_url, src)
                if abs_src.startswith(("http://", "https://")) and abs_src not in seen_imgs:
                    seen_imgs.add(abs_src)
                    alt = img.get("alt", "").strip()
                    img_name = os.path.basename(urlparse(abs_src).path) or "image.png"
                    clean_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", img_name)
                    images.append({"url": abs_src, "alt": alt, "filename": clean_name})

            # 7. Tables
            tables = []
            for table in soup.find_all("table"):
                table_matrix = []
                for tr in table.find_all("tr"):
                    row_cells = [cell.get_text(strip=True) for cell in tr.find_all(["th", "td"])]
                    if row_cells:
                        table_matrix.append(row_cells)
                if table_matrix:
                    tables.append(table_matrix)

            raw_html = soup.prettify()

            return ScrapedData(
                url=response.url,
                host=host,
                status_code=response.status_code,
                content_type=content_type,
                title=title,
                description=description,
                server=server,
                response_time_ms=elapsed_ms,
                scraped_at=scraped_time,
                links=links,
                images=images,
                tables=tables,
                headings=headings,
                paragraphs=paragraphs,
                raw_html=raw_html,
                error=None,
            )
        else:
            return ScrapedData(
                url=response.url,
                host=host,
                status_code=response.status_code,
                content_type=content_type,
                title=f"Non-HTML Content ({content_type})",
                server=server,
                response_time_ms=elapsed_ms,
                scraped_at=scraped_time,
                raw_html=response.text[:5000],
                error=None,
            )

    except Exception as exc:
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        return ScrapedData(
            url=normalized_url,
            host=host,
            status_code=0,
            scraped_at=scraped_time,
            response_time_ms=elapsed_ms,
            error=str(exc),
        )


class WebScraperEngine:
    """Thread pool manager for non-blocking web scraping."""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="NifrapScraper")
        self._active_jobs = set()

    def scrape_async(
        self,
        url: str,
        on_complete: Callable[[ScrapedData], None],
        on_error: Optional[Callable[[str], None]] = None,
    ):
        """Submit URL scraping task to background pool."""
        normalized = normalize_url(url)

        def _worker():
            try:
                data = scrape_url(normalized)
                on_complete(data)
            except Exception as exc:
                if on_error:
                    on_error(str(exc))
            finally:
                self._active_jobs.discard(normalized)

        self._active_jobs.add(normalized)
        self._executor.submit(_worker)

    def shutdown(self):
        """Shutdown thread pool cleanly."""
        self._executor.shutdown(wait=False)

