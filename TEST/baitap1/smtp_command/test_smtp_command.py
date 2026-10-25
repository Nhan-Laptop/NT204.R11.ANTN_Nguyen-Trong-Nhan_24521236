"""Test SMTP command (Bài 1, mục 9): parse HELO/EHLO, MAIL FROM hoặc RCPT TO.

Đọc input/smtp_command.pcap, chạy capture.py thật, rồi in event trong output/smtp_command.jsonl ra.
Chạy (từ thư mục gốc repo): python3 -m TEST.baitap1.smtp_command.test_smtp_command
"""

import json
from pathlib import Path
from pprint import pprint

from TEST import baitap1  # noqa: F401  (thêm đường dẫn module Bài 1)
import capture

HERE = Path(__file__).resolve().parent
pcap = HERE / "input" / "smtp_command.pcap"
log = HERE / "output" / "smtp_command.jsonl"

exit_code = capture.main(["--pcap", str(pcap), "--output", str(log)])
print("exit code:", exit_code)
for line in log.read_text(encoding="utf-8").splitlines():
    pprint(json.loads(line), sort_dicts=False)
