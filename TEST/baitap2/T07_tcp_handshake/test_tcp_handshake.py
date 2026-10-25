"""Test T07 TCP handshake (Bài 2, mục 6): SYN → SYN/ACK → ACK → 1 flow; trạng thái ESTABLISHED.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T07_tcp_handshake.test_tcp_handshake
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
states = []
for e in [event(tcp_flags=["SYN"]), event(reverse=True, tcp_flags=["SYN", "ACK"]), event(tcp_flags=["ACK"])]:
    states.append(track_event(tracker, e)[0]["flow_state"])
OUTPUT = {"so_flow": len(tracker["active_flows"]), "flow_state": states}
pprint(OUTPUT, sort_dicts=False)
