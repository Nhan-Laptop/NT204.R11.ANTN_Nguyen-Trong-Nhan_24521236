"""Test T04 Parse header (Bài 3, mục 7): TCP + any/single IP/CIDR + port/range → Internal Rule Object đúng.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap3.T04_parse_header.test_parse_header
"""

from pathlib import Path
from pprint import pprint

from TEST import baitap3  # noqa: F401  (thêm đường dẫn module Bài 3 và Bài 2)
from rule_loader import load_rule_files

RULES = Path(__file__).parent / "input" / "parse_header.rules"

HEADER = ("sid", "protocol", "src_ip", "src_port", "direction", "dst_ip", "dst_port")
results = load_rule_files([RULES])
OUTPUT = [{name: r["rule"][name] for name in HEADER} for r in results]
pprint(OUTPUT, sort_dicts=False)
