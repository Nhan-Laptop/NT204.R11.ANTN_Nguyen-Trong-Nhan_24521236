"""Test T08 Bidirectional flow (Bài 2, mục 6): packet A→B và B→A cùng 5-tuple đảo chiều → cùng flow_id; đúng direction.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T08_bidirectional_flow.test_bidirectional_flow
"""

from pprint import pprint

from TEST import baitap2  # noqa: F401  (thêm đường dẫn module Bài 2)
from flow_tracker import expire_flows, flow_snapshot, new_tracker, track_event


def event(reverse=False, **changes):
    """Một event TCP bình thường; mỗi case chỉ đổi những field cần thiết."""
    e = {"packet_id": 1, "timestamp": 1700000000, "network_protocol": "IPv4",
         "src_ip": "10.0.0.1", "dst_ip": "10.0.0.2", "src_port": 40000, "dst_port": 80,
         "transport_protocol": "TCP", "application_protocol": "UNKNOWN",
         "packet_length": 60, "payload_length": 0, "tcp_flags": [], "parse_status": "OK"}
    if reverse:
        e["src_ip"], e["dst_ip"] = e["dst_ip"], e["src_ip"]
        e["src_port"], e["dst_port"] = e["dst_port"], e["src_port"]
    e.update(changes)
    return e

tracker = new_tracker()
results = [track_event(tracker, e)[0] for e in [event(), event(reverse=True), event()]]
OUTPUT = {"flow_id": [r["flow_id"] for r in results], "direction": [r["direction"] for r in results]}
pprint(OUTPUT, sort_dicts=False)
