"""Test T12 flags và dsize (Bài 3, mục 7): match/không match đúng theo event.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap3.T12_flags_dsize.test_flags_dsize
"""

from pathlib import Path
from pprint import pprint

from TEST import baitap3  # noqa: F401  (thêm đường dẫn module Bài 3 và Bài 2)
from rule_loader import load_rule_files
from rule_repository import build_repository
from rule_evaluator import evaluate_event, new_engine

RULES = Path(__file__).parent / "input" / "flags_dsize.rules"


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

engine = new_engine(build_repository(load_rule_files([RULES])))
cases = {
    "SYN, payload 0": event(tcp_flags=["SYN"], payload_length=0),
    "SYN+ACK, payload 0": event(tcp_flags=["SYN", "ACK"], payload_length=0),
    "ACK, payload 12": event(tcp_flags=["ACK"], payload_length=12),
    "PSH+ACK, payload 7": event(tcp_flags=["PSH", "ACK"], payload_length=7),
}
OUTPUT = {name: [d["sid"] for d in evaluate_event(engine, e)] for name, e in cases.items()}
pprint(OUTPUT, sort_dicts=False)
