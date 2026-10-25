"""Test T03 Keyword ngoài phạm vi (Bài 3, mục 7): đánh dấu unsupported; không crash.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap3.T03_unsupported_keyword.test_unsupported_keyword
"""

from pathlib import Path
from pprint import pprint

from TEST import baitap3  # noqa: F401  (thêm đường dẫn module Bài 3 và Bài 2)
from rule_loader import load_rule_files

RULES = Path(__file__).parent / "input" / "unsupported_keyword.rules"

results = load_rule_files([RULES])
OUTPUT = {"ket_qua": [(r["line"], r["status"], r["reason"]) for r in results]}
pprint(OUTPUT, sort_dicts=False)
