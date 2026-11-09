import threading
from typing import Dict, List, Optional, Callable, Set
from collections import deque

from nifrap.core.packet_parser import PacketInfo
from nifrap.core.sniffer import NetworkSniffer, get_network_interfaces
from nifrap.core.scraper import WebScraperEngine, ScrapedData
from nifrap.config import MAX_AUTO_SCRAPE_QUEUE, NOISE_DOMAINS


class NifrapPipeline:
    """Central orchestrator bridging packet sniffing, web detection, scraping, and storage."""

    def __init__(
        self,
        on_packet: Optional[Callable[[PacketInfo], None]] = None,
        on_web_target: Optional[Callable[[Dict], None]] = None,
        on_scrape_start: Optional[Callable[[str], None]] = None,
        on_scrape_done: Optional[Callable[[ScrapedData], None]] = None,
        on_status: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        self.on_packet_cb = on_packet
        self.on_web_target_cb = on_web_target
        self.on_scrape_start_cb = on_scrape_start
        self.on_scrape_done_cb = on_scrape_done
        self.on_status_cb = on_status
        self.on_error_cb = on_error

        # Settings
        self.auto_scrape_enabled = True
        self.filter_web_only = False
        self.filter_noise_domains = True

        # In-Memory State
        self.all_packets: List[PacketInfo] = []
        self.raw_scapy_packets: List = []  # For Wireshark PCAP export
        self.web_targets: Dict[str, Dict] = {}  # host/url -> metadata
        self.scraped_results: Dict[str, ScrapedData] = {}  # url -> ScrapedData
        self.scraped_hosts: Set[str] = set()

        # Engine Components
        self.sniffer = NetworkSniffer(
            on_packet=self._handle_packet,
            on_error=self.on_error_cb,
            on_status=self.on_status_cb,
        )
        self.scraper_engine = WebScraperEngine(max_workers=4)
        self._lock = threading.Lock()

    def _handle_packet(self, packet: PacketInfo):
        with self._lock:
            self.all_packets.append(packet)

        # Notify GUI of new packet
        if self.on_packet_cb:
            if not self.filter_web_only or packet.is_web:
                self.on_packet_cb(packet)

        # If it is a web packet (HTTP / HTTPS / DNS)
        if packet.is_web and packet.target_url:
            url = packet.target_url
            host = packet.host or url

            is_new = False
            with self._lock:
                if host not in self.web_targets:
                    is_new = True
                    target_info = {
                        "host": host,
                        "url": url,
                        "web_type": packet.web_type,
                        "method": packet.method or "GET",
                        "first_seen": packet.timestamp,
                        "packet_count": 1,
                        "status": "Pending",  # Pending, Scraping, Scraped, Error
                    }
                    self.web_targets[host] = target_info
                else:
                    self.web_targets[host]["packet_count"] += 1
                    target_info = self.web_targets[host]

            if is_new and self.on_web_target_cb:
                self.on_web_target_cb(target_info)

            # Check if auto-scrape is enabled and not already scraped
            if is_new and self.auto_scrape_enabled:
                is_noise = False
                if self.filter_noise_domains:
                    is_noise = any(noise in host.lower() for noise in NOISE_DOMAINS)

                if not is_noise and len(self.scraped_hosts) < MAX_AUTO_SCRAPE_QUEUE:
                    self.scrape_target(url, host=host)

    def scrape_target(self, url: str, host: Optional[str] = None):
        """Queue target for scraping."""
        target_host = host or url
        with self._lock:
            if target_host in self.web_targets:
                self.web_targets[target_host]["status"] = "Scraping"
            self.scraped_hosts.add(target_host)

        if self.on_scrape_start_cb:
            self.on_scrape_start_cb(url)

        def _on_done(scraped_data: ScrapedData):
            with self._lock:
                self.scraped_results[url] = scraped_data
                if target_host in self.web_targets:
                    self.web_targets[target_host]["status"] = "Scraped" if not scraped_data.error else "Error"
                    self.web_targets[target_host]["title"] = scraped_data.title

            if self.on_scrape_done_cb:
                self.on_scrape_done_cb(scraped_data)

        self.scraper_engine.scrape_async(url, on_complete=_on_done)

    def start_sniffing(self, interface: Optional[str] = None, bpf_filter: str = "ip"):
        """Start capturing packets."""
        self.sniffer.start_live(interface=interface, bpf_filter=bpf_filter)

    def start_simulation(self):
        """Start simulation traffic generator."""
        self.sniffer.start_simulation()

    def stop_sniffing(self):
        """Stop packet capture."""
        self.sniffer.stop()

    def clear_session(self):
        """Reset all in-memory packet and scraping data."""
        with self._lock:
            self.all_packets.clear()
            self.raw_scapy_packets.clear()
            self.web_targets.clear()
            self.scraped_results.clear()
            self.scraped_hosts.clear()

    def shutdown(self):
        """Clean shutdown of all background services."""
        self.sniffer.stop()
        self.scraper_engine.shutdown()
