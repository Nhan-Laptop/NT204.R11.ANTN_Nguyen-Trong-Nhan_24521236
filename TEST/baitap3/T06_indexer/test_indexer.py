"""Test T06 Indexer (Bài 3, mục 7): Repository/Indexer trả đúng tập candidate rules theo IP, TCP, UDP và any.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap3.T06_indexer.test_indexer
"""

from pathlib import Path
from pprint import pprint

from TEST import baitap3  # noqa: F401  (thêm đường dẫn module Bài 3 và Bài 2)
from rule_loader import load_rule_files
from rule_repository import build_repository, get_candidates

RULES = Path(__file__).parent / "input" / "indexer.rules"


def event(reverse=False, **changes):
    """Một event TCP bình thường; mỗi case chỉ đổi những field cần thiết."""
    e = {"packet_id": 1, "timestamp": 1700000000, "network_protocol": "IPv4",
         "src_ip": "10.0.0.5", "dst_ip": "192.168.1.20", "src_port": 52133, "dst_port": 80,
         "transport_protocol": "TCP", "application_protocol": "HTTP",
         "packet_length": 60, "payload_length": 0, "tcp_flags": ["ACK"], "parse_status": "OK",
         "flow_id": "F123", "direction": "forward", "flow_state": "ESTABLISHED"}
    if reverse:
        e["src_ip"], e["dst_ip"] = e["dst_ip"], e["src_ip"]
        e["src_port"], e["dst_port"] = e["dst_port"], e["src_port"]
    e.update(changes)
    return e

repository = build_repository(load_rule_files([RULES]))
cases = {
    "TCP -> 192.168.1.20:80": event(),
    "TCP -> 172.16.0.1:80 (IP khác)": event(dst_ip="172.16.0.1"),
    "UDP -> :53": event(transport_protocol="UDP", dst_port=53),
    "TCP -> :1500": event(dst_port=1500),
    "TCP -> :9999": event(dst_port=9999),
}
OUTPUT = {name: [r["sid"] for r in get_candidates(repository, e)] for name, e in cases.items()}
pprint(OUTPUT, sort_dicts=False)
