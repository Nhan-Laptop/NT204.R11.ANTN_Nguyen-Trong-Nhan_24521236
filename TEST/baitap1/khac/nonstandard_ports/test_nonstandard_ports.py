"""Test nhận diện protocol trên port không chuẩn (Bài 1, mục 5).

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap1.khac.nonstandard_ports.test_nonstandard_ports
"""

from pprint import pprint
from scapy.all import DNS, DNSQR, DNSRR, IP, Raw, TCP, UDP

from TEST import baitap1  # noqa: F401  (thêm đường dẫn module Bài 1)
from parsers import parse_packet


def show(title, output):
    print(f"\n[{title}]")
    pprint(output, width=130, sort_dicts=False)


def tcp(payload, sport, dport):
    return IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=sport, dport=dport) / Raw(load=payload)


def udp(payload, sport, dport):
    return IP(src="10.0.0.1", dst="10.0.0.2") / UDP(sport=sport, dport=dport) / Raw(load=payload)


dns_query = bytes(DNS(id=1, rd=1, qd=DNSQR(qname="example.test", qtype="A")))
dns_response = bytes(DNS(id=1, qr=1, qd=DNSQR(qname="example.test"),
                         an=DNSRR(rrname="example.test", type="A", rdata="192.0.2.7")))

CASES = [
    ("HTTP request, port 8081", tcp(b"PUT /upload HTTP/1.0\r\nHost: example.test\r\n\r\n", 40000, 8081),
     ["application_protocol", "http_method", "http_target", "http_version"]),
    ("HTTP response, port 8081", tcp(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n", 8081, 40000),
     ["application_protocol", "status_code", "reason_phrase"]),
    ("DNS query, port 5300", udp(dns_query, 40000, 5300),
     ["application_protocol", "dns_is_response", "dns_questions"]),
    ("DNS response, port 5300", udp(dns_response, 5300, 40000),
     ["application_protocol", "dns_is_response", "dns_answers"]),
    ("DNS over TCP (có length prefix), port 5300",
     tcp(len(dns_query).to_bytes(2, "big") + dns_query, 40000, 5300),
     ["application_protocol", "dns_is_response", "dns_questions"]),
    ("SMTP command, port 2525", tcp(b"EHLO mail.example.test\r\n", 40000, 2525),
     ["application_protocol", "smtp_command", "smtp_argument"]),
    ("SMTP response, port 2525", tcp(b"250 OK\r\n", 2525, 40000),
     ["application_protocol", "smtp_status_code"]),
    ("Payload không có cấu trúc, port 40100", tcp(b"unstructured-payload", 40000, 40100),
     ["application_protocol", "parse_status"]),
]

for title, packet, keys in CASES:
    event = parse_packet(IP(bytes(packet)), 1)
    show(title, {key: event.get(key) for key in keys})
