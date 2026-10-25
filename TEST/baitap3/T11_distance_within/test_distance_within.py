"""Test T11 Hai content với distance/within (Bài 3, mục 7): relative matching đúng.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap3.T11_distance_within.test_distance_within
"""

from pathlib import Path
from pprint import pprint

from TEST import baitap3  # noqa: F401  (thêm đường dẫn module Bài 3 và Bài 2)
from rule_loader import load_rule_files
from rule_matcher import match_rule

RULES = Path(__file__).parent / "input" / "distance_within.rules"


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

payload = b"GET /a.php HTTP/1.1"   # "GET" kết thúc ở byte 3, "HTTP" nằm ở byte 11..15
e = event(payload_length=len(payload))
OUTPUT = {}
for r in load_rule_files([RULES]):
    outcome = match_rule(r["rule"], e, payload)
    OUTPUT[r["rule"]["msg"]] = (outcome["result"], [(m["start"], m["end"]) for m in outcome["matched"]])
pprint(OUTPUT, sort_dicts=False)
