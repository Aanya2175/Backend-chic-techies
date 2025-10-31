"""
ai_usage_analyzer.py

Analyzes AI interaction patterns from candidate session data.

Functions:
- analyze_ai_usage(events: list) -> dict
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger("ai_usage_analyzer")
if not logger.handlers:
    h = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s [ai_usage_analyzer] %(levelname)s: %(message)s")
    h.setFormatter(fmt)
    logger.addHandler(h)
logger.setLevel(logging.INFO)


def analyze_ai_usage(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Inspect sequence of candidate events and derive ethical AI usage patterns.
    """
    if not events:
        return {"ai_queries": 0, "ethical_flag": "none", "engagement_score": 0.0}

    ai_queries = 0
    relevant_ai = 0
    paste_after_ai = 0
    edits_after_ai = 0
    copy_paste_total = 0
    time_of_last_ai = None
    last_event_type = None

    for ev in events:
        etype = ev.get("event_type")
        payload = ev.get("payload", {})
        ts = ev.get("timestamp", 0)

        if etype == "ai_query":
            ai_queries += 1
            time_of_last_ai = ts
            if payload.get("relevant") or payload.get("used") or payload.get("response_snippet_used"):
                relevant_ai += 1

        elif etype == "paste":
            copy_paste_total += 1
            # If paste comes right after AI query → likely dependency
            if last_event_type == "ai_query" or (time_of_last_ai and ts - time_of_last_ai < 20):
                paste_after_ai += 1

        elif etype == "edit":
            # edits following AI queries show engagement
            if last_event_type == "ai_query" or (time_of_last_ai and ts - time_of_last_ai < 30):
                edits_after_ai += 1

        last_event_type = etype

    # Compute ratios
    relevance_ratio = (relevant_ai / ai_queries) if ai_queries > 0 else 0
    paste_dependency = (paste_after_ai / copy_paste_total) if copy_paste_total > 0 else 0
    engagement_ratio = (edits_after_ai / ai_queries) if ai_queries > 0 else 0

    # Simple heuristic scoring (0..1)
    base_score = relevance_ratio * (1 - paste_dependency) * (0.5 + engagement_ratio)
    engagement_score = round(min(1.0, base_score), 3)

    # Interpret behavior patterns
    if ai_queries == 0:
        ethical_flag = "neutral"
        usage_pattern = "manual-only"
    elif engagement_score > 0.7:
        ethical_flag = "ethical"
        usage_pattern = "balanced"
    elif paste_dependency > 0.5 and engagement_score < 0.5:
        ethical_flag = "overuse"
        usage_pattern = "copy-heavy"
    elif relevance_ratio < 0.3:
        ethical_flag = "underuse"
        usage_pattern = "inefficient"
    else:
        ethical_flag = "mixed"
        usage_pattern = "unclear"

    return {
        "ai_queries": ai_queries,
        "relevant_ai": relevant_ai,
        "paste_after_ai": paste_after_ai,
        "copy_paste_total": copy_paste_total,
        "edits_after_ai": edits_after_ai,
        "engagement_score": engagement_score,
        "usage_pattern": usage_pattern,
        "ethical_flag": ethical_flag
    }


# ---------------------------------------------
# Demo
# ---------------------------------------------
if __name__ == "__main__":
    demo_events = [
        {"event_type": "ai_query", "payload": {"relevant": True}, "timestamp": 10},
        {"event_type": "paste", "payload": {}, "timestamp": 15},
        {"event_type": "edit", "payload": {}, "timestamp": 25},
        {"event_type": "ai_query", "payload": {"relevant": True, "used": True}, "timestamp": 40},
        {"event_type": "edit", "payload": {}, "timestamp": 45},
    ]

    import pprint
    pprint.pprint(analyze_ai_usage(demo_events))
