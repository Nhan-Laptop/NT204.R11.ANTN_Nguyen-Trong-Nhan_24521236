"""Test Flow Tracker (Bài 2, T07-T13): in output của track_event() / expire_flows().

Chạy (từ thư mục gốc repo): python3 -m TEST.baitap2.khac.flow_tracker.test_flow_tracker
"""

from pprint import pprint
from TEST import baitap2  # noqa: F401  (thêm đường dẫn module Bài 2)
from flow_tracker import expire_flows, flow_snapshot, new_tracker, track_event
from TEST.baitap2.test_helpers import sample_event


def show(title, output):
    print(f"\n[{title}]")
    pprint(output, width=130, sort_dicts=False)


def track_all(tracker, events):
    """Đưa lần lượt các event vào tracker, trả về kết quả của từng event."""
    return [track_event(tracker, event) for event in events]


def only_flow(tracker):
    return flow_snapshot(next(iter(tracker["active_flows"].values())))


# T07: TCP handshake SYN -> SYN/ACK -> ACK
tracker = new_tracker()
results = track_all(tracker, [sample_event(tcp_flags=["SYN"]),
                              sample_event(reverse=True, tcp_flags=["SYN", "ACK"]),
                              sample_event(tcp_flags=["ACK"])])
show("T07 TCP handshake", {"số flow": len(tracker["active_flows"]), "flow_state": [r[0]["flow_state"] for r in results]})

# T08: A->B và B->A
tracker = new_tracker()
results = track_all(tracker, [sample_event(), sample_event(reverse=True), sample_event()])
show("T08 Bidirectional flow", {"flow_id": [r[0]["flow_id"] for r in results], "direction": [r[0]["direction"] for r in results]})

# T09: FIN và RST
tracker = new_tracker()
track_all(tracker, [sample_event(tcp_flags=["SYN"]), sample_event(reverse=True, tcp_flags=["SYN", "ACK"]),
                    sample_event(tcp_flags=["ACK"])])
fin = track_all(tracker, [sample_event(tcp_flags=["FIN", "ACK"]), sample_event(reverse=True, tcp_flags=["ACK"]),
                          sample_event(reverse=True, tcp_flags=["FIN", "ACK"]), sample_event(tcp_flags=["ACK"])])
show("T09 TCP close (FIN)", {"flow_state": [r[0]["flow_state"] for r in fin], "close_reason": fin[-1][1][0]["close_reason"],
      "active_flows": len(tracker["active_flows"])})
tracker = new_tracker()
track_event(tracker, sample_event(tcp_flags=["SYN"]))
result, done = track_event(tracker, sample_event(reverse=True, tcp_flags=["RST", "ACK"]))
show("T09 TCP reset (RST)", {"flow_state": result["flow_state"], "close_reason": done[0]["close_reason"]})

# T10: DNS qua UDP, hai chiều
tracker = new_tracker()
dns = dict(transport_protocol="UDP", application_protocol="DNS")
results = track_all(tracker, [
    sample_event(packet_length=70, src_port=40000, dst_port=53, **dns),
    sample_event(reverse=True, packet_length=120, src_port=53, dst_port=40000, timestamp=1700000001, **dns)])
flow = only_flow(tracker)
show("T10 UDP query/response", {k: flow[k] for k in ("protocol", "application_protocol", "packet_count", "byte_count", "state")})

# T11: nhiều flow cùng lúc
tracker = new_tracker()
track_all(tracker, [sample_event(), sample_event(src_port=40001), sample_event(dst_ip="10.0.0.3"),
                    sample_event(transport_protocol="UDP")])
show("T11 Concurrent flows", {"số flow": len(tracker["active_flows"])})

# T12: idle timeout (TCP 10 giây, UDP 5 giây)
tracker = new_tracker(tcp_timeout=10, udp_timeout=5)
track_all(tracker, [sample_event(), sample_event(transport_protocol="UDP")])
show("T12 Idle timeout (+4 giây)", {"hết hạn": len(expire_flows(tracker, 1700000004))})
show("T12 Idle timeout (+5 giây)", [(f["protocol"], f["state"], f["close_reason"]) for f in expire_flows(tracker, 1700000005)])
show("T12 Idle timeout (+10 giây)", {"hết hạn": [f["protocol"] for f in expire_flows(tracker, 1700000010)],
      "active_flows": len(tracker["active_flows"])})

# T13: thống kê
tracker = new_tracker()
track_all(tracker, [sample_event(tcp_flags=["SYN"], packet_length=60),
                    sample_event(reverse=True, tcp_flags=["SYN", "ACK"], packet_length=64, timestamp=1700000000.5),
                    sample_event(tcp_flags=["ACK"], packet_length=52, timestamp=1700000001),
                    sample_event(tcp_flags=["PSH", "ACK"], packet_length=100, timestamp=1700000002.5),
                    sample_event(reverse=True, tcp_flags=["ACK"], packet_length=52, timestamp=1700000003)])
flow = only_flow(tracker)
show("T13 Statistics",
     {"packet_count": flow["packet_count"], "byte_count": flow["byte_count"],
      "forward/backward": (flow["forward_packet_count"], flow["backward_packet_count"]),
      "SYN": flow["SYN_count"], "ACK": flow["ACK_count"], "FIN": flow["FIN_count"], "RST": flow["RST_count"],
      "duration": flow["duration"], "state": flow["state"],
      "endpoint_a": flow["endpoint_a"], "endpoint_b": flow["endpoint_b"]})
