"""Rule Matching Engine: so một event (+ payload) với một rule.

match_rule() trả về {"result": "MATCH" | "NO_MATCH", "sid", "reason", "stage", "matched"}.
Thứ tự kiểm tra: header -> flow -> flags -> dsize -> content (rẻ trước, đắt sau).
Matcher không in gì ra màn hình.
"""

import ipaddress


def ip_matches(rule_ip, ip):
    if rule_ip == "any":
        return True
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(rule_ip, strict=False)
    except ValueError:  # event thiếu IP hoặc IP hỏng
        return False


def port_matches(rule_port, port):
    if rule_port == "any":
        return True
    return port is not None and rule_port[0] <= port <= rule_port[1]


def header_matches(rule, event):
    if str(event.get("transport_protocol")).lower() != rule["protocol"]:
        return False
    src_ip, src_port = event.get("src_ip"), event.get("src_port")
    dst_ip, dst_port = event.get("dst_ip"), event.get("dst_port")
    forward = (ip_matches(rule["src_ip"], src_ip) and port_matches(rule["src_port"], src_port)
               and ip_matches(rule["dst_ip"], dst_ip) and port_matches(rule["dst_port"], dst_port))
    if rule["direction"] == "->":
        return forward
    reverse = (ip_matches(rule["src_ip"], dst_ip) and port_matches(rule["src_port"], dst_port)
               and ip_matches(rule["dst_ip"], src_ip) and port_matches(rule["dst_port"], src_port))
    return forward or reverse


def flow_matches(rule, event):
    """Dùng thông tin Flow Tracker đã gắn vào event: direction và flow_state."""
    for word in rule["flow"]:
        if word == "to_server" and event.get("direction") != "forward":
            return False
        if word == "to_client" and event.get("direction") != "backward":
            return False
        if word == "established" and event.get("flow_state") != "ESTABLISHED":
            return False
        if word == "not_established" and event.get("flow_state") == "ESTABLISHED":
            return False
    return True


def flags_match(rule, event):
    wanted = set(rule["flags"]["set"])
    actual = set(event.get("tcp_flags") or [])
    mode = rule["flags"]["mode"]
    if mode == "+":    # có đủ các cờ trong rule, cờ khác tùy ý
        return wanted <= actual
    if mode == "*":    # có ít nhất một cờ trong rule
        return bool(wanted & actual)
    return wanted == actual


def dsize_matches(rule, event):
    size = event.get("payload_length") or 0
    d = rule["dsize"]
    if d["op"] == ">":
        return size > d["low"]
    if d["op"] == "<":
        return size < d["low"]
    if d["op"] == "<>":
        return d["low"] <= size <= d["high"]
    return size == d["low"]


def find_content(payload, content, last_end):
    """Tìm một content trong payload. Trả về (start, end) hoặc None.

    last_end: vị trí kết thúc của content khớp trước đó (0 nếu đây là content đầu tiên).
    content: dict có value, nocase, offset, depth, distance, within.
    """
    if content["distance"] is not None or content["within"] is not None:
        start = last_end + (content["distance"] or 0)       # tương đối so với content trước
        end = start + content["within"] if content["within"] is not None else len(payload)
    else:
        start = content["offset"] or 0                       # tuyệt đối từ đầu payload
        end = start + content["depth"] if content["depth"] is not None else len(payload)
    start = max(start, 0)
    needle = content["value"].encode()
    if content["nocase"]:
        payload, needle = payload.lower(), needle.lower()
    position = payload.find(needle, start, end)
    if position == -1:
        return None
    return position, position + len(needle)


def content_matches(rule, payload):
    """Mọi content phải khớp; content sau tính tương đối từ chỗ content trước kết thúc."""
    matched, last_end = [], 0
    for content in rule["contents"]:
        found = find_content(payload, content, last_end)
        if found is None:
            return None
        matched.append({"content": content["value"], "start": found[0], "end": found[1]})
        last_end = found[1]
    return matched


def match_rule(rule, event, payload=b""):
    def no(stage, reason):
        return {"result": "NO_MATCH", "sid": rule["sid"], "stage": stage, "reason": reason, "matched": []}

    if not header_matches(rule, event):
        return no("header", "header mismatch")
    if not flow_matches(rule, event):
        return no("flow", "flow mismatch")
    if rule["flags"] is not None and not flags_match(rule, event):
        return no("flags", "tcp flags mismatch")
    if rule["dsize"] is not None and not dsize_matches(rule, event):
        return no("dsize", "dsize mismatch")
    matched = content_matches(rule, payload or b"")
    if matched is None:
        return no("content", "content not found")
    return {"result": "MATCH", "sid": rule["sid"], "stage": "content", "reason": "ok", "matched": matched}
