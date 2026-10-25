"""Test T02 HTML entity (Bài 2, mục 6): `&lt;...&gt;` trong text HTTP → decoded text đúng, không crash.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T02_html_entity.test_html_entity
"""

from pprint import pprint

from TEST import baitap2  # noqa: F401  (thêm đường dẫn module Bài 2)
from decoder import decode_event

event = {"application_protocol": "HTTP", "headers": {"Content-Type": "text/html"},
         "body": "&lt;script&gt;x&lt;/script&gt;"}
result = decode_event(event)
OUTPUT = {"body": result["body"], "decoded_body": result["decoded_body"], "decode_status": result["decode_status"]}
pprint(OUTPUT, sort_dicts=False)
