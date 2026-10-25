"""Test T14 Detection Event (Bài 3, mục 7): có đủ sid/msg/flow/5-tuple/protocol/match info.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap3.T14_detection_event.test_detection_event
"""

from pathlib import Path
from pprint import pprint

from TEST import baitap3  # noqa: F401  (thêm đường dẫn module Bài 3 và Bài 2)
from rule_loader import load_rule_files
from rule_repository import build_repository
from rule_evaluator import evaluate_event, new_engine

RULES = Path(__file__).parent / "input" / "detection_event.rules"


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
payload = b"GET /../etc/passwd HTTP/1.1"
detections = evaluate_event(engine, event(payload_length=len(payload)), payload)
OUTPUT = detections[0]
pprint(OUTPUT, sort_dicts=False)
