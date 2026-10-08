# TEST — Bài kiểm tra chung cho toàn bộ bài tập

`TEST/` nằm **ngang hàng với `main.py` ở thư mục gốc**, không nằm trong
`BaiTap1:...` hoặc `BaiTap2:...`. Các test được chia theo đúng module cần kiểm
tra. README này trả lời bốn câu hỏi: test use case nào, input là gì, output ra
sao, và module đã đạt yêu cầu chưa.

## 1. Cấu trúc

```text
repo/
  main.py                         Entry point chung
  BaiTap1:Packet_CAPTURER_AND_PARSER/
    capture.py                    Code capture/parser của Bài 1
    parsers/                      Parser dùng lại
  BaiTap2:DECODER_PREPROCESSOR_FLOW_CONNECTION_TRACKER/
    decoder.py                    Code Decoder
    preprocessor.py               Code Preprocessor
    flow_tracker.py               Code Flow Tracker
    pipeline.py                   Pipeline Bài 2
  TEST/
    README.md                     README chung này
    baitap1/parser/
      input/                      PCAP input của Bài 1
      output/                     Evidence JSONL và kết quả test
      test_*.py                   Test parser/capture
    baitap2/decoder/
      input/                      Input use case Decoder
      output/                     Kết quả T01–T04
      test_decoder.py
    baitap2/preprocessor/
      input/                      Input use case Preprocessor
      output/                     Kết quả T05, T06, T14
      test_preprocessor.py
    baitap2/flow_tracker/
      input/                      Input event TCP/UDP
      output/                     Kết quả T07–T13
      test_flow_tracker.py
    baitap2/integration/
      input/                      PCAP integration
      output/                     Events, flows và kết quả chạy thật
      test_main.py
```

Mỗi module có đủ ba phần: `input/` (dữ liệu đưa vào), `test_*.py` (cách kiểm
tra), và `output/` (kết quả/evidence). Với test unit, một số input nhỏ được tạo
trực tiếp trong file test để dễ đọc; PCAP lớn được lưu trong `input/`.

## 2. Cách chạy

Chạy từ thư mục gốc repository:

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

## 3. Entry point chung `main.py`

```bash
# Bài 1: capture/parse và ghi event JSONL
python main.py capture --pcap TEST/baitap1/parser/input/pcap/http_get.pcap \
  --output events.jsonl

# Bài 2: chạy đầy đủ parser → decoder → preprocessor → flow tracker
python main.py process --pcap TEST/baitap2/integration/input/pcap/http_request.pcap \
  --output events.jsonl --flows-output flows.jsonl
```

Có thể bỏ từ `capture`/`process` khi dùng option đặc trưng của Bài 2 như
`--flows-output`. Hai implementation bên trong vẫn là các module riêng; root
`main.py` chỉ chọn pipeline chung.

## 4. Bài 1 — Packet Capture & Parser

### Input/output và use case

| Test file | Input | Output kiểm tra | Module đạt khi |
|---|---|---|---|
| `test_mandatory_cases.py` | 12 PCAP/use case: TCP handshake, TCP data, UDP, HTTP GET/POST/response, DNS query/response, SMTP command/response, unknown, malformed | Event JSON có protocol, port, payload, HTTP/DNS/SMTP fields, lỗi rõ ràng | `parsers.parse_packet()` nhận diện đúng và không crash |
| `test_pipeline.py` | Packet TCP/UDP/HTTP/DNS/SMTP và protocol lạ | Event chuẩn hóa theo schema | Parser trả event đủ field và đúng `parse_status` |
| `test_capture_cli.py` | Fake live capture, PCAP, option sai, capture lỗi | Exit code, callback, count/filter, thông báo lỗi | `capture.py` dùng chung một callback và xử lý lỗi |
| `test_jsonl_log.py` | Nhiều packet khác protocol | Một JSON object mỗi dòng, đúng thứ tự, mark/skip | Output JSONL đọc được và packet id không sai |
| `test_error_handling.py` | Header thiếu/truncated/malformed/byte lỗi | Event `UNSUPPORTED`, `INCOMPLETE` hoặc `MALFORMED` | Một packet hỏng không dừng các packet sau |
| `test_event_schema.py` | Các event hợp lệ và lỗi | Danh sách lỗi schema rỗng | Event output đúng schema |
| `test_nonstandard_ports.py` | HTTP/DNS/SMTP trên port khác port mặc định | Application protocol vẫn được nhận diện | Nhận diện dựa trên nội dung và port hợp lý |
| `test_unknown_policy.py` | Unknown protocol với policy `mark`/`skip` | Event được giữ hoặc bỏ đúng policy | Chính sách unknown hoạt động đúng |

Evidence Bài 1 nằm tại:

- Input: `TEST/baitap1/parser/input/pcap/`.
- Output thật: `TEST/baitap1/parser/output/evidence/`.
- Kết quả từng nhóm test: `TEST/baitap1/parser/output/results/`.

