"""Rule Parser & Validator: chuyển một dòng rule Snort thành Internal Rule Object.

parse_rule(text) trả về {"status": "valid" | "invalid" | "unsupported", "reason": ..., "rule": ...}.
"""

import ipaddress
import re

SUPPORTED = {"msg", "sid", "rev", "content", "nocase", "offset", "depth", "distance", "within",
             "flags", "dsize", "flow", "classtype", "priority"}
FLOW_WORDS = {"to_server", "to_client", "established", "not_established"}
FLAG_LETTERS = {"S": "SYN", "A": "ACK", "F": "FIN", "R": "RST", "P": "PSH", "U": "URG"}


def result(status, reason, rule=None):
    return {"status": status, "reason": reason, "rule": rule}


def parse_port(text):
    """'any' -> 'any'; '80' -> [80, 80]; '1000:2000' -> [1000, 2000]; ':1024' / '1024:' cũng được."""
    if text == "any":
        return "any"
    if not re.fullmatch(r"\d*:?\d*", text) or text in ("", ":"):
        raise ValueError(f"bad port '{text}'")
    low, _, high = text.partition(":")
    if ":" not in text:
        high = low
    low = int(low) if low else 0
    high = int(high) if high else 65535
    if low > high or high > 65535:
        raise ValueError(f"bad port range '{text}'")
    return [low, high]


def parse_ip(text):
    if text != "any":
        ipaddress.ip_network(text, strict=False)  # lỗi -> ValueError
    return text


def split_options(text):
    """Tách các option theo ';' nhưng không tách ';' nằm trong dấu nháy."""
    options, current, in_quote = [], "", False
    for char in text:
        if char == '"':
            in_quote = not in_quote
        if char == ";" and not in_quote:
            options.append(current.strip())
            current = ""
        else:
            current += char
    if in_quote:
        raise ValueError("missing closing quote")
    if current.strip():
        raise ValueError("option is missing ';' at the end")
    return [o for o in options if o]


def parse_rule(text):
    text = text.strip()
    if "(" not in text or not text.endswith(")"):
        return result("invalid", "rule must look like: header (options)")
    header_text, _, option_text = text.partition("(")
    option_text = option_text[:-1]

    # ---- header ----
    parts = header_text.split()
    if len(parts) != 7:
        return result("invalid", "header needs 7 fields: action proto src sport dir dst dport")
    action, proto, src_ip, src_port, direction, dst_ip, dst_port = parts
    if action != "alert":
        return result("unsupported", f"action '{action}' is not supported")
    if proto not in ("tcp", "udp"):
        return result("unsupported", f"protocol '{proto}' is not supported")
    if direction not in ("->", "<>"):
        return result("invalid", f"bad direction '{direction}'")
    try:
        rule = {"action": action, "protocol": proto,
                "src_ip": parse_ip(src_ip), "src_port": parse_port(src_port),
                "direction": direction,
                "dst_ip": parse_ip(dst_ip), "dst_port": parse_port(dst_port),
                "contents": [], "flow": [], "flags": None, "dsize": None,
                "classtype": None, "priority": None, "rev": 1}
    except ValueError as error:
        return result("invalid", str(error))

    # ---- options ----
    try:
        options = split_options(option_text)
    except ValueError as error:
        return result("invalid", str(error))
    for option in options:
        key, _, value = option.partition(":")
        key, value = key.strip(), value.strip()
        if key not in SUPPORTED:
            return result("unsupported", f"keyword '{key}' is not supported")
        try:
            apply_option(rule, key, value)
        except ValueError as error:
            return result("invalid", f"{key}: {error}")

    for required in ("sid", "msg"):
        if required not in rule:
            return result("invalid", f"missing required option '{required}'")
    return result("valid", "ok", rule)


def apply_option(rule, key, value):
    """Ghi một option vào rule; ném ValueError nếu sai."""
    if key == "classtype":
        rule["classtype"] = value
    elif key in ("msg", "content"):
        if len(value) < 2 or value[0] != '"' or value[-1] != '"':
            raise ValueError("value must be in double quotes")
        value = value[1:-1]
        if key == "msg":
            rule["msg"] = value
        else:
            rule["contents"].append({"value": value, "nocase": False, "offset": None,
                                     "depth": None, "distance": None, "within": None})
    elif key in ("sid", "rev", "priority"):
        if not value.isdigit():
            raise ValueError("must be a number")
        rule[key] = int(value)
    elif key in ("offset", "depth", "distance", "within", "nocase"):
        if not rule["contents"]:
            raise ValueError("must come after a content")
        last = rule["contents"][-1]
        if key == "nocase":
            last["nocase"] = True
        else:
            if not re.fullmatch(r"-?\d+", value):
                raise ValueError("must be a number")
            last[key] = int(value)
    elif key == "flags":
        match = re.fullmatch(r"([SAFRPU]+)([+*]?)", value)
        if not match:
            raise ValueError("use letters S A F R P U and optional + or *")
        rule["flags"] = {"set": [FLAG_LETTERS[c] for c in match.group(1)], "mode": match.group(2) or "exact"}
    elif key == "dsize":
        match = re.fullmatch(r"(\d+)<>(\d+)|([<>]?)(\d+)", value)
        if not match:
            raise ValueError("use N, >N, <N or N<>M")
        if match.group(1):
            rule["dsize"] = {"op": "<>", "low": int(match.group(1)), "high": int(match.group(2))}
        else:
            rule["dsize"] = {"op": match.group(3) or "=", "low": int(match.group(4)), "high": None}
    elif key == "flow":
        words = [w.strip() for w in value.split(",")]
        for word in words:
            if word not in FLOW_WORDS:
                raise ValueError(f"unknown flow word '{word}'")
        rule["flow"] = words
