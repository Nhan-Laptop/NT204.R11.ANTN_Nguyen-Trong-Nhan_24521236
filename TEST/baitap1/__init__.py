"""Tests for Homework 1."""

from pathlib import Path
import sys

IMPLEMENTATION = Path(__file__).resolve().parents[2] / "BaiTap1:Packet_CAPTURER_AND_PARSER"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))
