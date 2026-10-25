"""Rule Loader: đọc file .rules, bỏ dòng trống/comment, gửi từng rule cho Parser."""

from rule_parser import parse_rule


def load_rule_files(paths, config=None):
    """Trả về danh sách kết quả, mỗi rule một phần tử:
    {"file", "line", "status": valid/invalid/unsupported/disabled, "reason", "rule"}.

    config (tùy chọn): {"disabled_files": [tên file], "disabled_sids": [sid]}
    """
    config = config or {}
    results = []
    for path in paths:
        name = str(path).split("/")[-1]
        if name in config.get("disabled_files", []):
            results.append({"file": name, "line": None, "status": "disabled", "reason": "rule file is disabled", "rule": None})
            continue
        try:
            with open(path, encoding="utf-8") as handle:
                lines = handle.readlines()
        except OSError as error:
            results.append({"file": name, "line": None, "status": "invalid", "reason": f"cannot read file: {error}", "rule": None})
            continue
        for number, line in enumerate(lines, start=1):
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            parsed = parse_rule(line)
            parsed.update(file=name, line=number)
            if parsed["status"] == "valid" and parsed["rule"]["sid"] in config.get("disabled_sids", []):
                parsed.update(status="disabled", reason="sid is disabled", rule=None)
            results.append(parsed)
    return results
