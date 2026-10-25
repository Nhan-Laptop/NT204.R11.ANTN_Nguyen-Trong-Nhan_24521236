"""Test toàn pipeline (Bài 3): chạy main.py thật với PCAP và file rule, in Detection Event ra.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap3.khac.integration.test_main
"""

import json
from pathlib import Path
from pprint import pprint
import subprocess
import sys
import tempfile

from scapy.all import Ether, IP, Raw, TCP, wrpcap

MAIN = Path(__file__).resolve().parents[4] / "main.py"
RULES = Path(__file__).parent / "input" / "web.rules"


def tcp_packet(flags, timestamp, reverse=False, payload=b""):
    source, destination = ("10.0.0.2", "10.0.0.1") if reverse else ("10.0.0.1", "10.0.0.2")
    sport, dport = (80, 40000) if reverse else (40000, 80)
    packet = Ether(src="02:00:00:00:00:01", dst="02:00:00:00:00:02") / IP(src=source, dst=destination) / TCP(
        sport=sport, dport=dport, flags=flags)
    if payload:
        packet = packet / Raw(payload)
    packet.time = timestamp
    return packet


request = b"GET /../../etc/passwd HTTP/1.1\r\nHost: example.test\r\n\r\n"
packets = [tcp_packet("S", 1700000000), tcp_packet("SA", 1700000001, reverse=True), tcp_packet("A", 1700000002),
           tcp_packet("PA", 1700000003, payload=request),
           tcp_packet("PA", 1700000004, reverse=True, payload=b"HTTP/1.1 200 OK\r\n\r\n")]

with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    wrpcap(str(directory / "input.pcap"), packets)
    command = [sys.executable, "-B", str(MAIN), "--pcap", str(directory / "input.pcap"),
               "--output", str(directory / "events.jsonl"), "--flows-output", str(directory / "flows.jsonl"),
               "--rules", str(RULES), "--detections-output", str(directory / "detections.jsonl")]
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    detections = [json.loads(line) for line in (directory / "detections.jsonl").read_text().splitlines()]
    events = (directory / "events.jsonl").read_text().splitlines()

OUTPUT = {"exit_code": result.returncode,
          "stderr": result.stderr.strip(),
          "so_event": len(events),
          "detections": [{k: d[k] for k in ("packet_id", "sid", "msg", "flow_id", "matched")} for d in detections]}
pprint(OUTPUT, width=130, sort_dicts=False)
