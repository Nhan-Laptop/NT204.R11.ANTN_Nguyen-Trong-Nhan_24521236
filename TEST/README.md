# TEST — Tổng hợp kiểm thử

Mỗi test case của đề là **một folder riêng, đặt đúng tên trong đề**. Trong folder có một file test
(chạy chương trình và **in output ra**), `readme.md` (đánh giá output có đúng mong đợi không, kèm ảnh chụp
terminal) và `input/`, `output/`. Kết quả dưới đây là lần chạy ngày **2026-10-13** (Bài 1, 2) và **2026-10-25** (Bài 3).

## Cách chạy

Từ thư mục gốc repo, chạy từng test bằng `python3 -m`, ví dụ:

```bash
python3 -m TEST.baitap1.tcp_handshake.test_tcp_handshake
python3 -m TEST.baitap2.T07_tcp_handshake.test_tcp_handshake
python3 -m TEST.baitap3.T09_content_nocase.test_content_nocase
```

Chạy lần lượt tất cả:

```bash
for f in TEST/baitap*/*/test_*.py TEST/baitap*/khac/*/test_*.py; do
  python3 -m $(echo ${f%.py} | tr / .)
done
```

## Bài 1 — Test cases bắt buộc (mục 9 của đề)

| Folder | Test (theo đề) | Yêu cầu của đề | Đánh giá | Chi tiết |
|---|---|---|---|---|
| `tcp_handshake` | TCP handshake | Nhận diện SYN, SYN/ACK, ACK | ĐẠT | [readme](baitap1/tcp_handshake/readme.md) |
| `tcp_data` | TCP data | Parse TCP packet có payload | ĐẠT | [readme](baitap1/tcp_data/readme.md) |
| `udp` | UDP | Parse UDP packet | ĐẠT | [readme](baitap1/udp/readme.md) |
| `http_get` | HTTP GET | Parse HTTP request | ĐẠT | [readme](baitap1/http_get/readme.md) |
| `http_post` | HTTP POST | Parse HTTP request có body | ĐẠT | [readme](baitap1/http_post/readme.md) |
| `http_response` | HTTP response | Parse status code và header | ĐẠT | [readme](baitap1/http_response/readme.md) |
| `dns_query` | DNS Query | Parse domain và query type | ĐẠT | [readme](baitap1/dns_query/readme.md) |
| `dns_response` | DNS Response | Parse ít nhất một answer | ĐẠT | [readme](baitap1/dns_response/readme.md) |
| `smtp_command` | SMTP command | Parse HELO/EHLO, MAIL FROM hoặc RCPT TO | ĐẠT | [readme](baitap1/smtp_command/readme.md) |
| `smtp_response` | SMTP response | Parse SMTP status code | ĐẠT | [readme](baitap1/smtp_response/readme.md) |
| `unknown_protocol` | Unknown protocol | Không crash | ĐẠT | [readme](baitap1/unknown_protocol/readme.md) |
| `malformed_packet` | Malformed packet | Không crash | ĐẠT | [readme](baitap1/malformed_packet/readme.md) |

## Bài 2 — Test cases bắt buộc (mục 6 của đề)

| Folder | Test (theo đề) | Kết quả mong đợi của đề | Đánh giá | Chi tiết |
|---|---|---|---|---|
| `T01_http_url_decode` | T01 HTTP URL decode | decoded URI đúng; raw URI còn nguyên | ĐẠT | [readme](baitap2/T01_http_url_decode/readme.md) |
| `T02_html_entity` | T02 HTML entity | decoded text đúng, không crash | ĐẠT | [readme](baitap2/T02_html_entity/readme.md) |
| `T03_smtp_base64_qp` | T03 SMTP Base64/QP | decoded body đúng + decode_status | ĐẠT | [readme](baitap2/T03_smtp_base64_qp/readme.md) |
| `T04_invalid_bytes` | T04 Invalid bytes | đánh dấu lỗi/partial; chương trình tiếp tục | ĐẠT | [readme](baitap2/T04_invalid_bytes/readme.md) |
| `T05_normalization` | T05 Normalization | representation sau preprocess nhất quán | ĐẠT | [readme](baitap2/T05_normalization/readme.md) |
| `T06_missing_field` | T06 Missing field | xử lý null/[] nhất quán, không exception | ĐẠT | [readme](baitap2/T06_missing_field/readme.md) |
| `T07_tcp_handshake` | T07 TCP handshake | 1 flow; trạng thái ESTABLISHED | ĐẠT | [readme](baitap2/T07_tcp_handshake/readme.md) |
| `T08_bidirectional_flow` | T08 Bidirectional flow | cùng flow_id; đúng direction | ĐẠT | [readme](baitap2/T08_bidirectional_flow/readme.md) |
| `T09_tcp_close` | T09 TCP close | flow chuyển CLOSED/RESET phù hợp | ĐẠT | [readme](baitap2/T09_tcp_close/readme.md) |
| `T10_udp_query_response` | T10 UDP query/response | 1 UDP flow, packet/byte count đúng | ĐẠT | [readme](baitap2/T10_udp_query_response/readme.md) |
| `T11_concurrent_flows` | T11 Concurrent flows | không gộp nhầm flow | ĐẠT | [readme](baitap2/T11_concurrent_flows/readme.md) |
| `T12_idle_timeout` | T12 Idle timeout | flow hết hạn và bị loại khỏi active table | ĐẠT | [readme](baitap2/T12_idle_timeout/readme.md) |
| `T13_statistics` | T13 Statistics | packet/byte/flag counters và duration đúng | ĐẠT | [readme](baitap2/T13_statistics/readme.md) |
| `T14_malformed_event` | T14 Malformed event | không crash; status/reason phù hợp | ĐẠT | [readme](baitap2/T14_malformed_event/readme.md) |

