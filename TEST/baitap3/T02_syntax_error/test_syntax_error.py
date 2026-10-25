"""Test T02 Rule sai cú pháp (Bài 3, mục 7): đánh dấu invalid, có lý do; engine tiếp tục chạy.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap3.T02_syntax_error.test_syntax_error
"""

from pathlib import Path
from pprint import pprint

from TEST import baitap3  # noqa: F401  (thêm đường dẫn module Bài 3 và Bài 2)
from rule_loader import load_rule_files
from rule_repository import build_repository

RULES = Path(__file__).parent / "input" / "syntax_error.rules"

results = load_rule_files([RULES])
repository = build_repository(results)
OUTPUT = {"ket_qua": [(r["line"], r["status"], r["reason"]) for r in results],
          "so_rule_dung_duoc": repository["count"]}
pprint(OUTPUT, sort_dicts=False)
