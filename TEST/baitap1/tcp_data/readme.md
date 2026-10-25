# TCP data (Bài 1)

Chạy (từ thư mục gốc repo): `python3 -m TEST.baitap1.tcp_data.test_tcp_data`

## Test gì

Test case **TCP data** ở mục 9 của đề. Yêu cầu của đề: *Parse TCP packet có payload*.
Test đọc `input/tcp_data.pcap`, chạy `capture.py --pcap` thật rồi in event (cũng được lưu ở `output/tcp_data.jsonl`).

## Input và output mong đợi

- **Input:** 1 packet TCP có payload `hello tcp payload` (17 byte).
- **Output mong đợi:**

| Field | Mong đợi |
|---|---|
| `transport_protocol` | `TCP` |
| `payload_length` | `17` |
| `src_port` | `40000` |
| `dst_port` | `9000` |

## Kết quả chạy

![Output khi chạy tcp_data](output/terminal_run_1.png)

Ngày chạy: 2026-10-13.

| Field | Output thật | Khớp |
|---|---|---|
| `transport_protocol` | `TCP` | ✓ |
| `payload_length` | `17` | ✓ |
| `src_port` | `40000` | ✓ |
| `dst_port` | `9000` | ✓ |

**Kết luận:** 4/4 field đúng mong đợi, exit code 0 → **ĐẠT**.
