import time
import random
import threading
from typing import Callable, Optional, Dict, Any, List
import psutil

from nifrap.core.packet_parser import parse_scapy_packet, PacketInfo

try:
    import scapy.all as scapy
    from scapy.layers.inet import IP, TCP, UDP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


def get_network_interfaces() -> List[Dict[str, Any]]:
    """Return formatted list of available network interfaces with IPs and status."""
    interfaces = []
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for iface_name, addr_list in addrs.items():
        ip_addr = "N/A"
        mac_addr = "N/A"
        for a in addr_list:
            if a.family.name == "AF_INET":
                ip_addr = a.address
            elif a.family.name in ("AF_LINK", "AF_PACKET"):
                mac_addr = a.address

        is_up = stats[iface_name].isup if iface_name in stats else False
        interfaces.append({
            "name": iface_name,
            "ip": ip_addr,
            "mac": mac_addr,
            "is_up": is_up,
            "display": f"{iface_name} ({ip_addr}) {'[UP]' if is_up else '[DOWN]'}",
        })
    return interfaces


class NetworkSniffer:
    """Thread-safe packet sniffer supporting live Scapy capture and demo simulation."""

    def __init__(
        self,
        on_packet: Callable[[PacketInfo, Optional[Any]], None],
        on_error: Optional[Callable[[str], None]] = None,
        on_status: Optional[Callable[[str], None]] = None,
    ):
        self.on_packet = on_packet
        self.on_error = on_error
        self.on_status = on_status

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._packet_count = 0
        self.is_running = False
        self.mode = "idle"  # "live", "simulation", "idle"

    def start_live(self, interface: Optional[str] = None, bpf_filter: str = "ip"):
        """Start capturing packets on the specified interface using Scapy."""
        if self.is_running:
            return

        self._stop_event.clear()
        self._packet_count = 0
        self.is_running = True
        self.mode = "live"

        if self.on_status:
            self.on_status(f"Starting live sniffer on [{interface or 'Default'}] with filter: {bpf_filter}")

        def _capture_loop():
            try:
                def _packet_callback(pkt):
                    if self._stop_event.is_set():
                        return
                    self._packet_count += 1
                    info = parse_scapy_packet(pkt, self._packet_count)
                    self.on_packet(info, pkt)

                # Use Scapy sniff with stop_filter so it terminates smoothly
                sniff_kwargs = {
                    "prn": _packet_callback,
                    "store": False,
                    "stop_filter": lambda _: self._stop_event.is_set(),
                }
                if interface and interface != "All":
                    sniff_kwargs["iface"] = interface
                if bpf_filter:
                    sniff_kwargs["filter"] = bpf_filter

                scapy.sniff(**sniff_kwargs)

            except Exception as exc:
                err_msg = str(exc)
                if "npcap" in err_msg.lower() or "winpcap" in err_msg.lower():
                    err_msg += " (Note: Windows requires Npcap driver with WinPcap compatibility for raw packet capture)."
                if self.on_error:
                    self.on_error(f"Capture error: {err_msg}")
            finally:
                self.is_running = False
                self.mode = "idle"
                if self.on_status:
                    self.on_status("Sniffing stopped.")

        self._thread = threading.Thread(target=_capture_loop, daemon=True, name="NifrapSniffer")
        self._thread.start()

    def start_simulation(self):
        """Start simulation mode for testing when running without admin privileges or active traffic."""
        if self.is_running:
            return

        self._stop_event.clear()
        self._packet_count = 0
        self.is_running = True
        self.mode = "simulation"

        if self.on_status:
            self.on_status("Simulation mode active: Generating test network & web packets...")

        simulated_web_targets = [
            ("https://httpbin.org/get", "httpbin.org", "HTTPS", "GET", "/get"),
            ("https://quotes.toscrape.com/", "quotes.toscrape.com", "HTTPS", "GET", "/"),
            ("https://books.toscrape.com/", "books.toscrape.com", "HTTPS", "GET", "/"),
            ("http://example.com/", "example.com", "HTTP", "GET", "/"),
            ("https://en.wikipedia.org/wiki/Main_Page", "en.wikipedia.org", "HTTPS", "GET", "/wiki/Main_Page"),
            ("https://news.ycombinator.com/", "news.ycombinator.com", "HTTPS", "GET", "/"),
        ]

        def _simulation_loop():
            import datetime
            while not self._stop_event.is_set():
                time.sleep(random.uniform(0.6, 1.8))
                if self._stop_event.is_set():
                    break

                self._packet_count += 1
                is_web = random.random() < 0.65  # 65% chance of web traffic
                ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]

                src_ip = f"192.168.1.{random.randint(10, 80)}"
                raw_pkt = None

                if is_web:
                    target_url, host, web_type, method, path = random.choice(simulated_web_targets)
                    src_port = random.randint(49152, 65535)
                    dst_port = 443 if web_type == "HTTPS" else (80 if web_type == "HTTP" else 53)
                    dst_ip = f"{random.randint(93, 198)}.{random.randint(10, 200)}.{random.randint(1, 250)}.{random.randint(1, 250)}"
                    info = PacketInfo(
                        id=self._packet_count,
                        timestamp=ts,
                        src_ip=src_ip,
                        dst_ip=dst_ip,
                        src_port=src_port,
                        dst_port=dst_port,
                        protocol="TCP",
                        length=random.randint(250, 1480),
                        is_web=True,
                        web_type=web_type,
                        host=host,
                        method=method,
                        path=path,
                        target_url=target_url,
                        summary=f"{web_type} {method} -> {target_url}",
                    )
                    if SCAPY_AVAILABLE:
                        raw_pkt = IP(src=src_ip, dst=dst_ip) / TCP(sport=src_port, dport=dst_port)
                else:
                    proto = random.choice(["TCP", "UDP", "ICMP"])
                    dst_ip = f"10.0.0.{random.randint(1, 254)}"
                    src_port = random.randint(1024, 65535)
                    dst_port = random.randint(1024, 65535)
                    info = PacketInfo(
                        id=self._packet_count,
                        timestamp=ts,
                        src_ip=src_ip,
                        dst_ip=dst_ip,
                        src_port=src_port,
                        dst_port=dst_port,
                        protocol=proto,
                        length=random.randint(64, 1200),
                        is_web=False,
                        web_type="",
                        host="",
                        method="",
                        path="",
                        target_url="",
                        summary=f"Background {proto} packet",
                    )
                    if SCAPY_AVAILABLE:
                        if proto == "TCP":
                            raw_pkt = IP(src=src_ip, dst=dst_ip) / TCP(sport=src_port, dport=dst_port)
                        elif proto == "UDP":
                            raw_pkt = IP(src=src_ip, dst=dst_ip) / UDP(sport=src_port, dport=dst_port)

                self.on_packet(info, raw_pkt)

            self.is_running = False
            self.mode = "idle"
            if self.on_status:
                self.on_status("Simulation stopped.")

        self._thread = threading.Thread(target=_simulation_loop, daemon=True, name="NifrapSimulation")
        self._thread.start()

    def stop(self):
        """Stop sniffing immediately."""
        if not self.is_running:
            return
        self._stop_event.set()
        self.is_running = False
        if self.on_status:
            self.on_status("Stopping sniffer...")
