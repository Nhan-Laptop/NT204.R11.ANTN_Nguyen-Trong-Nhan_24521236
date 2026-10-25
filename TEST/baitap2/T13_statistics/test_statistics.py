"""Test T13 Statistics (Bài 2, mục 6): nhiều packet hai chiều → packet/byte/flag counters và duration đúng.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T13_statistics.test_statistics
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
for e in [event(tcp_flags=["SYN"], packet_length=60),
          event(reverse=True, tcp_flags=["SYN", "ACK"], packet_length=64, timestamp=1700000000.5),
          event(tcp_flags=["ACK"], packet_length=52, timestamp=1700000001),
          event(tcp_flags=["PSH", "ACK"], packet_length=100, timestamp=1700000002.5),
          event(reverse=True, tcp_flags=["ACK"], packet_length=52, timestamp=1700000003)]:
    track_event(tracker, e)
flow = flow_snapshot(next(iter(tracker["active_flows"].values())))
OUTPUT = {"packet_count": flow["packet_count"], "byte_count": flow["byte_count"],
          "forward_packet_count": flow["forward_packet_count"], "backward_packet_count": flow["backward_packet_count"],
          "SYN_count": flow["SYN_count"], "ACK_count": flow["ACK_count"], "FIN_count": flow["FIN_count"],
          "RST_count": flow["RST_count"], "duration": flow["duration"],
          "endpoint_a": flow["endpoint_a"], "endpoint_b": flow["endpoint_b"]}
pprint(OUTPUT, sort_dicts=False)
