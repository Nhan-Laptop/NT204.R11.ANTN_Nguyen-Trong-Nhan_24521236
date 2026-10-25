# Bài tập 2 — Decoder, Preprocessor & Flow Tracker

## Vị trí trong app chung

Bài 2 cung cấp các bước đứng sau Parser trong **một pipeline duy nhất**:

```text
main.py
  → parser Bài 1
  → decoder.py
  → preprocessor.py
  → flow_tracker.py
  → events.jsonl + flows.jsonl
```

Không có `main.py` riêng cho Bài 2. Root `main.py` là app tích hợp; các file
trong thư mục này chỉ là module xử lý.

| File | Nhiệm vụ |
|---|---|
| `decoder.py` | Decode URI/form, HTML entity và MIME |
| `preprocessor.py` | Kiểm tra và chuẩn hóa event |
| `flow_tracker.py` | Gom packet TCP/UDP, state, timeout, statistics |

## Cách chạy app hoàn chỉnh

Chạy từ root repository:

```bash
python main.py --pcap TEST/baitap2/integration/input/pcap/http_request.pcap \
  --output events.jsonl --flows-output flows.jsonl
```

Các option chính: `--pcap` hoặc `--interface`, `--count`, `--timeout`,
`--filter`, `--tcp-timeout`, `--udp-timeout`, `--max-decode-size` và
`--invalid-policy mark|skip`.

## Chức năng

- Decoder giữ field gốc, decode URI/form/HTML/MIME và đánh dấu byte lỗi là
  `PARTIAL` thay vì crash.
- Preprocessor kiểm tra IP, port, timestamp, protocol; normalize event và
  mark/skip event lỗi.
- Flow Tracker gộp TCP/UDP hai chiều, theo dõi handshake/FIN/RST, timeout và
  statistics.
- Không thực hiện TLS decryption hoặc full TCP stream reassembly.

## Test và kết quả thực tế

14 test case bắt buộc (mục 6 của đề) nằm ở `TEST/baitap2/`, mỗi test case một folder đúng mã trong đề:
`T01_http_url_decode`, `T02_html_entity`, `T03_smtp_base64_qp`, `T04_invalid_bytes`, `T05_normalization`,
`T06_missing_field`, `T07_tcp_handshake`, `T08_bidirectional_flow`, `T09_tcp_close`, `T10_udp_query_response`,
`T11_concurrent_flows`, `T12_idle_timeout`, `T13_statistics`, `T14_malformed_event`.

Mỗi folder có file test (chạy ra output), `readme.md` đánh giá output kèm ảnh chụp terminal.
Ví dụ chạy: `python3 -m TEST.baitap2.T07_tcp_handshake.test_tcp_handshake`.
Test chạy `main.py` thật với PCAP nằm ở `TEST/baitap2/khac/integration/`. Tổng hợp ở `TEST/README.md`.
