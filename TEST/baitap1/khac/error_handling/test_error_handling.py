"""Test xử lý lỗi (Bài 1, mục 7): packet hỏng/thiếu/cắt không được làm dừng chương trình.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap1.khac.error_handling.test_error_handling
"""

from pprint import pprint
import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

from scapy.all import Ether, IP, Raw, TCP, UDP, wrpcap

from TEST import baitap1  # noqa: F401  (thêm đường dẫn module Bài 1)
import capture
from parsers import parse_packet, validate_event


def show(title, output):
    print(f"\n[{title}]")
    pprint(output, width=130, sort_dicts=False)


broken_ip = bytearray(bytes(IP(src="10.0.0.1", dst="10.0.0.2") / UDP(sport=1, dport=2)))
broken_ip[0] = 0x43  # IPv4 header dài 12 byte là không hợp lệ

CASES = [
    ("Malformed IPv4 header", IP(bytes(broken_ip))),
    ("Transport protocol không hỗ trợ", IP(src="10.0.0.1", dst="10.0.0.2", proto=1) / Raw(load=b"\x08\x00")),
    ("Thiếu IPv4 header", Ether() / Raw(load=b"\x00" * 20)),
    ("DNS payload rỗng", IP(bytes(IP() / UDP(sport=40000, dport=53)))),
    ("TCP payload rỗng", IP(bytes(IP() / TCP(sport=40000, dport=80, flags="S")))),
    ("TCP header bị cắt", IP(src="10.0.0.1", dst="10.0.0.2", proto=6) / Raw(load=b"\x00\x01")),
    ("HTTP body không decode được",
     IP() / TCP(sport=40000, dport=80) / Raw(load=b"POST /s HTTP/1.1\r\nHost: a\r\n\r\n" + bytes([0xFF, 0xFE]))),
    ("DNS payload không decode được", IP(bytes(IP() / UDP(sport=40000, dport=53) / Raw(load=b"\xff\xfe\xfd")))),
]

for title, packet in CASES:
    event = parse_packet(packet, 1)
    show(title, {"application_protocol": event["application_protocol"], "parse_status": event["parse_status"],
                 "error": event.get("error"), "schema_errors": validate_event(event)})

# PCAP bị cắt ở cuối file: packet đọc được vẫn được xử lý, lỗi được báo lại
packet = IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=40000, dport=80) / Raw(load=b"GET / HTTP/1.1\r\n\r\n")
with tempfile.TemporaryDirectory() as directory:
    pcap = Path(directory) / "cut.pcap"
    wrpcap(str(pcap), [packet, packet])
    pcap.write_bytes(pcap.read_bytes()[:-10])
    output = io.StringIO()
    with redirect_stdout(output):
        exit_code = capture.main(["--pcap", str(pcap)])
events = [json.loads(line) for line in output.getvalue().splitlines()]
show("PCAP bị cắt cuối file", {"exit_code": exit_code,
                               "events": [{k: e.get(k) for k in ("packet_id", "parse_status", "error")} for e in events]})
