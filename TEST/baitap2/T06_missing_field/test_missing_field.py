"""Test T06 Missing field (Bài 2, mục 6): event thiếu field không bắt buộc → xử lý null/[] nhất quán, không exception.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T06_missing_field.test_missing_field
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

needed = ("src_ip", "dst_ip", "src_port", "dst_port", "timestamp", "transport_protocol", "packet_length")
raw = {name: value for name, value in event().items() if name in needed}
result = preprocess_event(raw)
OUTPUT = {"body": result["body"], "tcp_flags": result["tcp_flags"], "dns_questions": result["dns_questions"],
          "headers": result["headers"], "preprocess_status": result["preprocess_status"]}
pprint(OUTPUT, sort_dicts=False)
