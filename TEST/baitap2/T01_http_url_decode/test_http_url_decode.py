"""Test T01 HTTP URL decode (Bài 2, mục 6): URI chứa percent-encoding → decoded URI đúng; raw URI còn nguyên.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T01_http_url_decode.test_http_url_decode
"""

from pprint import pprint

from TEST import baitap2  # noqa: F401  (thêm đường dẫn module Bài 2)
from decoder import decode_event

event = {"application_protocol": "HTTP", "http_target": "/Search?q=%27%20OR%201%3D1",
         "headers": {"Content-Type": "application/x-www-form-urlencoded"}, "body": "name=Alice+Smith"}
result = decode_event(event)
OUTPUT = {"http_target": result["http_target"], "decoded_http_target": result["decoded_http_target"],
          "decoded_form": result["decoded_form"], "decode_status": result["decode_status"]}
pprint(OUTPUT, sort_dicts=False)
