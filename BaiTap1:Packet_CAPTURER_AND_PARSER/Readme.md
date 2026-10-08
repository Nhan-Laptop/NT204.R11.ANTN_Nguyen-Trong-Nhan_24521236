# Bài tập 1 — Packet Capture & Parser

## Mục tiêu

Bài 1 đọc packet từ interface hoặc PCAP, phân tích các giao thức cơ bản và
xuất event theo JSON Lines. Entry point chung nằm ở root repository:

```text
repo/main.py → BaiTap1:Packet_CAPTURER_AND_PARSER/capture.py
                         └→ parsers/
```

Bài 1 không có `main.py` riêng và không có thư mục test riêng. Tất cả test
nằm tại `TEST/baitap1/parser/`, ngang hàng với entry point chung.

## Chức năng

- Capture live packet qua interface hoặc đọc PCAP.
- Parse Ethernet/IPv4, TCP, UDP.
- Nhận diện HTTP, DNS, SMTP và payload unknown.
- Nhận diện HTTP/DNS/SMTP trên một số port không chuẩn khi nội dung đủ rõ.
- Chuẩn hóa event và kiểm tra schema.
- Ghi một JSON object trên mỗi dòng.
- Xử lý packet malformed, packet bị cắt, capture lỗi và byte không đọc được mà
  không làm dừng toàn bộ pipeline.

TCP stream reassembly, IP fragmentation reassembly và IDS rule engine chưa nằm
trong phạm vi của Bài 1.

## Cách chạy

Chạy từ thư mục root:

```bash
python main.py capture --pcap TEST/baitap1/parser/input/pcap/http_get.pcap \
  --output events.jsonl
```

Capture live (cần quyền phù hợp):

```bash
python main.py capture --interface eth0 --count 20 --output events.jsonl
```

Các option chính: `--pcap` hoặc `--interface`, `--count`, `--timeout`,
`--filter`, `--output`, `--unknown-policy mark|skip`.

## Test và evidence

Test nằm ngoài module tại `TEST/baitap1/parser/`:

- `test_mandatory_cases.py`: 12 use case chính của đề.
- `test_pipeline.py`: parser HTTP, DNS, SMTP, TCP, UDP và unknown.
- `test_capture_cli.py`: interface/PCAP, callback, count và argument.
- `test_jsonl_log.py`: JSONL, thứ tự packet, skip policy.
- `test_error_handling.py`: malformed, truncated, unsupported và capture error.
- `test_event_schema.py`: schema và JSON compatibility.
- `test_nonstandard_ports.py`: protocol trên port không chuẩn.
- `test_unknown_policy.py`: mark/skip unknown.

Input PCAP nằm trong `TEST/baitap1/parser/input/pcap/`; output thật và kết quả
chạy nằm trong `TEST/baitap1/parser/output/`. Bảng use case, expected output và
kết luận module nằm trong `TEST/README.md`.

Chạy nhóm test:

```bash
python -m unittest discover -s TEST/baitap1/parser -v
```
