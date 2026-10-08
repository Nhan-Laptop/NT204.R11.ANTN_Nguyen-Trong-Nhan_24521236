"""Tests for Homework 2."""

from pathlib import Path
import sys

IMPLEMENTATION = Path(__file__).resolve().parents[2] / "BaiTap2:DECODER_PREPROCESSOR_FLOW_CONNECTION_TRACKER"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))
