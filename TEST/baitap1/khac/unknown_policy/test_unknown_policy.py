"""Test policy cho gói UNKNOWN (Bài 1, mục 5): mark hoặc skip.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap1.khac.unknown_policy.test_unknown_policy
"""

from pprint import pprint
import io
import json
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from scapy.all import IP, Raw, TCP, UDP, wrpcap

from TEST import baitap1  # noqa: F401  (thêm đường dẫn module Bài 1)
import capture


def show(title, output):
    print(f"\n[{title}]")
    pprint(output, width=130, sort_dicts=False)


def run(arguments):
    """Chạy capture.main(), trả về (exit code, các event in ra stdout)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = capture.main(arguments)
        except SystemExit as exit_error:
            code = exit_error.code
    return code, [json.loads(line) for line in out.getvalue().splitlines()], err.getvalue().strip().splitlines()[-1:]


packets = [
    IP(src="10.0.0.1", dst="10.0.0.2") / UDP(sport=40000, dport=40001) / Raw(load=bytes(range(16))),  # unknown
    IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=40000, dport=40100) / Raw(load=b"GET / HTTP/1.1\r\nHost: a\r\n\r\n"),
]

with tempfile.TemporaryDirectory() as directory:
    pcap = str(Path(directory) / "mixed.pcap")
    wrpcap(pcap, packets)

    for policy in (None, "mark", "skip"):
        arguments = ["--pcap", pcap] + (["--unknown-policy", policy] if policy else [])
        code, events, _ = run(arguments)
        show(f"--unknown-policy {policy or '(mặc định)'}", {"exit_code": code, "events": [
            {key: e.get(key) for key in ("packet_id", "application_protocol", "parse_status", "payload_length")}
            for e in events]})

    code, events, message = run(["--pcap", pcap, "--unknown-policy", "drop"])
    show("--unknown-policy drop (giá trị sai)", {"exit_code": code, "events": events, "stderr": message})
