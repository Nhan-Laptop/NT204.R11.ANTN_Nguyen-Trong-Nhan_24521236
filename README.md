# NT204.R11.ANTN — Nguyễn Trọng Nhân (24521236)

Repository cho các phần bài tập IDS/IPS của môn NT204.

## Ứng dụng chung

Chỉ có một entry point ở root: `main.py`. Đây là pipeline hoàn chỉnh, không
chia thành lệnh từng bài:

```text
PCAP/interface
  → Packet Parser (Bài 1)
  → Decoder
  → Preprocessor
  → Flow/Connection Tracker
  → events.jsonl + flows.jsonl
  → Core Engine (Bài 3, khi có --rules) → detections.jsonl
```

Các bài sau có thể nối thêm module vào pipeline này mà không cần tạo thêm
`main.py` mới.

| Đường dẫn | Nội dung |
|---|---|
| `main.py` | App/pipeline chung |
| `BaiTap1:Packet_CAPTURER_AND_PARSER/` | Parser và capture module |
| `BaiTap2:DECODER_PREPROCESSOR_FLOW_CONNECTION_TRACKER/` | Decoder, Preprocessor, Flow Tracker |
| `BaiTap3:Core_Engine_IDS/` | Core Engine: Rule Loader, Parser, Repository, Matcher, Evaluator, Detection Event |
| `TEST/` | Toàn bộ test, nằm ngoài các thư mục bài tập |
| `TEST/README.md` | Báo cáo input, output, use case và kết quả thực tế |

## Chạy app

Cài dependency:

```bash
python -m pip install scapy
```

Chạy toàn bộ pipeline với PCAP:

```bash
python main.py --pcap input.pcap \
  --output events.jsonl --flows-output flows.jsonl
```

Chạy kèm Core Engine (rule Snort):

```bash
python main.py --pcap input.pcap \
  --rules "BaiTap3:Core_Engine_IDS/rules/sample.rules" --detections-output detections.jsonl
```

Chạy với interface live:

```bash
python main.py --interface eth0 --count 20 \
  --output events.jsonl --flows-output flows.jsonl
```

## Chạy test

```bash
python3 -m TEST.baitap1.tcp_handshake.test_tcp_handshake
python3 -m TEST.baitap3.T14_detection_event.test_detection_event
```

Mỗi thư mục trong `TEST/` có một file test chạy ra output và `readme.md` đánh giá output đó.
Danh sách lệnh và kết quả: [`TEST/README.md`](TEST/README.md).


## AI assistance disclosure

AI tools used: **OpenAI ChatGPT through the pi coding agent** (Bài 1, 2) và **Claude Code** (cấu trúc lại test Bài 1, 2; viết Bài 3 và test của nó).

AI hỗ trợ thảo luận thiết kế, viết một phần code/test và sắp xếp tài liệu.
Sinh viên tự kiểm tra code bằng test và chịu trách nhiệm về kết quả nộp.
