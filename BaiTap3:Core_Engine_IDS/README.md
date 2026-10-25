# Bài 3 — Core Engine và Snort rule matching

Engine nhận event đã chuẩn hóa (Bài 1–2, kèm `flow_id`, `direction`, `flow_state` từ Flow Tracker) và payload
của gói đó, so với các rule Snort, rồi sinh Detection Event. Engine không đọc gói thô từ Scapy.

```
event + payload → rule_evaluator → rule_repository → rule_matcher → detection_event
```

| File | Vai trò (mục của đề) |
|---|---|
| `rule_loader.py` | 4.1 Đọc file `.rules`, bỏ comment/dòng trống, gửi từng rule cho parser; tắt rule/file qua config |
| `rule_parser.py` | 4.2 Tách header/option thành Internal Rule Object; phân loại `valid` / `invalid` / `unsupported` kèm lý do |
| `rule_repository.py` | 4.3 Lưu rule hợp lệ; index theo protocol rồi dst port để chọn candidate |
| `rule_matcher.py` | 4.4 Header → flow → flags → dsize → content (offset/depth/distance/within/nocase) |
| `rule_evaluator.py` | 4.5 Lấy candidate, gọi matcher cho từng rule (không dừng ở match đầu), đếm thống kê |
| `detection_event.py` | 4.6 Tạo Detection Event |
| `rules/sample.rules` | Rule mẫu; không có signature nào viết cứng trong code |

## Phạm vi hỗ trợ

`alert`, `tcp`/`udp`, IP `any`/IPv4/CIDR, port `any`/đơn/range (`1000:2000`), hướng `->` và `<>`;
`msg`, `sid`, `rev`, `content`, `nocase`, `offset`, `depth`, `distance`, `within`, `flags` (`S A F R P U` + `+`/`*`),
`dsize` (`N`, `>N`, `<N`, `N<>M`), `flow` (`to_server`, `to_client`, `established`, `not_established`), `classtype`, `priority`.
Keyword hoặc protocol khác (ví dụ `pcre`, `byte_test`, `icmp`) được đánh dấu `unsupported`, không làm dừng chương trình.

## Chạy

```bash
python main.py --pcap input.pcap --rules "BaiTap3:Core_Engine_IDS/rules/sample.rules" \
  --detections-output detections.jsonl
```

`--rules` nhận nhiều file; `--rules-config config.json` (`{"disabled_files": [...], "disabled_sids": [...]}`)
tắt rule hoặc cả file. Dòng rule lỗi/unsupported được in ra stderr, các rule còn lại vẫn chạy.

## Giới hạn

- Content chỉ so với payload gói đơn (chưa ghép lại luồng TCP).
- Content là chuỗi văn bản; chưa hỗ trợ byte hex dạng `|41 42|`.
- Index chỉ theo protocol và dst port; IP được kiểm tra ở bước matching.
