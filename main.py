"""Complete NT204 IDS pipeline.

The application has one flow for every input source:

    capture/PCAP -> Packet Parser -> Decoder -> Preprocessor
                 -> Flow Tracker -> event and flow JSONL output

Homework folders contain implementation modules.  This root file is the
application orchestrator, so a later homework can add another processing step
without creating another entry point.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any, TextIO

from scapy.all import PcapReader, TCP, UDP, sniff
from scapy.error import Scapy_Exception

ROOT = Path(__file__).resolve().parent
HOMEWORK1 = ROOT / "BaiTap1:Packet_CAPTURER_AND_PARSER"
HOMEWORK2 = ROOT / "BaiTap2:DECODER_PREPROCESSOR_FLOW_CONNECTION_TRACKER"
for path in (HOMEWORK1, HOMEWORK2):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from parsers import error_event, parse_packet  # noqa: E402
from decoder import decode_event  # noqa: E402
from preprocessor import preprocess_event  # noqa: E402
from flow_tracker import finish_flows, new_tracker, track_event  # noqa: E402


def packet_to_event(packet: Any, packet_id: int) -> tuple[dict[str, Any], bytes]:
    """Reuse the Homework 1 parser and preserve raw transport payload bytes."""
    try:
        event = parse_packet(packet, packet_id)
        event["packet_length"] = len(bytes(packet))
        transport = packet.getlayer(TCP) or packet.getlayer(UDP)
        payload = bytes(transport.payload) if transport is not None else b""
        payload = payload[:event["payload_length"]]
        return event, payload
    except Exception as error:
        event = error_event(packet_id, f"packet conversion failed: {error}")
        event["packet_length"] = None
        return event, b""


def write_jsonl(output: TextIO, record: dict[str, Any]) -> None:
    """Write one JSON-compatible record and flush it immediately."""
    output.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
    output.flush()


def process_event(
    event: dict[str, Any],
    tracker: dict[str, Any],
    raw_payload: bytes | None = None,
    max_decode_size: int = 65536,
    invalid_policy: str = "mark",
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run one event through Decoder, Preprocessor and Flow Tracker."""
    try:
        decoded = decode_event(event, raw_payload, max_decode_size)
    except Exception as error:
        decoded = dict(event) if isinstance(event, dict) else {}
        decoded.update(decode_status="ERROR", decode_reason=f"decoder failed: {error}")

    try:
        processed = preprocess_event(decoded, invalid_policy)
    except Exception as error:
        return {
            "preprocess_status": "invalid",
            "trackable": False,
            "processing_action": "skip" if invalid_policy == "skip" else "mark",
            "reason": f"preprocessor failed: {error}",
            "track_status": "ERROR",
            "flow_id": None,
            "direction": None,
            "flow_state": None,
        }, []

    try:
        return track_event(tracker, processed)
    except Exception as error:
        processed.update(
            preprocess_status="invalid",
            trackable=False,
            track_status="ERROR",
            processing_action="skip" if invalid_policy == "skip" else "mark",
            reason=f"tracker failed: {error}",
            flow_id=None,
            direction=None,
            flow_state=None,
        )
        return processed, []


def handle_packet(
    packet: Any,
    packet_id: int,
    tracker: dict[str, Any],
    events: TextIO,
    flows: TextIO,
    *,
    max_decode_size: int,
    invalid_policy: str,
) -> int:
    """Run one captured packet through the complete pipeline."""
    packet_id += 1
    event, raw_payload = packet_to_event(packet, packet_id)
    event, completed = process_event(
        event,
        tracker,
        raw_payload,
        max_decode_size,
        invalid_policy,
    )
    if event.get("processing_action") != "skip":
        write_jsonl(events, event)
    for flow in completed:
        write_jsonl(flows, flow)
    return packet_id


def handle_read_error(
    message: str,
    packet_id: int,
    tracker: dict[str, Any],
    events: TextIO,
    flows: TextIO,
    *,
    invalid_policy: str,
) -> int:
    """Keep a readable error event when a PCAP record cannot be read."""
    packet_id += 1
    bad_event = error_event(packet_id, message, status="INCOMPLETE")
    processed, completed = process_event(
        bad_event,
        tracker,
        invalid_policy=invalid_policy,
    )
    if processed.get("processing_action") != "skip":
        write_jsonl(events, processed)
    for flow in completed:
        write_jsonl(flows, flow)
    return packet_id


def finish_tracker(tracker: dict[str, Any], flows: TextIO, reason: str) -> None:
    """Write all remaining active flows at the end of an input source."""
    for flow in finish_flows(tracker, reason):
        write_jsonl(flows, flow)


