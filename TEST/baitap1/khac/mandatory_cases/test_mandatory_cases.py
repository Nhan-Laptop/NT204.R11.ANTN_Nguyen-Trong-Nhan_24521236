"""Test 12 case bắt buộc của đề Bài 1 (mục 9): chạy qua CLI thật và in event ra.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap1.khac.mandatory_cases.test_mandatory_cases
"""

from pprint import pprint
import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

from scapy.all import wrpcap

from TEST import baitap1  # noqa: F401  (thêm đường dẫn module Bài 1)
import capture
from TEST.baitap1.khac.mandatory_cases import mandatory_cases

# Với mỗi case, chỉ in những field liên quan đến yêu cầu của đề.
KEYS = {
    "tcp_handshake": ["tcp_flags"],
    "tcp_data": ["transport_protocol", "payload_length", "src_port", "dst_port"],
    "udp": ["transport_protocol", "payload_length", "dst_port"],
    "http_get": ["application_protocol", "http_method", "http_target", "http_version", "headers"],
    "http_post": ["http_method", "http_target", "body", "headers"],
    "http_response": ["http_message_type", "status_code", "reason_phrase", "headers"],
    "dns_query": ["application_protocol", "dns_is_response", "dns_questions"],
    "dns_response": ["dns_is_response", "dns_answers"],
    "smtp_command": ["smtp_command", "smtp_argument"],
    "smtp_response": ["smtp_message_type", "smtp_status_code", "smtp_text"],
    "unknown_protocol": ["application_protocol", "parse_status"],
    "malformed_packet": ["parse_status", "error"],
}


def show(title, output):
    print(f"\n[{title}]")
    pprint(output, width=130, sort_dicts=False)


for name, build_packets in mandatory_cases.cases():
    with tempfile.TemporaryDirectory() as directory:
        pcap, log = Path(directory) / "case.pcap", Path(directory) / "case.jsonl"
        wrpcap(str(pcap), build_packets())
        with redirect_stdout(io.StringIO()):
            exit_code = capture.main(["--pcap", str(pcap), "--output", str(log)])
        events = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    show(name, {"exit_code": exit_code,
                "events": [{key: event.get(key) for key in KEYS[name]} for event in events]})
