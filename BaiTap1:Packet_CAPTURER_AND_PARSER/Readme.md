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
python main.py --pcap TEST/baitap1/http_get/input/http_get.pcap \
  --output events.jsonl --flows-output flows.jsonl
```

Kết quả event sẽ đi tiếp qua Decoder, Preprocessor và Flow Tracker; vì vậy đây
không phải parser độc lập.

## Test và evidence

12 test case bắt buộc (mục 9 của đề) nằm ở `TEST/baitap1/`, mỗi test case một folder đúng tên trong đề:
`tcp_handshake`, `tcp_data`, `udp`, `http_get`, `http_post`, `http_response`, `dns_query`, `dns_response`,
`smtp_command`, `smtp_response`, `unknown_protocol`, `malformed_packet`.

Mỗi folder có file test (chạy ra output), `readme.md` đánh giá output kèm ảnh chụp terminal, và `input/`, `output/`.
Ví dụ chạy: `python3 -m TEST.baitap1.http_get.test_http_get`.
Các test về CLI, JSONL, schema, lỗi... nằm ở `TEST/baitap1/khac/`. Tổng hợp ở `TEST/README.md`.
