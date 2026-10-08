# TEST — Báo cáo kiểm thử chung

`TEST/` nằm ngang hàng với `main.py` ở thư mục gốc, bên ngoài cả hai thư mục
bài tập. README này ghi **những gì đã chạy và kết quả thực tế**, không chỉ ghi
mục tiêu cần đạt.

## 1. Cấu trúc

```text
main.py
TEST/
  README.md
  baitap1/parser/
    input/                    PCAP input
    output/evidence/           JSONL evidence
    output/results/            Kết quả chạy test
    test_*.py
  baitap2/decoder/
    input/                    cases.json
    output/                   T01–T04 và tổng hợp
    test_decoder.py
  baitap2/preprocessor/       input/, output/, test_preprocessor.py
  baitap2/flow_tracker/       input/, output/, test_flow_tracker.py
  baitap2/integration/        input/PCAP, output/, test_main.py
```

Mỗi nhóm module có `input/`, file test và `output/`. Các file JSONL/PCAP trong
`output/` là dữ liệu đã sinh từ lần chạy thật; các file `.txt` là log kết quả.

## 2. Cách chạy lại

Chạy toàn bộ:

```bash
python -m unittest discover -s TEST -v
```

Chạy riêng từng nhóm:

```bash
python -m unittest discover -s TEST/baitap1/parser -v
python -m unittest discover -s TEST/baitap2/decoder -v
python -m unittest discover -s TEST/baitap2/preprocessor -v
python -m unittest discover -s TEST/baitap2/flow_tracker -v
python -m unittest discover -s TEST/baitap2/integration -v
```

Sinh lại evidence:

```bash
python TEST/baitap1/parser/make_test_pcaps.py
python TEST/baitap2/integration/make_evidence.py
```

## 3. Entry point chung

```bash
# Bài 1
python main.py capture --pcap TEST/baitap1/parser/input/pcap/http_get.pcap \
  --output events.jsonl

# Bài 2 đầy đủ
python main.py process --pcap TEST/baitap2/integration/input/pcap/http_request.pcap \
  --output events.jsonl --flows-output flows.jsonl
```

## 4. Báo cáo Bài 1 — Packet Capture & Parser

### Kết quả theo file test

| Test file | Input/use case đã chạy | Output thực tế quan sát được | Kết quả |
|---|---|---|---|
| `test_mandatory_cases.py` | 12 case: TCP handshake/data, UDP, HTTP, DNS, SMTP, unknown, malformed | `output/evidence/` có 12 PCAP/log; HTTP, DNS, SMTP nhận diện đúng; malformed có `MALFORMED`; tất cả exit code `0` | **12/12 PASS** |
| `test_pipeline.py` | TCP, UDP, HTTP, DNS, SMTP, unsupported và unknown | Event có field protocol/payload/header đúng; JSON serialize được | **13/13 PASS** |
| `test_capture_cli.py` | Live capture giả lập, PCAP, count/filter, option sai, capture lỗi | Callback dùng đúng; option sai trả `2`; lỗi capture trả `1`; interrupt trả `130` | **9/9 PASS** |
| `test_jsonl_log.py` | Nhiều packet, mark/skip, PCAP bị cắt | Mỗi dòng là JSON; thứ tự packet giữ nguyên; unknown skip đúng; lỗi truncated được ghi | **7/7 PASS** |
| `test_error_handling.py` | Header thiếu, packet malformed/truncated, byte lỗi, reader lỗi | Parser tạo `UNSUPPORTED`/`INCOMPLETE`/`MALFORMED`; packet sau vẫn chạy | **14/14 PASS** |
| `test_event_schema.py` | Event TCP/HTTP/DNS/SMTP và event sai schema | `validate_event()` trả danh sách rỗng cho event hợp lệ; JSON-compatible | **10/10 PASS** |
| `test_nonstandard_ports.py` | HTTP/DNS/SMTP trên port không chuẩn | Protocol vẫn nhận diện theo payload; payload không có cấu trúc vẫn là `UNKNOWN` | **8/8 PASS** |
| `test_unknown_policy.py` | Unknown với `mark` và `skip` | `mark` giữ diagnostic; `skip` bỏ event unknown; policy sai bị từ chối | **6/6 PASS** |

