"""Test T11 Concurrent flows (Bài 2, mục 6): ≥2 flow có endpoint/port khác nhau → không gộp nhầm flow.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T11_concurrent_flows.test_concurrent_flows
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
for e in [event(), event(src_port=40001), event(dst_ip="10.0.0.3"), event(transport_protocol="UDP")]:
    track_event(tracker, e)
OUTPUT = {"so_flow": len(tracker["active_flows"])}
pprint(OUTPUT, sort_dicts=False)
