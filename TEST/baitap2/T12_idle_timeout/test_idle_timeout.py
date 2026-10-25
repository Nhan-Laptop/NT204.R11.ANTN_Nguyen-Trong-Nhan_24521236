"""Test T12 Idle timeout (Bài 2, mục 6): flow không có packet mới quá timeout → flow hết hạn và bị loại khỏi active table.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T12_idle_timeout.test_idle_timeout
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

tracker = new_tracker(tcp_timeout=10, udp_timeout=5)  # TCP 10 giây, UDP 5 giây
track_event(tracker, event())
track_event(tracker, event(transport_protocol="UDP"))
after_4s = expire_flows(tracker, 1700000004)
after_5s = expire_flows(tracker, 1700000005)
after_10s = expire_flows(tracker, 1700000010)
OUTPUT = {"sau_4s": {"het_han": len(after_4s)},
          "sau_5s": {"het_han": [(f["protocol"], f["state"], f["close_reason"]) for f in after_5s]},
          "sau_10s": {"het_han": [f["protocol"] for f in after_10s], "active_flows": len(tracker["active_flows"])}}
pprint(OUTPUT, sort_dicts=False)
