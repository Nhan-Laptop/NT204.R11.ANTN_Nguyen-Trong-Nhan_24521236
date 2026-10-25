"""Test T07 Header không match (Bài 3, mục 7): rule bị loại trước content matching.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap3.T07_header_mismatch.test_header_mismatch
"""

from pathlib import Path
from pprint import pprint

from TEST import baitap3  # noqa: F401  (thêm đường dẫn module Bài 3 và Bài 2)
from rule_loader import load_rule_files
from rule_matcher import match_rule
from rule_repository import build_repository
from rule_evaluator import evaluate_event, new_engine

RULES = Path(__file__).parent / "input" / "header_mismatch.rules"


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

rule = load_rule_files([RULES])[0]["rule"]
payload = b"GET /../etc/passwd HTTP/1.1"   # payload CÓ content "../"
e = event(dst_ip="172.16.0.9", payload_length=len(payload))   # nhưng sai IP đích
engine = new_engine(build_repository(load_rule_files([RULES])))
detections = evaluate_event(engine, e, payload)
OUTPUT = {"match_rule": match_rule(rule, e, payload),
          "so_detection": len(detections),
          "stats": engine["stats"]}
pprint(OUTPUT, sort_dicts=False)
