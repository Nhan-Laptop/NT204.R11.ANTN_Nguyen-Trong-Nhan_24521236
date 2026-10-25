"""Generate the committed evidence for the section 9 mandatory test cases.

The script writes one PCAP per mandatory case, runs the real command line entry
point on it, and records the resulting JSON Lines log plus a short summary.

Usage (from the repository root):

    python TEST/baitap1/khac/mandatory_cases/make_test_pcaps.py
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

from scapy.all import wrpcap

TEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = TEST_DIR.parents[3]
BASE = TEST_DIR.parent.parent  # TEST/baitap1: mỗi test case có folder riêng
IMPLEMENTATION = REPO_ROOT / "BaiTap1:Packet_CAPTURER_AND_PARSER"
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(IMPLEMENTATION))

import capture as main  # noqa: E402  (the parser module is added above)


def load_cases():
    """Load the sibling module that builds the mandatory test packets."""
    spec = importlib.util.spec_from_file_location(
        "mandatory_cases", TEST_DIR / "mandatory_cases.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def describe(event: dict) -> str:
    """Return a one line description of the fields a case must expose."""
    fields = [
        f"packet_id={event['packet_id']}",
        f"proto={event['application_protocol']}",
        f"status={event['parse_status']}",
    ]
    extra_keys = (
        "http_message_type",
        "http_method",
        "http_target",
        "status_code",
        "dns_questions",
        "dns_answers",
        "smtp_command",
        "smtp_status_code",
        "tcp_flags",
        "payload_length",
    )
    for key in extra_keys:
        if key in event:
            fields.append(f"{key}={json.dumps(event[key], ensure_ascii=False)}")
    if "error" in event:
        fields.append(f"error={event['error']}")
    return " ".join(fields)


def main_entry() -> int:
    cases = load_cases()
    output_dir = TEST_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    lines = ["Section 9 mandatory test case evidence", "=" * 40, ""]
    for name, builder in cases.cases():
        pcap_path = BASE / name / "input" / f"{name}.pcap"
        log_path = BASE / name / "output" / f"{name}.jsonl"
        pcap_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        packets = builder()
        wrpcap(str(pcap_path), packets)
        with redirect_stdout(io.StringIO()):
            exit_code = main.main(["--pcap", str(pcap_path), "--output", str(log_path)])
        events = [
            json.loads(line)
            for line in log_path.read_text(encoding="utf-8").splitlines()
        ]
        lines.append(f"{name}: {len(packets)} packet(s), exit code {exit_code}")
        lines.extend(f"    {describe(event)}" for event in events)
        lines.append("")

    summary_path = output_dir / "summary.txt"
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"PCAP và JSONL của từng case nằm trong {BASE}/<tên case>/input và output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main_entry())
