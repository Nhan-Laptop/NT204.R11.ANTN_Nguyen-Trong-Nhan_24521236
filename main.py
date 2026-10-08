"""One common command-line entry point for both homework phases."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOMEWORK1 = ROOT / "BaiTap1:Packet_CAPTURER_AND_PARSER"
HOMEWORK2 = ROOT / "BaiTap2:DECODER_PREPROCESSOR_FLOW_CONNECTION_TRACKER"

# The folder names are not Python package names, so expose their modules here.
for path in (HOMEWORK1, HOMEWORK2):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import capture  # noqa: E402
import pipeline  # noqa: E402


def choose_phase(argv: list[str]) -> tuple[str, list[str]]:
    """Choose the small implementation that should receive the arguments."""
    args = list(argv)
    if args and args[0] in {"capture", "parser", "homework1"}:
        return "capture", args[1:]
    if args and args[0] in {"process", "ids", "homework2"}:
        return "process", args[1:]

    homework2_options = {
        "--flows-output",
        "--tcp-timeout",
        "--udp-timeout",
        "--max-decode-size",
        "--invalid-policy",
    }
    if any(option in args for option in homework2_options):
        return "process", args
    return "capture", args


def main(argv: list[str] | None = None) -> int:
    """Run capture/parser or the complete decoder/flow pipeline."""
    args = list(sys.argv[1:] if argv is None else argv)
    phase, args = choose_phase(args)
    if phase == "process":
        return pipeline.main(args)
    return capture.main(args)


if __name__ == "__main__":
    raise SystemExit(main())
