"""Test giao diện dòng lệnh capture.py (Bài 1, mục 2): chạy thật và in kết quả.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap1.khac.capture_cli.test_capture_cli
"""

from pprint import pprint
import io
import json
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from scapy.all import DNS, DNSQR, IP, Raw, TCP, UDP, wrpcap

from TEST import baitap1  # noqa: F401  (thêm đường dẫn module Bài 1)
import capture


def show(title, output):
    print(f"\n[{title}]")
    pprint(output, width=130, sort_dicts=False)


def run(arguments):
    """Chạy capture.main(), trả về (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = capture.main(arguments)
        except SystemExit as exit_error:  # argparse thoát bằng SystemExit
            code = exit_error.code
    return code, out.getvalue(), err.getvalue().strip().splitlines()[-1:]


packets = [
    IP(src="10.0.0.1", dst="10.0.0.2") / UDP(sport=40000, dport=40001) / Raw(load=bytes(range(16))),
    IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=40000, dport=80) / Raw(load=b"GET / HTTP/1.1\r\n\r\n"),
    IP(src="10.0.0.1", dst="10.0.0.2") / UDP(sport=40000, dport=53) / DNS(rd=1, qd=DNSQR(qname="example.com")),
]

with tempfile.TemporaryDirectory() as directory:
    pcap = str(Path(directory) / "sample.pcap")
    log = Path(directory) / "events.jsonl"
    wrpcap(pcap, packets)

    code, out, _ = run(["--pcap", pcap])
    show("--pcap (đọc cả file)", {"exit_code": code,
                                  "packet_ids": [json.loads(line)["packet_id"] for line in out.splitlines()]})

    code, out, _ = run(["--pcap", pcap, "--count", "1"])
    show("--pcap --count 1", {"exit_code": code,
                              "packet_ids": [json.loads(line)["packet_id"] for line in out.splitlines()]})

    code, out, _ = run(["--pcap", pcap, "--output", str(log)])
    show("--pcap --output file", {"exit_code": code, "stdout": out,
                                  "dòng trong file": len(log.read_text().splitlines())})

    for bad in (["--interface", "eth0", "--pcap", pcap], ["--interface", "eth0", "--count", "-1"],
                ["--interface", "eth0", "--timeout", "0"], ["--pcap", pcap, "--filter", "udp"]):
        code, _, message = run(bad)
        show(f"Tham số sai: {' '.join(bad[:2])} ...", {"exit_code": code, "stderr": message})

    code, _, message = run(["--interface", "no_such_iface0", "--count", "1"])
    show("Interface không tồn tại", {"exit_code": code, "stderr": message})
