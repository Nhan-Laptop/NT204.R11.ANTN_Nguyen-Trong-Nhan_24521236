"""Test Malformed packet (Bài 1, mục 9): không crash.

Đọc input/malformed_packet.pcap, chạy capture.py thật, rồi in event trong output/malformed_packet.jsonl ra.
Chạy (từ thư mục gốc repo): python3 -m TEST.baitap1.malformed_packet.test_malformed_packet
"""

import json
from pathlib import Path
from pprint import pprint

from TEST import baitap1  # noqa: F401  (thêm đường dẫn module Bài 1)
import capture

HERE = Path(__file__).resolve().parent
pcap = HERE / "input" / "malformed_packet.pcap"
log = HERE / "output" / "malformed_packet.jsonl"

exit_code = capture.main(["--pcap", str(pcap), "--output", str(log)])
print("exit code:", exit_code)
for line in log.read_text(encoding="utf-8").splitlines():
    pprint(json.loads(line), sort_dicts=False)
