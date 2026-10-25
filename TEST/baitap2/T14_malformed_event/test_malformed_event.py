"""Test T14 Malformed event (Bài 2, mục 6): event invalid/unsupported → không crash; status/reason phù hợp.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T14_malformed_event.test_malformed_event
"""

from pprint import pprint

from TEST import baitap2  # noqa: F401  (thêm đường dẫn module Bài 2)
from preprocessor import preprocess_event


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

bad_events = {"src_ip_sai": event(src_ip="not-an-ip"), "port_65536": event(dst_port=65536),
              "timestamp_sai": event(timestamp="bad time"), "protocol_ICMP": event(transport_protocol="ICMP"),
              "event_rong": {}}
OUTPUT = {}
for name, bad in bad_events.items():
    result = preprocess_event(bad)
    OUTPUT[name] = {"preprocess_status": result["preprocess_status"], "trackable": result["trackable"],
                    "processing_action": result["processing_action"], "reason": result["reason"]}
OUTPUT["policy_skip"] = {"processing_action": preprocess_event({}, "skip")["processing_action"]}
pprint(OUTPUT, sort_dicts=False)
