"""Test DNS Response (Bài 1, mục 9): parse ít nhất một answer.

Đọc input/dns_response.pcap, chạy capture.py thật, rồi in event trong output/dns_response.jsonl ra.
Chạy (từ thư mục gốc repo): python3 -m TEST.baitap1.dns_response.test_dns_response
"""

import json
from pathlib import Path
from pprint import pprint

from TEST import baitap1  # noqa: F401  (thêm đường dẫn module Bài 1)
import capture

HERE = Path(__file__).resolve().parent
pcap = HERE / "input" / "dns_response.pcap"
log = HERE / "output" / "dns_response.jsonl"

exit_code = capture.main(["--pcap", str(pcap), "--output", str(log)])
print("exit code:", exit_code)
for line in log.read_text(encoding="utf-8").splitlines():
    pprint(json.loads(line), sort_dicts=False)
