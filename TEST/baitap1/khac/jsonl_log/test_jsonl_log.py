"""Test log JSON Lines (Bài 1, mục 8): chạy capture.py và in nội dung file log.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap1.khac.jsonl_log.test_jsonl_log
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
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        return capture.main(arguments)


def read_log(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()]


def brief(events):
    return [{key: event.get(key) for key in ("packet_id", "application_protocol", "parse_status")} for event in events]


# 3 packet theo thứ tự: unknown, HTTP, DNS
packets = [
    IP(src="10.0.0.1", dst="10.0.0.2") / UDP(sport=40000, dport=40001) / Raw(load=bytes(range(16))),
    IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=40000, dport=40100) / Raw(load=b"GET / HTTP/1.1\r\nHost: a\r\n\r\n"),
    IP(src="10.0.0.1", dst="10.0.0.2") / UDP(sport=40000, dport=53) / DNS(rd=1, qd=DNSQR(qname="example.com")),
]

with tempfile.TemporaryDirectory() as directory:
    pcap, log = str(Path(directory) / "in.pcap"), str(Path(directory) / "events.jsonl")
    wrpcap(pcap, packets)

    code = run(["--pcap", pcap, "--output", log])
    text = Path(log).read_text(encoding="utf-8")
    show("Log mặc định", {"exit_code": code, "số dòng": len(text.splitlines()),
                          "kết thúc bằng xuống dòng": text.endswith("\n"), "events": brief(read_log(log))})

    code = run(["--pcap", pcap, "--output", log, "--unknown-policy", "skip"])
    show("Log với --unknown-policy skip", {"exit_code": code, "events": brief(read_log(log))})

    code = run(["--interface", "no_such_iface0", "--output", log])
    show("Lỗi capture được ghi vào log", {"exit_code": code, "log": [{"error": e.get("error"),
                                                                    "parse_status": e.get("parse_status")} for e in read_log(log)]})

    cut = Path(directory) / "cut.pcap"
    wrpcap(str(cut), packets)
    cut.write_bytes(cut.read_bytes()[:-10])
    code = run(["--pcap", str(cut), "--output", log])
    show("PCAP bị cắt cuối file", {"exit_code": code, "events": [{**{k: e.get(k) for k in ("packet_id", "parse_status")},
                                                                "error": e.get("error")} for e in read_log(log)]})
