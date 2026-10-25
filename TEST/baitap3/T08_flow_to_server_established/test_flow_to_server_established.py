"""Test T08 flow:to_server,established (Bài 3, mục 7): match đúng theo Flow Tracker.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap3.T08_flow_to_server_established.test_flow_to_server_established
"""

from pathlib import Path
from pprint import pprint

from TEST import baitap3  # noqa: F401  (thêm đường dẫn module Bài 3 và Bài 2)
from flow_tracker import new_tracker, track_event
from rule_loader import load_rule_files
from rule_repository import build_repository
from rule_evaluator import evaluate_event, new_engine

RULES = Path(__file__).parent / "input" / "flow_to_server_established.rules"


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
tracker = new_tracker()
packets = [   # (mô tả, event, payload) — event đi qua Flow Tracker thật trước khi vào engine
    ("SYN mang chữ GET", event(tcp_flags=["SYN"]), b"GET"),
    ("SYN/ACK", event(reverse=True, tcp_flags=["SYN", "ACK"]), b""),
    ("ACK", event(tcp_flags=["ACK"]), b""),
    ("client gửi GET", event(tcp_flags=["PSH", "ACK"]), b"GET / HTTP/1.1"),
    ("server trả 200 OK", event(reverse=True, tcp_flags=["PSH", "ACK"]), b"HTTP/1.1 200 OK"),
]
OUTPUT = []
for mo_ta, e, payload in packets:
    e["payload_length"] = len(payload)
    e, _ = track_event(tracker, e)
    OUTPUT.append({"goi": mo_ta, "direction": e["direction"], "flow_state": e["flow_state"],
                   "sid_match": [d["sid"] for d in evaluate_event(engine, e, payload)]})
pprint(OUTPUT, sort_dicts=False)