**Tổng Bài 1: 79/79 PASS — module parser/capture ĐẠT theo các test đã chạy.**

Evidence Bài 1:

- Input: `TEST/baitap1/parser/input/pcap/`.
- Output thật: `TEST/baitap1/parser/output/evidence/`.
- Log test: `TEST/baitap1/parser/output/results/all_tests.txt`.

## 5. Báo cáo Bài 2 — Decoder, Preprocessor, Flow Tracker

### Kết quả T01–T14

| ID | Input/use case đã chạy | Output thực tế | Kết quả |
|---|---|---|---|
| T01 | URI percent-encoding và form có `+` | `decoded_http_target` được giải mã; form `Alice+Smith` thành `Alice Smith`; raw target vẫn còn | **PASS** |
| T02 | Body có `&lt;script&gt;` | `decoded_body` là `<script>x</script>`; body gốc không bị ghi đè | **PASS** |
| T03 | MIME Base64 và Quoted-Printable | Body lần lượt decode thành `Hello` và `Xin chào` | **PASS** |
| T04 | Payload có byte `0xff` không hợp lệ | `decode_status=PARTIAL`, có reason; không làm dừng test sau | **PASS** |
| T05 | Protocol/header/domain/timestamp khác kiểu chữ | Event được normalize, header/domain đúng dạng chuẩn | **PASS** |
| T06 | Event thiếu field tùy chọn | Scalar/list/header được điền `null`/`[]`/`{}`; không exception | **PASS** |
| T07 | TCP `SYN → SYN/ACK → ACK` | Flow chuyển sang `ESTABLISHED` | **PASS** |
| T08 | Packet A→B và B→A | Hai packet có cùng `flow_id`; direction là forward/backward | **PASS** |
| T09 | FIN/ACK và RST | FIN tạo `CLOSING` rồi `CLOSED`; RST tạo `RESET` | **PASS** |
| T10 | DNS UDP query/response | Một flow `UDP/DNS`, packet/byte count được cập nhật | **PASS** |
| T11 | Nhiều endpoint/port đồng thời | Các connection có flow riêng, không bị gộp nhầm | **PASS** |
| T12 | Không có packet mới quá timeout | Flow được export và xóa khỏi active table | **PASS** |
| T13 | Nhiều packet hai chiều | Duration, packet/byte count và TCP flags khớp expected assertion | **PASS** |
| T14 | IP/port/time/protocol/event sai | Event được đánh `invalid`, có reason; mark/skip không làm dừng pipeline | **PASS** |

### Kết quả theo module

| Module/test file | Đã chạy | Output/log thực tế | Trạng thái |
|---|---:|---|---|
| Decoder — `test_decoder.py` | 4/4 | `TEST/baitap2/decoder/output/T01.txt`–`T04.txt`: đều `OK` | **ĐẠT** |
| Preprocessor — `test_preprocessor.py` | 3/3 | `T05.txt`, `T06.txt`, `T14.txt`: đều `OK` | **ĐẠT** |
| Flow Tracker — `test_flow_tracker.py` | 7/7 | `T07.txt`–`T13.txt`: đều `OK` | **ĐẠT** |
| Integration — `test_main.py` | 4/4 | `http_request`: 9 events/1 flow `CLOSED`; byte lỗi vẫn xử lý MIME; truncated được báo `INCOMPLETE` | **ĐẠT** |

**Tổng Bài 2: 18/18 PASS — Decoder, Preprocessor, Flow Tracker và pipeline
được nối đúng theo các test đã chạy.**

Evidence Bài 2:

- Input PCAP: `TEST/baitap2/integration/input/pcap/`.
- Output event/flow thật: `TEST/baitap2/integration/output/evidence/`.
- Log toàn bộ: `TEST/baitap2/integration/output/results/whole_suite.txt`.
- Summary flow thật: `TEST/baitap2/integration/output/evidence/summary.txt`.

## 6. Kết luận tổng

Lần chạy đã ghi nhận:

```text
Bài 1: 79/79 PASS
Bài 2: 18/18 PASS
Tổng:  97/97 PASS
```

Vì không có `FAIL` hoặc `ERROR`, các module trong phạm vi các testcase trên
được đánh dấu **ĐẠT**. Kết luận này dựa trên output/log đã lưu, không phải chỉ
là danh sách yêu cầu lý thuyết.
