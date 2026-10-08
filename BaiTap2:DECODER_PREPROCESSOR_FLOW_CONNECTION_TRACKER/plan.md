# Kế hoạch ngắn — Bài tập 2

## Luồng xử lý

```text
root main.py
  → pipeline.py
  → parser Bài 1
  → decoder.py
  → preprocessor.py
  → flow_tracker.py
  → events.jsonl + flows.jsonl
```

## Module

1. **Decoder:** giữ dữ liệu gốc, decode URI/form/HTML/MIME, không crash vì byte lỗi.
2. **Preprocessor:** kiểm tra field, chuẩn hóa giá trị và mark/skip event lỗi.
3. **Flow Tracker:** gộp TCP/UDP hai chiều, theo dõi state, timeout và statistics.
4. **Integration:** kiểm tra các module nối với nhau qua root `main.py`.

## Test order

| Bước | Nội dung | Test |
|---|---|---|
| 1 | Parser reuse và pipeline | integration smoke |
| 2 | URI, form, HTML | T01, T02 |
| 3 | MIME và byte lỗi | T03, T04 |
| 4 | Normalize, missing, malformed event | T05, T06, T14 |
| 5 | TCP/UDP flow và direction | T07–T11 |
| 6 | Timeout và statistics | T12, T13 |
| 7 | Chạy lại toàn bộ | `python -m unittest discover -s TEST -v` |

Không dùng TLS decryption, live capture trong test, hoặc full TCP stream
reassembly. Input/output/test của từng module nằm trong `TEST/`; mô tả chung nằm
ở `TEST/README.md`.
