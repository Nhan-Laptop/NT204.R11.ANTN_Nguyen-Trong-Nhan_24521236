"""Test T01 Nạp file rule (Bài 3, mục 7): file có rule hợp lệ, comment và dòng trống → chỉ rule hợp lệ được đưa sang parser.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap3.T01_load_rule_file.test_load_rule_file
"""

from pathlib import Path
from pprint import pprint

from TEST import baitap3  # noqa: F401  (thêm đường dẫn module Bài 3 và Bài 2)
from rule_loader import load_rule_files

RULES = Path(__file__).parent / "input" / "load_rule_file.rules"

results = load_rule_files([RULES])
OUTPUT = {"so_dong_file": len(RULES.read_text().splitlines()),
          "so_rule_gui_cho_parser": len(results),
          "ket_qua": [(r["line"], r["status"], r["rule"]["sid"]) for r in results]}
pprint(OUTPUT, sort_dicts=False)
