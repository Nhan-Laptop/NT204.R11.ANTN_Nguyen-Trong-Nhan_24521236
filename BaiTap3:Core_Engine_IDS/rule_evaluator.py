"""Rule Evaluation Engine: event -> candidate rules -> matcher -> Detection Event."""

from detection_event import make_detection_event
from rule_matcher import match_rule
from rule_repository import get_candidates


def new_engine(repository):
    return {"repository": repository,
            "stats": {"events_evaluated": 0, "candidate_rules": 0, "header_dropped": 0, "matches": 0}}


def evaluate_event(engine, event, payload=b""):
    """Trả về danh sách Detection Event; một event có thể khớp nhiều rule."""
    stats = engine["stats"]
    stats["events_evaluated"] += 1
    detections = []
    for rule in get_candidates(engine["repository"], event):
        stats["candidate_rules"] += 1
        outcome = match_rule(rule, event, payload)
        if outcome["result"] == "MATCH":
            stats["matches"] += 1
            detections.append(make_detection_event(rule, event, outcome["matched"]))
        elif outcome["stage"] == "header":
            stats["header_dropped"] += 1
    return detections
