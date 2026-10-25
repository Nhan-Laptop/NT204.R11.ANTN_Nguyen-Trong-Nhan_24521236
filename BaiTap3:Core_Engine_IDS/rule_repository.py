"""Rule Repository/Indexer: lưu rule hợp lệ và chọn candidate rules cho một event.

Index: theo protocol (tcp/udp), rồi theo dst port nếu rule có đúng một dst port và hướng '->'.
Rule có port any/range hoặc hướng '<>' nằm trong nhóm "other" của protocol đó.
"""


def new_repository():
    return {"tcp": {"by_port": {}, "other": []}, "udp": {"by_port": {}, "other": []}, "count": 0}


def add_rule(repository, rule):
    group = repository[rule["protocol"]]
    port = rule["dst_port"]
    if rule["direction"] == "->" and port != "any" and port[0] == port[1]:
        group["by_port"].setdefault(port[0], []).append(rule)
    else:
        group["other"].append(rule)
    repository["count"] += 1


def build_repository(results):
    """Chỉ nhận kết quả có status 'valid'."""
    repository = new_repository()
    for item in results:
        if item["status"] == "valid":
            add_rule(repository, item["rule"])
    return repository


def get_candidates(repository, event):
    """Rule có thể khớp event, giữ thứ tự sid tăng dần."""
    protocol = str(event.get("transport_protocol")).lower()
    if protocol not in ("tcp", "udp"):
        return []
    group = repository[protocol]
    candidates = group["by_port"].get(event.get("dst_port"), []) + group["other"]
    return sorted(candidates, key=lambda rule: rule["sid"])
