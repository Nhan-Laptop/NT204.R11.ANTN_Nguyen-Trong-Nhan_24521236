"""Test TCP handshake (Bài 1, mục 9): nhận diện SYN, SYN/ACK, ACK.

Đọc input/tcp_handshake.pcap, chạy capture.py thật, rồi in event trong output/tcp_handshake.jsonl ra.
Chạy (từ thư mục gốc repo): python3 -m TEST.baitap1.tcp_handshake.test_tcp_handshake
"""

import json
from pathlib import Path
from pprint import pprint

from TEST import baitap1  # noqa: F401  (thêm đường dẫn module Bài 1)
import capture

HERE = Path(__file__).resolve().parent
pcap = HERE / "input" / "tcp_handshake.pcap"
log = HERE / "output" / "tcp_handshake.jsonl"

exit_code = capture.main(["--pcap", str(pcap), "--output", str(log)])
print("exit code:", exit_code)
for line in log.read_text(encoding="utf-8").splitlines():
    pprint(json.loads(line), sort_dicts=False)
