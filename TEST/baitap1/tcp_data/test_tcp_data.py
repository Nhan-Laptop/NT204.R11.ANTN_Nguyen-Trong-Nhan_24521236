"""Test TCP data (Bài 1, mục 9): parse TCP packet có payload.

Đọc input/tcp_data.pcap, chạy capture.py thật, rồi in event trong output/tcp_data.jsonl ra.
Chạy (từ thư mục gốc repo): python3 -m TEST.baitap1.tcp_data.test_tcp_data
"""

import json
from pathlib import Path
from pprint import pprint

from TEST import baitap1  # noqa: F401  (thêm đường dẫn module Bài 1)
import capture

HERE = Path(__file__).resolve().parent
pcap = HERE / "input" / "tcp_data.pcap"
log = HERE / "output" / "tcp_data.jsonl"

exit_code = capture.main(["--pcap", str(pcap), "--output", str(log)])
print("exit code:", exit_code)
for line in log.read_text(encoding="utf-8").splitlines():
    pprint(json.loads(line), sort_dicts=False)
