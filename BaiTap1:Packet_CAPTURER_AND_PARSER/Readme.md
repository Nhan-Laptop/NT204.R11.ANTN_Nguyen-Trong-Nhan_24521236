# Bài tập 1 — Packet Capture & Parser

## Vị trí trong app chung

Bài 1 là **bước Parser đầu tiên** của pipeline root:

```text
main.py → capture.py → parsers.parse_packet()
       → Decoder → Preprocessor → Flow Tracker → output
```

Bài 1 không có entry point riêng. Module `capture.py` và thư mục `parsers/`
chỉ cung cấp chức năng cho app chung và cho unit test.

## Chức năng đã kiểm tra

- Đọc PCAP hoặc capture live qua interface.
- Parse Ethernet/IPv4, TCP, UDP.
- Nhận diện HTTP, DNS, SMTP và payload unknown.
- Nhận diện protocol trên một số port không chuẩn.
- Chuẩn hóa event, ghi JSON Lines và xử lý packet malformed/truncated.

## Chạy app hoàn chỉnh

Chạy từ root repository:

```bash
python main.py --pcap TEST/baitap1/parser/input/pcap/http_get.pcap \
  --output events.jsonl --flows-output flows.jsonl
```

Kết quả event sẽ đi tiếp qua Decoder, Preprocessor và Flow Tracker; vì vậy đây
không phải parser độc lập.

## Test và evidence

Test nằm ngoài module tại `TEST/baitap1/parser/`:

- `test_mandatory_cases.py`: 12 use case chính.
- `test_pipeline.py`: TCP, UDP, HTTP, DNS, SMTP và unknown.
- `test_capture_cli.py`: capture, callback, count và option.
- `test_jsonl_log.py`: JSONL, thứ tự packet, mark/skip.
- `test_error_handling.py`: malformed, truncated và capture error.
- `test_event_schema.py`: schema và JSON compatibility.
- `test_nonstandard_ports.py`: protocol trên port không chuẩn.
- `test_unknown_policy.py`: mark/skip unknown.

Kết quả thực tế: **79/79 test PASS**. Input nằm ở
`TEST/baitap1/parser/input/pcap/`; JSONL evidence và log nằm ở
`TEST/baitap1/parser/output/`. Báo cáo chi tiết ở `TEST/README.md`.
