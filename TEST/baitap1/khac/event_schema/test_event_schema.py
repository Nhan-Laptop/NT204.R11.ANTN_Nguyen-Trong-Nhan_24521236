"""Test cấu trúc event chuẩn (Bài 1, mục 6): in event và kết quả validate_event().

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap1.khac.event_schema.test_event_schema
"""

from pprint import pprint
import json

from scapy.all import DNS, DNSQR, IP, Raw, TCP, UDP

from TEST import baitap1  # noqa: F401  (thêm đường dẫn module Bài 1)
from parsers import parse_packet, validate_event


def show(title, output):
    print(f"\n[{title}]")
    pprint(output, width=130, sort_dicts=False)


def ip():
    return IP(src="10.0.0.1", dst="10.0.0.2")


SAMPLES = {
    "TCP": ip() / TCP(sport=40000, dport=80, flags="S"),
    "HTTP": ip() / TCP(sport=40000, dport=40100) / Raw(load=b"GET / HTTP/1.1\r\nHost: example.test\r\n\r\n"),
    "DNS": ip() / UDP(sport=40000, dport=53) / DNS(rd=1, qd=DNSQR(qname="example.test", qtype="A")),
    "SMTP": ip() / TCP(sport=40000, dport=25) / Raw(load=b"EHLO mail.example.test\r\n"),
    "UNKNOWN": ip() / UDP(sport=40000, dport=40001) / Raw(load=b"unstructured-payload"),
}

events = {}
for name, packet in SAMPLES.items():
    events[name] = parse_packet(packet, 1)
    show(f"Event {name}: validate_event() và JSON", {
        "application_protocol": events[name]["application_protocol"],
        "schema_errors": validate_event(events[name]),
        "json_ok": json.loads(json.dumps(events[name])) == events[name]})

show("Các field của event HTTP", sorted(events["HTTP"]))

# Sửa event để xem validate_event() báo lỗi gì
broken = dict(events["TCP"])
del broken["src_ip"]
show("Event thiếu src_ip", validate_event(broken))
show("Event sai giá trị", validate_event(dict(events["TCP"], application_protocol="BAD", src_port=70000)))
show("Event có giá trị không JSON", validate_event(dict(events["TCP"], timestamp=object())))
show("Event có field không có trong schema", validate_event(dict(events["TCP"], hacker_field=1)))
