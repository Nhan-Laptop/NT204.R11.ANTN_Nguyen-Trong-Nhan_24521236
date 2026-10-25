"""Test parser (Bài 1): đưa packet vào parse_packet() và in event ra.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap1.khac.pipeline.test_pipeline
"""

from pprint import pprint
from scapy.all import DNS, DNSQR, DNSRR, IP, Raw, TCP, UDP

from TEST import baitap1  # noqa: F401  (thêm đường dẫn module Bài 1)
from parsers import parse_packet


def show(title, output):
    print(f"\n[{title}]")
    pprint(output, width=130, sort_dicts=False)


def ip():
    return IP(src="10.0.0.1", dst="10.0.0.2")


def smtp(payload, dport=25):
    return ip() / TCP(sport=40000, dport=dport, flags="PA") / Raw(load=payload)


broken_ip = bytearray(bytes(ip() / UDP(sport=1, dport=2)))
broken_ip[0] = 0x43  # IPv4 header dài 12 byte là không hợp lệ

# (tên case, packet, các field cần in)
CASES = [
    ("TCP SYN", ip() / TCP(sport=40000, dport=80, flags="S"), ["transport_protocol", "tcp_flags"]),
    ("TCP data", ip() / TCP(sport=40000, dport=9000, flags="PA") / Raw(load=b"hello tcp"),
     ["transport_protocol", "payload_length"]),
    ("UDP", ip() / UDP(sport=40000, dport=9001) / Raw(load=b"hello udp"),
     ["transport_protocol", "payload_length"]),
    ("HTTP GET (port 8080)",
     ip() / TCP(sport=40000, dport=8080) / Raw(load=b"GET /index.html HTTP/1.1\r\nHost: example.test\r\n\r\n"),
     ["application_protocol", "http_method", "http_target", "headers"]),
    ("HTTP POST có body",
     ip() / TCP(sport=40000, dport=80) / Raw(load=b"POST /login HTTP/1.1\r\nContent-Length: 10\r\n\r\nuser=alice"),
     ["http_method", "http_target", "body", "headers"]),
    ("HTTP response",
     ip() / TCP(sport=80, dport=40000) / Raw(load=b"HTTP/1.1 200 OK\r\nServer: ids-test\r\n\r\n"),
     ["http_message_type", "status_code", "reason_phrase", "headers"]),
    ("DNS query", ip() / UDP(sport=40000, dport=53) / DNS(rd=1, qd=DNSQR(qname="example.com", qtype="A")),
     ["application_protocol", "dns_is_response", "dns_questions"]),
    ("DNS response",
     ip() / UDP(sport=53, dport=40000) / DNS(qr=1, qd=DNSQR(qname="example.com"),
                                             an=DNSRR(rrname="example.com", type="A", rdata="192.0.2.10")),
     ["dns_is_response", "dns_answers"]),
    ("SMTP HELO", smtp(b"HELO mail.example\r\n"), ["application_protocol", "smtp_command", "smtp_argument"]),
    ("SMTP MAIL FROM", smtp(b"MAIL FROM:<a@example.com>\r\n"), ["smtp_command", "smtp_argument"]),
    ("SMTP RCPT TO", smtp(b"RCPT TO:<b@example.com>\r\n"), ["smtp_command", "smtp_argument"]),
    ("SMTP response", smtp(b"250 OK\r\n", dport=40000), ["smtp_message_type", "smtp_status_code", "smtp_text"]),
    ("Unknown protocol", ip() / UDP(sport=40000, dport=40001) / Raw(load=bytes(range(16))),
     ["application_protocol", "parse_status"]),
    ("Network protocol không hỗ trợ", Raw(load=b"\x01\x02\x03"), ["network_protocol", "parse_status"]),
    ("Malformed packet", IP(bytes(broken_ip)), ["parse_status", "error"]),
]

for title, packet, keys in CASES:
    event = parse_packet(IP(bytes(packet)) if packet.haslayer(IP) else packet, 1)
    show(title, {key: event.get(key) for key in keys})
