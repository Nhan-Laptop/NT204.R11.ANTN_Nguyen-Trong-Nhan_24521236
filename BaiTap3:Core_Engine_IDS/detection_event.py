"""Detection Event Generator: tạo Detection Event từ rule + event khi khớp."""


def make_detection_event(rule, event, matched):
    return {
        "timestamp": event.get("timestamp"),
        "sid": rule["sid"],
        "rev": rule["rev"],
        "msg": rule["msg"],
        "classtype": rule["classtype"],
        "priority": rule["priority"],
        "src_ip": event.get("src_ip"),
        "src_port": event.get("src_port"),
        "dst_ip": event.get("dst_ip"),
        "dst_port": event.get("dst_port"),
        "protocol": event.get("transport_protocol"),
        "application_protocol": event.get("application_protocol"),
        "flow_id": event.get("flow_id"),
        "packet_id": event.get("packet_id"),
        "matched": matched,
    }
