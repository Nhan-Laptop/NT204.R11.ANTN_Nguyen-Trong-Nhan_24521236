"""Test T09 TCP close (Bài 2, mục 6): FIN/ACK hoặc RST → flow chuyển CLOSED/RESET phù hợp.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T09_tcp_close.test_tcp_close
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
for e in [event(tcp_flags=["SYN"]), event(reverse=True, tcp_flags=["SYN", "ACK"]), event(tcp_flags=["ACK"])]:
    track_event(tracker, e)  # mở kết nối
results = [track_event(tracker, e) for e in [event(tcp_flags=["FIN", "ACK"]), event(reverse=True, tcp_flags=["ACK"]),
                                             event(reverse=True, tcp_flags=["FIN", "ACK"]), event(tcp_flags=["ACK"])]]
fin = {"flow_state": [r[0]["flow_state"] for r in results], "close_reason": results[-1][1][0]["close_reason"],
       "active_flows": len(tracker["active_flows"])}
tracker = new_tracker()
track_event(tracker, event(tcp_flags=["SYN"]))
result, done = track_event(tracker, event(reverse=True, tcp_flags=["RST", "ACK"]))
OUTPUT = {"fin": fin, "rst": {"flow_state": result["flow_state"], "close_reason": done[0]["close_reason"]}}
pprint(OUTPUT, sort_dicts=False)
