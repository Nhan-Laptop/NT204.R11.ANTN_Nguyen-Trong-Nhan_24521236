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

Test nằm ngoài module tại `TEST/baitap2/`:

| Thư mục | Test | Kết quả |
|---|---|---:|
| `decoder/` | T01–T04 | **4/4 PASS** |
| `preprocessor/` | T05, T06, T14 | **3/3 PASS** |
| `flow_tracker/` | T07–T13 | **7/7 PASS** |
| `integration/` | Chạy root `main.py` thật qua subprocess | **4/4 PASS** |

Tổng Bài 2: **18/18 PASS**. PCAP input nằm trong
`TEST/baitap2/integration/input/pcap/`; event/flow output và log nằm trong
`TEST/baitap2/integration/output/`. Báo cáo use case và output thực tế nằm ở
`TEST/README.md`.