## Bài 3 — Test cases bắt buộc (mục 7 của đề)

Đề ghi thư mục `TEST/BT3`; repo dùng `TEST/baitap3` cho thống nhất với Bài 1, Bài 2.

| Folder | Test (theo đề) | Kết quả mong đợi của đề | Đánh giá | Chi tiết |
|---|---|---|---|---|
| `T01_load_rule_file` | T01 Nạp file rule | Chỉ rule hợp lệ được đưa sang parser | ĐẠT | [readme](baitap3/T01_load_rule_file/readme.md) |
| `T02_syntax_error` | T02 Rule sai cú pháp | invalid, có lý do; engine tiếp tục chạy | ĐẠT | [readme](baitap3/T02_syntax_error/readme.md) |
| `T03_unsupported_keyword` | T03 Keyword ngoài phạm vi | unsupported; không crash | ĐẠT | [readme](baitap3/T03_unsupported_keyword/readme.md) |
| `T04_parse_header` | T04 Parse header | Internal Rule Object đúng | ĐẠT | [readme](baitap3/T04_parse_header/readme.md) |
| `T05_direction` | T05 Direction `->` và `<>` | đúng chiều / bidirectional | ĐẠT | [readme](baitap3/T05_direction/readme.md) |
| `T06_indexer` | T06 Indexer | đúng tập candidate rules | ĐẠT | [readme](baitap3/T06_indexer/readme.md) |
| `T07_header_mismatch` | T07 Header không match | rule bị loại trước content matching | ĐẠT | [readme](baitap3/T07_header_mismatch/readme.md) |
| `T08_flow_to_server_established` | T08 flow:to_server,established | match đúng theo Flow Tracker | ĐẠT | [readme](baitap3/T08_flow_to_server_established/readme.md) |
| `T09_content_nocase` | T09 content có/không có nocase | phân biệt/không phân biệt hoa thường đúng | ĐẠT | [readme](baitap3/T09_content_nocase/readme.md) |
| `T10_offset_depth` | T10 offset/depth | chỉ match trong vùng được chỉ định | ĐẠT | [readme](baitap3/T10_offset_depth/readme.md) |
| `T11_distance_within` | T11 Hai content với distance/within | relative matching đúng | ĐẠT | [readme](baitap3/T11_distance_within/readme.md) |
| `T12_flags_dsize` | T12 flags và dsize | match/không match đúng theo event | ĐẠT | [readme](baitap3/T12_flags_dsize/readme.md) |
| `T13_multi_match` | T13 Một event match ≥2 rule | sinh đầy đủ các kết quả match | ĐẠT | [readme](baitap3/T13_multi_match/readme.md) |
| `T14_detection_event` | T14 Detection Event | đủ sid/msg/flow/5-tuple/protocol/match info | ĐẠT | [readme](baitap3/T14_detection_event/readme.md) |

Test ngoài danh sách của đề: [`baitap3/khac/integration`](baitap3/khac/integration/readme.md) — chạy `main.py --rules` thật với PCAP (cả pipeline đến Detection Event).


## Test ngoài danh sách của đề (`khac/`)

Các test này kiểm tra những mục khác của đề (CLI, log JSONL, schema, port không chuẩn, xử lý lỗi, pipeline) nên
được gom riêng, không nằm trong danh sách test case bắt buộc.

| Folder | Nội dung |
|---|---|
| [`baitap1/khac/mandatory_cases`](baitap1/khac/mandatory_cases/readme.md) | chạy cả 12 case một lần; chứa script sinh lại PCAP (`make_test_pcaps.py`) |
| [`baitap1/khac/pipeline`](baitap1/khac/pipeline/readme.md) | parser với TCP, UDP, HTTP, DNS, SMTP, unknown, malformed |
| [`baitap1/khac/capture_cli`](baitap1/khac/capture_cli/readme.md) | tham số CLI, `--count`, `--output`, lỗi |
| [`baitap1/khac/jsonl_log`](baitap1/khac/jsonl_log/readme.md) | log JSON Lines, thứ tự, PCAP bị cắt |
| [`baitap1/khac/error_handling`](baitap1/khac/error_handling/readme.md) | gói hỏng/thiếu/cắt không làm dừng chương trình |
| [`baitap1/khac/event_schema`](baitap1/khac/event_schema/readme.md) | cấu trúc event chuẩn, `validate_event()` |
| [`baitap1/khac/nonstandard_ports`](baitap1/khac/nonstandard_ports/readme.md) | nhận diện protocol trên port không chuẩn |
| [`baitap1/khac/unknown_policy`](baitap1/khac/unknown_policy/readme.md) | policy `mark` và `skip` |
| [`baitap2/khac/decoder`](baitap2/khac/decoder/readme.md), [`preprocessor`](baitap2/khac/preprocessor/readme.md), [`flow_tracker`](baitap2/khac/flow_tracker/readme.md) | chạy cả nhóm T01–T04, T05/T06/T14, T07–T13 một lần |
| [`baitap2/khac/integration`](baitap2/khac/integration/readme.md) | chạy `main.py` thật với PCAP (cả pipeline) |

## Ghi chú

- Bắt gói thật từ interface hợp lệ cần quyền root nên chưa được chạy trong test.
- `main.py` ở root là pipeline đầy đủ: PCAP/interface → Parser → Decoder → Preprocessor → Flow Tracker → JSONL; thêm `--rules` thì có Core Engine → `detections.jsonl`.
