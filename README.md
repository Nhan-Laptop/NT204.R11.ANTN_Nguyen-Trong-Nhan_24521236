# NT204.R11.ANTN — Nguyễn Trọng Nhân (24521236)

Repository cho các phần bài tập IDS/IPS của môn NT204.

## Ứng dụng chung

Chỉ có một entry point ở root: `main.py`. Đây là pipeline hoàn chỉnh, không
chia thành lệnh Bài 1/Bài 2:

```text
PCAP/interface
  → Packet Parser (Bài 1)
  → Decoder
  → Preprocessor
  → Flow/Connection Tracker
  → events.jsonl + flows.jsonl
```

Các bài sau có thể nối thêm module vào pipeline này mà không cần tạo thêm
`main.py` mới.

| Đường dẫn | Nội dung |
|---|---|
| `main.py` | App/pipeline chung |
| `BaiTap1:Packet_CAPTURER_AND_PARSER/` | Parser và capture module |
| `BaiTap2:DECODER_PREPROCESSOR_FLOW_CONNECTION_TRACKER/` | Decoder, Preprocessor, Flow Tracker |
| `TEST/` | Toàn bộ test, nằm ngoài hai thư mục bài tập |
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

Chạy với interface live:

```bash
python main.py --interface eth0 --count 20 \
  --output events.jsonl --flows-output flows.jsonl
```

## Chạy test

```bash
python -m unittest discover -s TEST -v
```

Kết quả thực tế và evidence được ghi trong
[`TEST/README.md`](TEST/README.md).

## AI assistance disclosure

AI tool used: **OpenAI ChatGPT through the pi coding agent**.

AI hỗ trợ thảo luận thiết kế, viết một phần code/test và sắp xếp tài liệu.
Sinh viên tự kiểm tra code bằng test và chịu trách nhiệm về kết quả nộp.
