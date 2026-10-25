"""Tests for Homework 3."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
for folder in ("BaiTap3:Core_Engine_IDS", "BaiTap2:DECODER_PREPROCESSOR_FLOW_CONNECTION_TRACKER"):
    if str(ROOT / folder) not in sys.path:
        sys.path.insert(0, str(ROOT / folder))
