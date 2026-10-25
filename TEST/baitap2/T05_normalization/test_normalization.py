"""Test T05 Normalization (Bài 2, mục 6): header/protocol/domain khác kiểu chữ hoặc format → representation sau preprocess nhất quán.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T05_normalization.test_normalization
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

raw = event(transport_protocol=" tcp ", application_protocol=" http ", timestamp="2024-01-01T07:00:00+07:00",
            headers={" HOST ": " EXAMPLE.TEST "}, dns_questions=[{"name": " EXAMPLE.COM. ", "type": "A"}])
result = preprocess_event(raw)
OUTPUT = {"transport_protocol": result["transport_protocol"], "application_protocol": result["application_protocol"],
          "timestamp": result["timestamp"], "headers": result["headers"],
          "domain": result["dns_questions"][0]["name"], "preprocess_status": result["preprocess_status"]}
pprint(OUTPUT, sort_dicts=False)
