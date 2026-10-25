"""Test T03 SMTP Base64/QP (Bài 2, mục 6): MIME body có encoding phù hợp (Base64 và Quoted-Printable) → decoded body đúng + decode_status.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T03_smtp_base64_qp.test_smtp_base64_qp
"""

from pprint import pprint

from TEST import baitap2  # noqa: F401  (thêm đường dẫn module Bài 2)
from decoder import decode_event

OUTPUT = {}
for encoding, body in [("base64", "SGVsbG8="), ("quoted-printable", "Xin ch=C3=A0o")]:
    event = {"application_protocol": "SMTP", "body": body,
             "headers": {"Content-Type": "text/plain; charset=utf-8", "Content-Transfer-Encoding": encoding}}
    result = decode_event(event)
    OUTPUT[encoding] = {"body": result["body"], "decoded_body": result["decoded_body"],
                        "decode_status": result["decode_status"]}
pprint(OUTPUT, sort_dicts=False)
