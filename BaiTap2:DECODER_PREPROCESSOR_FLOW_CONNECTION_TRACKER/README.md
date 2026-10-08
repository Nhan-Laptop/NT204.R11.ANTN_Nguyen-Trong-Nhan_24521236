# Bài tập 2 — Decoder, Preprocessor & Flow Tracker

## Mục tiêu

Bài 2 nhận event từ parser Bài 1 và xử lý tiếp:

```text
parser Bài 1 → Decoder → Preprocessor → Flow/Connection Tracker
```

Entry point chung là `main.py` ở root repository. Code riêng của Bài 2 nằm ở
thư mục này:

| File | Nhiệm vụ |
|---|---|
| `decoder.py` | Decode URI/form, HTML entity và MIME |
| `preprocessor.py` | Kiểm tra và chuẩn hóa event |
| `flow_tracker.py` | Gom packet thành flow TCP/UDP, state, timeout, statistics |
| `pipeline.py` | Nối parser Bài 1 với ba module trên |

## Cách chạy

Chạy từ root repository:

```bash
python main.py process --pcap TEST/baitap2/integration/input/pcap/http_request.pcap \
  --output events.jsonl --flows-output flows.jsonl
```

Các option của pipeline:

| Option | Ý nghĩa |
|---|---|
| `--pcap` | PCAP input |
| `--output` | JSONL event output |
| `--flows-output` | JSONL flow output |
| `--tcp-timeout`, `--udp-timeout` | Idle timeout |
| `--max-decode-size` | Giới hạn dữ liệu decode |
| `--invalid-policy mark\|skip` | Giữ hoặc bỏ event invalid |

## Chức năng chính

### Decoder

- Giải mã percent-encoding của URI.
- Giải mã form với quy tắc `+` thành space chỉ trong form.
- Giải mã HTML entity trong text phù hợp.
- Giải mã MIME Base64/Quoted-Printable khi header chỉ định.
- Giữ field gốc và ghi kết quả vào field `decoded_*`.
- Byte lỗi tạo trạng thái `PARTIAL`/reason thay vì làm crash chương trình.

### Preprocessor

- Kiểm tra IP, port, timestamp, transport/app protocol và field bắt buộc.
- Chuẩn hóa protocol, domain, header và timestamp.
- Dùng `null`, `[]`, `{}` nhất quán cho dữ liệu thiếu.
- Gắn `preprocess_status`, `processing_action`, `trackable` và `reason`.

### Flow Tracker

- Dùng bidirectional 5-tuple để gộp flow.
- Phân biệt `forward` và `backward`.
- Theo dõi TCP handshake, FIN, RST; UDP được gom không cần handshake.
- Lưu packet/byte count, TCP flags, duration và state.
- Expire flow bằng timestamp của packet, sau đó ghi flow ra JSONL.

Không thực hiện TLS decryption hoặc full TCP stream reassembly.

## Test và evidence

Tất cả test nằm ngoài các module, tại `TEST/baitap2/`:

| Thư mục | Test |
|---|---|
| `decoder/` | T01–T04 |
| `preprocessor/` | T05, T06, T14 |
| `flow_tracker/` | T07–T13 |
| `integration/` | Chạy root `main.py` thật qua subprocess |

Mỗi thư mục có `input/`, file `test_*.py` và `output/`. PCAP integration nằm
trong `TEST/baitap2/integration/input/pcap/`. README chung giải thích chi tiết
input, output, use case, expected result và module đã đạt hay chưa:
`TEST/README.md`.

Chạy toàn bộ test:

```bash
python -m unittest discover -s TEST -v
```

Chạy riêng từng phần của Bài 2:

```bash
python -m unittest discover -s TEST/baitap2/decoder -v
python -m unittest discover -s TEST/baitap2/preprocessor -v
python -m unittest discover -s TEST/baitap2/flow_tracker -v
python -m unittest discover -s TEST/baitap2/integration -v
```
