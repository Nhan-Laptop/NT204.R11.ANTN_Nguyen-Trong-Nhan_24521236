# NT204.R11.ANTN — Nguyễn Trọng Nhân (24521236)

Repository cho hai phần bài tập IDS/IPS của môn NT204.

```text
main.py (entry point chung)
  ├── Bài 1: capture.py → parsers/
  └── Bài 2: decoder.py → preprocessor.py → flow_tracker.py → pipeline.py
```

## Cấu trúc chính

| Đường dẫn | Nội dung |
|---|---|
| `main.py` | Entry point chung cho cả hai bài |
| `BaiTap1:Packet_CAPTURER_AND_PARSER/` | Code capture và parser |
| `BaiTap2:DECODER_PREPROCESSOR_FLOW_CONNECTION_TRACKER/` | Code Decoder, Preprocessor, Flow Tracker |
| `TEST/` | Toàn bộ test chung, nằm ngoài hai thư mục bài tập |
| `TEST/README.md` | Mô tả input, output, use case, testcase và kết luận module |

`TEST/README.md` là tài liệu chính để đọc cách kiểm tra và evidence. Không có
test nào nằm bên trong thư mục implementation của hai bài.

## Chạy chương trình

Cài dependency:

```bash
python -m pip install scapy
```

Chạy parser Bài 1:

```bash
python main.py capture --pcap input.pcap --output events.jsonl
```

Chạy pipeline đầy đủ Bài 2:

```bash
python main.py process --pcap input.pcap \
  --output events.jsonl --flows-output flows.jsonl
```

## Chạy toàn bộ test

```bash
python -m unittest discover -s TEST -v
```

Kết quả và cách đối chiếu từng testcase được ghi trong
[`TEST/README.md`](TEST/README.md).

## AI assistance disclosure

AI tool used: **OpenAI ChatGPT through the pi coding agent**.

AI hỗ trợ thảo luận thiết kế, viết một phần code/test và sắp xếp tài liệu.
Sinh viên tự kiểm tra code bằng test và chịu trách nhiệm về kết quả nộp.
