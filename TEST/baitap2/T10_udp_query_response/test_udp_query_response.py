"""Test T10 UDP query/response (Bài 2, mục 6): DNS UDP hai chiều → 1 UDP flow, packet/byte count đúng.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T10_udp_query_response.test_udp_query_response
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
dns = dict(transport_protocol="UDP", application_protocol="DNS")
track_event(tracker, event(packet_length=70, src_port=40000, dst_port=53, **dns))
track_event(tracker, event(reverse=True, packet_length=120, src_port=53, dst_port=40000, timestamp=1700000001, **dns))
flows = [flow_snapshot(f) for f in tracker["active_flows"].values()]
OUTPUT = {"so_flow": len(flows), "protocol": flows[0]["protocol"], "application_protocol": flows[0]["application_protocol"],
          "packet_count": flows[0]["packet_count"], "byte_count": flows[0]["byte_count"]}
pprint(OUTPUT, sort_dicts=False)
