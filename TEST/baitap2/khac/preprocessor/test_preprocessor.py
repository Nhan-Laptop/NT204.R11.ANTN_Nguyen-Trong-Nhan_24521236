"""Test Preprocessor (Bài 2, T05, T06, T14): in output của preprocess_event().

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.khac.preprocessor.test_preprocessor
"""

from pprint import pprint
from TEST import baitap2  # noqa: F401  (thêm đường dẫn module Bài 2)
from preprocessor import preprocess_event
from TEST.baitap2.test_helpers import sample_event


def show(title, output):
    print(f"\n[{title}]")
    pprint(output, width=130, sort_dicts=False)


def pick(event, *keys):
    return {key: event.get(key) for key in keys}


# T05: protocol, header, domain, timestamp khác kiểu chữ/format
event = sample_event(transport_protocol=" tcp ", application_protocol=" http ",
                     timestamp="2024-01-01T07:00:00+07:00",
                     headers={" HOST ": " EXAMPLE.TEST "},
                     dns_questions=[{"name": " EXAMPLE.COM. ", "type": "A"}])
result = preprocess_event(event)
show("T05 Normalization",
     {"transport": result["transport_protocol"], "app": result["application_protocol"],
      "timestamp": result["timestamp"], "headers": result["headers"],
      "dns_questions": result["dns_questions"], "preprocess_status": result["preprocess_status"]})

# T06: event thiếu field không bắt buộc
event = {name: sample_event()[name] for name in (
    "src_ip", "dst_ip", "src_port", "dst_port", "timestamp", "transport_protocol", "packet_length")}
show("T06 Missing field", pick(preprocess_event(event), "body", "tcp_flags", "dns_questions", "headers", "preprocess_status"))

# T14: event sai / không hỗ trợ
bad_events = {"src_ip sai": sample_event(src_ip="not-an-ip"), "port 65536": sample_event(dst_port=65536),
              "timestamp sai": sample_event(timestamp="bad time"),
              "protocol ICMP": sample_event(transport_protocol="ICMP"), "event rỗng": {}}
for name, event in bad_events.items():
    show(f"T14 Malformed event: {name}", pick(preprocess_event(event), "preprocess_status", "processing_action", "trackable", "reason"))
show("T14 policy skip", pick(preprocess_event({}, "skip"), "processing_action"))
