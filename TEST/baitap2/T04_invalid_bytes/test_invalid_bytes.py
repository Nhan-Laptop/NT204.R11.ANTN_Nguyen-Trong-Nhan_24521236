"""Test T04 Invalid bytes (Bài 2, mục 6): Payload không phải UTF-8 hợp lệ → đánh dấu lỗi/partial; chương trình tiếp tục.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.T04_invalid_bytes.test_invalid_bytes
"""

from pprint import pprint

from TEST import baitap2  # noqa: F401  (thêm đường dẫn module Bài 2)
from decoder import decode_event

event = {"application_protocol": "HTTP", "headers": {"Content-Type": "text/plain; charset=utf-8"}}
result = decode_event(event, b"HTTP/1.1 200 OK\r\n\r\ninvalid: \xff\xfe")
OUTPUT = {"decoded_body": result["decoded_body"], "decode_status": result["decode_status"],
          "decode_reason": result["decode_reason"]}
pprint(OUTPUT, sort_dicts=False)
