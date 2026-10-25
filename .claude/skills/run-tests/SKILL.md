---
name: run-tests
description: Run one of the repo's output tests (or all of them) and show the printed output. Use after changing parser, decoder, preprocessor, flow tracker, or main.py.
---

Run from the repository root. Each test is a plain script under `TEST/` that prints the program's output; it has no pass/fail asserts. `scapy` must be installed (`python -m pip install scapy`).

Pick the scope from `$ARGUMENTS`:

- one test: `python3 -m TEST.<group>.<folder>.test_<name>`, for example `python3 -m TEST.baitap1.http_get.test_http_get` or `python3 -m TEST.baitap2.T07_tcp_handshake.test_tcp_handshake`
  - Bài 1 folders (group `baitap1`) are named after the 12 test cases in the assignment: `tcp_handshake`, `tcp_data`, `udp`, `http_get`, `http_post`, `http_response`, `dns_query`, `dns_response`, `smtp_command`, `smtp_response`, `unknown_protocol`, `malformed_packet`
  - Bài 2 folders (group `baitap2`) are `T01_...` to `T14_...`
  - other tests live in `khac/` (for example `python3 -m TEST.baitap1.khac.capture_cli.test_capture_cli`)
- empty or `all`: run every test with the loop in `TEST/README.md`

Then compare the printed output with the expected values in that module's `readme.md` ("Input và output mong đợi") and say which cases differ. A Python traceback or a non-zero exit code is a failure.

If `ruff` is installed (`which ruff`), also run `ruff check .` and report its findings. If it is not installed, say so and skip it.

Do not edit `TEST/**/output/` files to make output match. Those files are recorded evidence; regenerate them only with the `regen-evidence` skill.
