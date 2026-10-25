"""Test T05 Direction -> và <> (Bài 3, mục 7): so khớp đúng chiều / bidirectional.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap3.T05_direction.test_direction
"""

from pathlib import Path
from pprint import pprint

from TEST import baitap3  # noqa: F401  (thêm đường dẫn module Bài 3 và Bài 2)
from rule_loader import load_rule_files
from rule_matcher import match_rule

RULES = Path(__file__).parent / "input" / "direction.rules"


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

rules = {r["rule"]["sid"]: r["rule"] for r in load_rule_files([RULES])}
forward = event()                 # 10.0.0.5:52133 -> 192.168.1.20:80
backward = event(reverse=True)    # 192.168.1.20:80 -> 10.0.0.5:52133
OUTPUT = {}
for sid, rule in rules.items():
    for name, e in (("forward", forward), ("backward", backward)):
        OUTPUT[f"sid {sid} ({rule['direction']}) + {name}"] = match_rule(rule, e)["result"]
pprint(OUTPUT, sort_dicts=False)
