"""Test Decoder (Bài 2, T01-T04): in output của decode_event() để so với mong đợi.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.khac.decoder.test_decoder
"""

from pprint import pprint
from TEST import baitap2  # noqa: F401  (thêm đường dẫn module Bài 2)
from decoder import decode_event


def show(title, output):
    print(f"\n[{title}]")
    pprint(output, width=130, sort_dicts=False)


def pick(event, *keys):
    return {key: event.get(key) for key in keys}


# T01: URI có percent-encoding
event = {"application_protocol": "HTTP", "http_target": "/Search?q=%27%20OR%201%3D1",
         "headers": {"Content-Type": "application/x-www-form-urlencoded"},
         "body": "name=Alice+Smith"}
show("T01 HTTP URL decode",
     pick(decode_event(event), "http_target", "decoded_http_target", "decoded_form", "decode_status"))

# T02: HTML entity
event = {"application_protocol": "HTTP", "headers": {"Content-Type": "text/html"},
         "body": "&lt;script&gt;x&lt;/script&gt;"}
show("T02 HTML entity", pick(decode_event(event), "body", "decoded_body", "decode_status"))

# T03: MIME Base64 và Quoted-Printable
for encoding, body in [("base64", "SGVsbG8="), ("quoted-printable", "Xin ch=C3=A0o")]:
    event = {"application_protocol": "SMTP", "body": body,
             "headers": {"Content-Type": "text/plain; charset=utf-8",
                         "Content-Transfer-Encoding": encoding}}
    show(f"T03 MIME {encoding}", pick(decode_event(event), "body", "decoded_body", "decode_status"))

# T04: byte không phải UTF-8 hợp lệ
event = {"application_protocol": "HTTP", "headers": {"Content-Type": "text/plain; charset=utf-8"}}
result = decode_event(event, b"HTTP/1.1 200 OK\r\n\r\ninvalid: \xff\xfe")
show("T04 Invalid bytes", pick(result, "decoded_body", "decode_status", "decode_reason"))