def run_pcap(
    pcap_file: str,
    tracker: dict[str, Any],
    events: TextIO,
    flows: TextIO,
    *,
    count: int,
    max_decode_size: int,
    invalid_policy: str,
) -> int:
    """Read a PCAP and send every readable packet into the same pipeline."""
    packet_id = 0
    end_reason = "eof"
    with PcapReader(pcap_file) as packets:
        while count == 0 or packet_id < count:
            try:
                packet = next(packets)
            except StopIteration:
                break
            except KeyboardInterrupt:
                end_reason = "interrupted"
                finish_tracker(tracker, flows, end_reason)
                return 130
            except Exception as error:
                packet_id = handle_read_error(
                    f"unreadable PCAP record: {error}",
                    packet_id,
                    tracker,
                    events,
                    flows,
                    invalid_policy=invalid_policy,
                )
                end_reason = "read_error"
                break
            packet_id = handle_packet(
                packet,
                packet_id,
                tracker,
                events,
                flows,
                max_decode_size=max_decode_size,
                invalid_policy=invalid_policy,
            )
    finish_tracker(tracker, flows, end_reason)
    return 0


def run_interface(
    interface: str,
    tracker: dict[str, Any],
    events: TextIO,
    flows: TextIO,
    *,
    count: int,
    timeout: float | None,
    packet_filter: str | None,
    max_decode_size: int,
    invalid_policy: str,
) -> int:
    """Capture live traffic and send it through the same pipeline as PCAP."""
    packet_id = 0

    def callback(packet: Any) -> None:
        nonlocal packet_id
        packet_id = handle_packet(
            packet,
            packet_id,
            tracker,
            events,
            flows,
            max_decode_size=max_decode_size,
            invalid_policy=invalid_policy,
        )

    try:
        sniff(
            iface=interface,
            prn=callback,
            count=count,
            timeout=timeout,
            filter=packet_filter,
            store=False,
        )
    except KeyboardInterrupt:
        finish_tracker(tracker, flows, "interrupted")
        return 130
    finish_tracker(tracker, flows, "eof")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the one application parser shared by all future pipeline steps."""
    parser = argparse.ArgumentParser(description="NT204 IDS processing pipeline")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--pcap", help="PCAP input file")
    source.add_argument("--interface", help="Live capture interface")
    parser.add_argument("--count", type=int, default=0, help="Packet limit; 0 means no limit")
    parser.add_argument("--timeout", type=float, help="Live capture timeout in seconds")
    parser.add_argument("--filter", dest="packet_filter", help="Live capture BPF filter")
    parser.add_argument("--output", default="events.jsonl", help="Event JSONL output")
    parser.add_argument("--flows-output", default="flows.jsonl", help="Flow JSONL output")
    parser.add_argument("--tcp-timeout", type=float, default=120)
    parser.add_argument("--udp-timeout", type=float, default=30)
    parser.add_argument("--max-decode-size", type=int, default=65536)
    parser.add_argument("--invalid-policy", choices=("mark", "skip"), default="mark")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the complete capture → parser → decoder → flow pipeline."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.count < 0:
        parser.error("--count must be zero or greater")
    if args.timeout is not None and (
        not math.isfinite(args.timeout) or args.timeout <= 0
    ):
        parser.error("--timeout must be a finite positive number")
    for name in ("tcp_timeout", "udp_timeout"):
        value = getattr(args, name)
        if not math.isfinite(value) or value <= 0:
            parser.error(f"--{name.replace('_', '-')} must be a finite positive number")
    if args.max_decode_size <= 0:
        parser.error("--max-decode-size must be positive")
    if args.pcap is not None and (args.timeout is not None or args.packet_filter is not None):
        parser.error("--timeout and --filter are only supported with --interface")

    paths = [Path(path).resolve() for path in (args.pcap or args.interface, args.output, args.flows_output)]
    if len(set(paths)) != 3:
        parser.error("input, event output and flow output must be different files")

    tracker = new_tracker(args.tcp_timeout, args.udp_timeout)
    try:
        with open(args.output, "w", encoding="utf-8") as events, open(
            args.flows_output, "w", encoding="utf-8"
        ) as flows:
            if args.pcap is not None:
                return run_pcap(
                    args.pcap,
                    tracker,
                    events,
                    flows,
                    count=args.count,
                    max_decode_size=args.max_decode_size,
                    invalid_policy=args.invalid_policy,
                )
            return run_interface(
                args.interface,
                tracker,
                events,
                flows,
                count=args.count,
                timeout=args.timeout,
                packet_filter=args.packet_filter,
                max_decode_size=args.max_decode_size,
                invalid_policy=args.invalid_policy,
            )
    except (OSError, ValueError, Scapy_Exception) as error:
        print(f"Processing failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
