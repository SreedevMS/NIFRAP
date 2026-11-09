import re
import datetime
from dataclasses import dataclass
from typing import Optional

try:
    from scapy.layers.inet import IP, TCP, UDP
    from scapy.layers.http import HTTPRequest
    from scapy.layers.dns import DNS, DNSQR
    from scapy.layers.tls.all import TLSClientHello, TLS_Ext_ServerName, ServerName
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


@dataclass
class PacketInfo:
    id: int
    timestamp: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    length: int
    is_web: bool
    web_type: str  # "HTTP", "HTTPS", "DNS", or ""
    host: str
    method: str
    path: str
    target_url: str
    summary: str


def extract_sni_from_raw(payload: bytes) -> Optional[str]:
    """Parse Server Name Indication (SNI) from TLS Client Hello byte stream."""
    try:
        # TLS Record Header: Type 22 (0x16) Handshake, Version 3.x
        if len(payload) < 45 or payload[0] != 0x16:
            return None
        # Handshake Type: 1 (Client Hello)
        if payload[5] != 0x01:
            return None

        session_id_len = payload[43]
        pos = 44 + session_id_len
        if pos + 2 > len(payload):
            return None

        cipher_suites_len = int.from_bytes(payload[pos:pos+2], "big")
        pos += 2 + cipher_suites_len
        if pos + 1 > len(payload):
            return None

        compression_methods_len = payload[pos]
        pos += 1 + compression_methods_len
        if pos + 2 > len(payload):
            return None

        extensions_len = int.from_bytes(payload[pos:pos+2], "big")
        pos += 2
        end_pos = min(pos + extensions_len, len(payload))

        while pos + 4 <= end_pos:
            ext_type = int.from_bytes(payload[pos:pos+2], "big")
            ext_len = int.from_bytes(payload[pos+2:pos+4], "big")
            pos += 4

            if ext_type == 0:  # server_name extension
                if pos + 5 <= end_pos:
                    # Skip server_name_list_length (2 bytes)
                    name_type = payload[pos+2]
                    name_len = int.from_bytes(payload[pos+3:pos+5], "big")
                    if name_type == 0 and pos + 5 + name_len <= end_pos:
                        hostname = payload[pos+5:pos+5+name_len].decode("utf-8", errors="ignore")
                        return hostname.strip()
            pos += ext_len
    except Exception:
        pass
    return None


def extract_http_from_raw(payload: bytes):
    """Regex fallback to extract HTTP request method, URI, and Host header."""
    try:
        text = payload[:1024].decode("utf-8", errors="ignore")
        match = re.search(r"^(GET|POST|HEAD|PUT|DELETE|OPTIONS|PATCH)\s+([^\s]+)\s+HTTP/[0-9.]+", text)
        if match:
            method = match.group(1)
            path = match.group(2)
            host_match = re.search(r"(?i)\r\nHost:\s*([^\r\n]+)", text)
            host = host_match.group(1).strip() if host_match else ""
            return method, path, host
    except Exception:
        pass
    return None, None, None


def parse_scapy_packet(packet, packet_id: int) -> PacketInfo:
    """Parse a Scapy packet into a standardized PacketInfo structure."""
    ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    src_ip = "0.0.0.0"
    dst_ip = "0.0.0.0"
    src_port = 0
    dst_port = 0
    proto_name = "Other"
    length = len(packet)

    if SCAPY_AVAILABLE and packet.haslayer(IP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        proto = packet[IP].proto
        proto_map = {6: "TCP", 17: "UDP", 1: "ICMP", 2: "IGMP"}
        proto_name = proto_map.get(proto, f"IP-{proto}")

    if SCAPY_AVAILABLE and packet.haslayer(TCP):
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
    elif SCAPY_AVAILABLE and packet.haslayer(UDP):
        src_port = packet[UDP].sport
        dst_port = packet[UDP].dport

    is_web = False
    web_type = ""
    host = ""
    method = ""
    path = ""
    target_url = ""
    summary = f"{src_ip}:{src_port} -> {dst_ip}:{dst_port} [{proto_name}]"

    # 1. Inspect HTTP
    if SCAPY_AVAILABLE and packet.haslayer(HTTPRequest):
        try:
            req = packet[HTTPRequest]
            method = req.Method.decode("utf-8", errors="ignore") if req.Method else "GET"
            path = req.Path.decode("utf-8", errors="ignore") if req.Path else "/"
            host = req.Host.decode("utf-8", errors="ignore") if req.Host else ""
            if host:
                is_web = True
                web_type = "HTTP"
                target_url = f"http://{host}{path}"
                summary = f"HTTP {method} {target_url}"
        except Exception:
            pass

    # 2. Inspect TLS / HTTPS (Client Hello SNI)
    if not is_web and SCAPY_AVAILABLE and packet.haslayer(TLSClientHello):
        try:
            hello = packet[TLSClientHello]
            if hasattr(hello, "ext"):
                for ext in hello.ext:
                    if isinstance(ext, TLS_Ext_ServerName) and hasattr(ext, "servernames"):
                        for sn in ext.servernames:
                            if isinstance(sn, ServerName):
                                host = sn.servername.decode("utf-8", errors="ignore")
                                is_web = True
                                web_type = "HTTPS"
                                target_url = f"https://{host}/"
                                summary = f"HTTPS TLS SNI -> {host}"
                                break
        except Exception:
            pass

    # 3. Inspect DNS Queries
    if not is_web and SCAPY_AVAILABLE and packet.haslayer(DNS) and packet.haslayer(DNSQR):
        try:
            dns_layer = packet[DNSQR]
            qname = dns_layer.qname.decode("utf-8", errors="ignore").rstrip(".")
            # Filter common web domains (contains dot, not arpa)
            if "." in qname and not qname.endswith(".in-addr.arpa"):
                is_web = True
                web_type = "DNS"
                host = qname
                target_url = f"https://{host}/"
                summary = f"DNS Query -> {qname}"
        except Exception:
            pass

    # 4. Fallback Raw Payload inspection for HTTP and TLS SNI
    if not is_web and SCAPY_AVAILABLE and (packet.haslayer(TCP) or packet.haslayer(UDP)):
        payload = bytes(packet[TCP].payload) if packet.haslayer(TCP) else bytes(packet[UDP].payload)
        if payload:
            # Check for TLS SNI
            sni = extract_sni_from_raw(payload)
            if sni:
                is_web = True
                web_type = "HTTPS"
                host = sni
                target_url = f"https://{sni}/"
                summary = f"HTTPS TLS SNI -> {sni}"
            else:
                # Check for HTTP
                http_m, http_p, http_h = extract_http_from_raw(payload)
                if http_h:
                    is_web = True
                    web_type = "HTTP"
                    method = http_m or "GET"
                    path = http_p or "/"
                    host = http_h
                    target_url = f"http://{host}{path}"
                    summary = f"HTTP {method} {target_url}"

    return PacketInfo(
        id=packet_id,
        timestamp=ts,
        src_ip=src_ip,
        dst_ip=dst_ip,
        src_port=src_port,
        dst_port=dst_port,
        protocol=proto_name,
        length=length,
        is_web=is_web,
        web_type=web_type,
        host=host,
        method=method,
        path=path,
        target_url=target_url,
        summary=summary,
    )