## 5. Bài 2 — Decoder, Preprocessor, Flow Tracker

### Bảng testcase bắt buộc

| ID | Module | Input/use case | Output cần kiểm tra | Đạt yêu cầu khi |
|---|---|---|---|---|
| T01 | Decoder | URI percent-encoding và form có dấu `+` | `decoded_http_target`, `decoded_form`, raw field còn nguyên | Decode URI đúng; `+` chỉ thành space trong form |
| T02 | Decoder | HTML entity như `&lt;script&gt;` | `decoded_body` thành text đúng | Decode body đúng và không ghi đè body gốc |
| T03 | Decoder | MIME Base64 và Quoted-Printable | `mime_parts`, `decoded_body`, status | Chỉ decode khi header chỉ định encoding |
| T04 | Decoder | Payload có byte UTF-8 không hợp lệ | `decode_status=PARTIAL` và reason | Không crash, vẫn xử lý packet sau |
| T05 | Preprocessor | Protocol/header/domain viết hoa, timestamp | Event normalized | Chuẩn hóa đúng nhưng không đổi ý nghĩa URI/path |
| T06 | Preprocessor | Event thiếu field tùy chọn | `null`, `[]`, `{}` nhất quán | Không exception, event vẫn có schema ổn định |
| T07 | Flow Tracker | TCP `SYN → SYN/ACK → ACK` | Một flow, `ESTABLISHED` | Theo dõi handshake đúng |
| T08 | Flow Tracker | Packet A→B và B→A | Cùng `flow_id`, direction đúng | Gộp được flow hai chiều |
| T09 | Flow Tracker | FIN/ACK và RST | `CLOSING → CLOSED` hoặc `RESET` | Đóng/reset đúng state |
| T10 | Flow Tracker | DNS UDP query/response | Một flow, count/byte đúng | UDP được gom theo tuple hai chiều |
| T11 | Flow Tracker | Nhiều endpoint/port | Nhiều flow riêng | Không gộp nhầm connection |
| T12 | Flow Tracker | Không có packet mới quá timeout | Flow được export và xóa | Timeout dùng timestamp packet |
| T13 | Flow Tracker | Nhiều packet hai chiều | duration, packet/byte count, flags | Thống kê flow đúng |
| T14 | Preprocessor | IP/port/time/protocol/event sai | `invalid`, `reason`, mark/skip | Event lỗi không tạo flow và không dừng chương trình |

### Test integration qua pipeline chung

`TEST/baitap2/integration/test_main.py` chạy **root `main.py` thật** bằng
`subprocess`, không gọi tắt từng hàm. Nó kiểm tra:

| Use case | Input | Output kiểm tra |
|---|---|---|
| Parser reuse | HTTP PCAP | Event có field do parser Bài 1 tạo |
| HTTP TCP end-to-end | Handshake + request + response + FIN | Event decoded và flow `CLOSED` |
| Byte lỗi rồi MIME | HTTP payload lỗi, sau đó SMTP MIME | Packet đầu `PARTIAL`, packet sau vẫn decode |
| Invalid policy | Packet malformed với `mark`/`skip` | Event invalid được mark hoặc bỏ đúng |
| Truncated PCAP | File PCAP bị cắt | Record `INCOMPLETE`, flow đọc được vẫn được export |

Evidence Bài 2 nằm tại:

- Input PCAP: `TEST/baitap2/integration/input/pcap/`.
- Output event/flow thật: `TEST/baitap2/integration/output/evidence/`.
- Kết quả test: thư mục `output/` của từng module.

## 6. Kết quả và kết luận module

Kết quả đã kiểm tra hiện tại: **97 tests — OK** (79 test Bài 1 và 18 test
Bài 2). Bản ghi toàn bộ lần chạy nằm ở
`TEST/baitap2/integration/output/results/whole_suite.txt`. Sau khi chạy lại,
kết quả phải có `OK`, không có `FAIL` hoặc `ERROR`. Các file `.txt` trong các thư mục `output/` là bản lưu của những lần chạy đã
thực hiện; các file JSONL/PCAP là evidence để kiểm tra lại input và output.

| Module | Test chính | Kết luận cần đạt |
|---|---|---|
| Bài 1 parser/capture | 12 mandatory cases + CLI/schema/error tests | Đạt: parse packet, ghi JSONL, xử lý lỗi |
| Decoder | T01–T04 | Đạt: decode đúng và không crash vì byte lỗi |
| Preprocessor | T05, T06, T14 | Đạt: normalize/validate/mark-skip đúng |
| Flow Tracker | T07–T13 | Đạt: flow hai chiều, state, timeout, statistics đúng |
| Pipeline chung | integration tests | Đạt: các module nối đúng qua root `main.py` |

Nếu một test fail, module tương ứng **chưa được kết luận đạt**; phải đọc output
của test đó để biết input nào làm fail và field output nào sai.
