"""Decode pcap / pcapng / cap files into a text ladder the analyzer can consume.

We pull SIP messages out of the capture (UDP/TCP port 5060 or any payload that
looks like SIP), order them by timestamp, and emit a labelled ladder so the
output reads the same way the bundled text fixtures do.

Heavy lifting is done by scapy. If scapy is not installed, importing this
module still works but `decode_pcap_to_text` raises an informative error.
"""

from __future__ import annotations

from io import BytesIO
from typing import Iterable

try:
    from scapy.all import rdpcap, IP, IPv6, UDP, TCP, Raw  # type: ignore
    _SCAPY_OK = True
    _SCAPY_ERR: Exception | None = None
except Exception as exc:  # pragma: no cover - environment-dependent
    _SCAPY_OK = False
    _SCAPY_ERR = exc

SIP_METHODS = (
    "INVITE",
    "ACK",
    "BYE",
    "CANCEL",
    "OPTIONS",
    "REGISTER",
    "REFER",
    "NOTIFY",
    "SUBSCRIBE",
    "MESSAGE",
    "INFO",
    "PRACK",
    "UPDATE",
    "PUBLISH",
)


def _looks_like_sip(payload: bytes) -> bool:
    if not payload:
        return False
    head = payload[:32]
    if head.startswith(b"SIP/2.0 "):
        return True
    try:
        first_token = head.split(b" ", 1)[0].decode("ascii", errors="ignore")
    except Exception:
        return False
    return first_token in SIP_METHODS


def _decode_payload(payload: bytes) -> str:
    # SIP is ASCII per RFC 3261; fall back gracefully for any rogue bytes.
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return payload.decode("latin-1", errors="replace")


def _summary_line(text: str) -> str:
    first = text.splitlines()[0] if text else ""
    return first.strip()


def _iter_sip_packets(packets: Iterable):
    """Yield (timestamp, src, sport, dst, dport, payload_text) for SIP packets."""
    for pkt in packets:
        if not (pkt.haslayer(UDP) or pkt.haslayer(TCP)):
            continue
        if not pkt.haslayer(Raw):
            continue
        raw_bytes = bytes(pkt[Raw].load)
        if not _looks_like_sip(raw_bytes):
            continue

        if pkt.haslayer(IP):
            src, dst = pkt[IP].src, pkt[IP].dst
        elif pkt.haslayer(IPv6):
            src, dst = pkt[IPv6].src, pkt[IPv6].dst
        else:
            src = dst = "?"

        if pkt.haslayer(UDP):
            sport, dport = pkt[UDP].sport, pkt[UDP].dport
        else:
            sport, dport = pkt[TCP].sport, pkt[TCP].dport

        ts = float(pkt.time)
        yield ts, src, sport, dst, dport, _decode_payload(raw_bytes)


def decode_pcap_to_text(file_bytes: bytes, *, max_messages: int = 80) -> str:
    """Decode a pcap/pcapng/cap byte stream into a text ladder.

    Raises:
        RuntimeError: if scapy is unavailable in the current environment.
        ValueError:   if no SIP packets are found.
    """
    if not _SCAPY_OK:
        raise RuntimeError(
            "scapy is not installed in this environment. "
            "Install it with: pip install scapy"
            + (f"  (import error: {_SCAPY_ERR})" if _SCAPY_ERR else "")
        )

    packets = rdpcap(BytesIO(file_bytes))
    sip_packets = list(_iter_sip_packets(packets))
    if not sip_packets:
        raise ValueError(
            "No SIP packets were found in this capture. The file may not contain "
            "SIP signalling, or it may use a non-standard port that the decoder "
            "did not recognise as SIP. (Decoder uses payload sniffing, not port "
            "filtering, so any plain-text SIP/2.0 traffic should be picked up.)"
        )

    sip_packets.sort(key=lambda r: r[0])
    if max_messages and len(sip_packets) > max_messages:
        sip_packets = sip_packets[:max_messages]
        truncation_note = (
            f"\n\n(Truncated to first {max_messages} SIP messages for analysis. "
            "Adjust max_messages in pcap_decoder.py to change this limit.)\n"
        )
    else:
        truncation_note = ""

    base_ts = sip_packets[0][0]
    lines: list[str] = []
    lines.append(f"# Decoded from packet capture · {len(sip_packets)} SIP messages\n")
    for i, (ts, src, sport, dst, dport, payload) in enumerate(sip_packets, start=1):
        rel = ts - base_ts
        first_line = _summary_line(payload)
        header = "=" * 78
        lines.append(header)
        lines.append(
            f"F{i}  t+{rel:7.3f}s  {src}:{sport} -> {dst}:{dport}    {first_line}"
        )
        lines.append(header)
        lines.append(payload.rstrip())
        lines.append("")

    return "\n".join(lines) + truncation_note
