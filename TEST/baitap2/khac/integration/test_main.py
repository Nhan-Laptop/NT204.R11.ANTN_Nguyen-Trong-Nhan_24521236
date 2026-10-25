"""Test toàn pipeline (Bài 2): chạy main.py thật với PCAP và in events/flows ra.

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.khac.integration.test_main
"""

from pprint import pprint
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from scapy.all import Ether, IP, Raw, TCP, wrpcap

MAIN = Path(__file__).resolve().parents[4] / "main.py"


def tcp_packet(flags, timestamp, reverse=False, payload=b"", seq=100, ack=0):
    source, destination = ("10.0.0.2", "10.0.0.1") if reverse else ("10.0.0.1", "10.0.0.2")
    sport, dport = (80, 40000) if reverse else (40000, 80)
    packet = Ether(src="02:00:00:00:00:01", dst="02:00:00:00:00:02") / IP(src=source, dst=destination) / TCP(
        sport=sport, dport=dport, flags=flags, seq=seq, ack=ack)
    if payload:
        packet = packet / Raw(payload)
    packet.time = timestamp
    return packet


def run_pcap(packets, *options):
    """Ghi PCAP tạm, chạy main.py, trả về (events, flows) đọc từ file JSONL."""
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        wrpcap(str(directory / "input.pcap"), packets)
        command = [sys.executable, "-B", str(MAIN), "--pcap", str(directory / "input.pcap"),
                   "--output", str(directory / "events.jsonl"),
                   "--flows-output", str(directory / "flows.jsonl"), *options]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        events = [json.loads(line) for line in (directory / "events.jsonl").read_text().splitlines()]
        flows = [json.loads(line) for line in (directory / "flows.jsonl").read_text().splitlines()]
        return result.returncode, events, flows


def show(title, output):
    print(f"\n[{title}]")
    pprint(output, width=130, sort_dicts=False)


def pick(event, *keys):
    return {key: event.get(key) for key in keys}


def http_flow():
    form = b"name=Alice+Smith&literal=%2B"
    request = (b"POST /Search?q=%27%20OR%201%3D1 HTTP/1.1\r\nHost: EXAMPLE.TEST\r\n"
               b"Content-Type: application/x-www-form-urlencoded\r\n"
               + f"Content-Length: {len(form)}\r\n\r\n".encode() + form)
    body = b"&lt;script&gt;x&lt;/script&gt;"
    response = (b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n"
                + f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
    base = 1700000000
    packets = [tcp_packet("S", base), tcp_packet("SA", base + 1, True, seq=500, ack=101),
               tcp_packet("A", base + 2, seq=101, ack=501),
               tcp_packet("PA", base + 3, payload=request, seq=101, ack=501),
               tcp_packet("PA", base + 4, True, response, seq=501, ack=101 + len(request)),
               tcp_packet("FA", base + 5, seq=101 + len(request), ack=501 + len(response)),
               tcp_packet("A", base + 6, True, seq=501 + len(response), ack=102 + len(request)),
               tcp_packet("FA", base + 7, True, seq=501 + len(response), ack=102 + len(request)),
               tcp_packet("A", base + 8, seq=102 + len(request), ack=502 + len(response))]
    code, events, flows = run_pcap(packets)
    show("HTTP end-to-end: exit code và số lượng", {"exit": code, "events": len(events), "flows": len(flows)})
    show("Trạng thái flow theo từng packet", [event["flow_state"] for event in events])
    show("Packet 4 (HTTP request) sau Decoder + Preprocessor",
         {**pick(events[3], "http_target", "decoded_http_target", "decoded_form"), "host": events[3]["headers"]["host"]})
    show("Packet 5 (HTTP response)", pick(events[4], "body", "decoded_body"))
    show("Flow xuất ra", pick(flows[0], "state", "close_reason", "application_protocol", "packet_count",
              "forward_packet_count", "backward_packet_count", "duration"))


def bad_bytes_then_mime():
    bad = tcp_packet("PA", 1700000000, payload=(
        b"HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\n\r\ninvalid: \xff"))
    mime1 = tcp_packet("PA", 1700000001, payload=(
        b"MIME-Version: 1.0\r\nContent-Type: text/plain; charset=utf-8\r\n"
        b"Content-Transfer-Encoding: base64\r\n\r\nSGVsbG8="))
    mime2 = tcp_packet("PA", 1700000002, payload=(
        b"MIME-Version: 1.0\r\nContent-Type: text/plain; charset=utf-8\r\n"
        b"Content-Transfer-Encoding: quoted-printable\r\n\r\nXin ch=C3=A0o"))
    for packet in (mime1, mime2):
        packet[TCP].sport, packet[TCP].dport = 40001, 25
    code, events, flows = run_pcap([bad, mime1, mime2])
    show("Byte lỗi rồi tới MIME", {"exit": code, "decode_status": [e["decode_status"] for e in events],
          "decoded_body": [e["decoded_body"] for e in events], "flows": len(flows)})


def bad_packet_policy():
    good = tcp_packet("PA", 1700000000, payload=b"GET / HTTP/1.1\r\nHost: a.test\r\n\r\n")
    broken = Ether(src="02:00:00:00:00:01", dst="02:00:00:00:00:02") / IP(src="10.0.0.9", dst="10.0.0.8") / TCP(sport=1, dport=2)
    broken[IP].ihl = 3
    broken.time = 1700000001
    for policy in ("mark", "skip"):
        code, events, flows = run_pcap([broken, good], "--invalid-policy", policy)
        show(f"Packet hỏng với --invalid-policy {policy}",
             {"exit": code, "events": [pick(e, "packet_id", "preprocess_status") for e in events], "flows": len(flows)})


def truncated_pcap():
    good = tcp_packet("PA", 1700000000, payload=b"GET / HTTP/1.1\r\nHost: a.test\r\n\r\n")
    with tempfile.TemporaryDirectory() as directory:
        pcap = Path(directory) / "cut.pcap"
        wrpcap(str(pcap), [good, good])
        pcap.write_bytes(pcap.read_bytes()[:-10])  # cắt bớt cuối file
        command = [sys.executable, "-B", str(MAIN), "--pcap", str(pcap), "--output",
                   str(Path(directory) / "e.jsonl"), "--flows-output", str(Path(directory) / "f.jsonl")]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        events = [json.loads(line) for line in (Path(directory) / "e.jsonl").read_text().splitlines()]
    show("PCAP bị cắt cuối file", {"exit": result.returncode, "last_event": pick(events[-1], "packet_id", "parse_status", "error")})


if __name__ == "__main__":
    http_flow()
    bad_bytes_then_mime()
    bad_packet_policy()
    truncated_pcap()
