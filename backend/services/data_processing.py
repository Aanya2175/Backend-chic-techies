"""
data_processing.py

Prepares and sanitizes candidate session data before evaluation.

Functions:
- load_raw_session(source: Union[str, dict, list]) -> list
- clean_and_normalize_events(events: list) -> list
- preprocess_session_data(raw_data: Any) -> dict
"""

from typing import Any, Dict, List, Union
import json
import logging
from datetime import datetime

# Import evaluation engine for integration
from app.services.evaluation_engine import evaluate_candidate_session

logger = logging.getLogger("data_processing")
if not logger.handlers:
    h = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s [data_processing] %(levelname)s: %(message)s")
    h.setFormatter(fmt)
    logger.addHandler(h)
logger.setLevel(logging.INFO)

# ------------------------------------------------
# Load + Parse
# ------------------------------------------------
def load_raw_session(source: Union[str, Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Load raw events from different input formats:
    - JSON string
    - Dict with 'events'
    - Direct list of event dicts
    """
    if isinstance(source, list):
        return source
    if isinstance(source, dict):
        return source.get("events", [])
    if isinstance(source, str):
        try:
            parsed = json.loads(source)
            if isinstance(parsed, dict):
                return parsed.get("events", [])
            elif isinstance(parsed, list):
                return parsed
        except Exception as e:
            logger.error(f"JSON parse failed: {e}")
    return []


# ------------------------------------------------
# Normalization + Cleaning
# ------------------------------------------------
def normalize_event_types(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalizes event naming and structure (handles variations from different frontends).
    """
    normalized = []
    mapping = {
        "run_code": "run",
        "code_run": "run",
        "query_ai": "ai_query",
        "chatgpt_call": "ai_query",
        "paste_action": "paste",
        "text_edit": "edit",
    }

    for ev in events:
        etype = ev.get("event_type") or ev.get("type")
        etype = mapping.get(etype, etype)
        payload = ev.get("payload", {})
        timestamp = ev.get("timestamp")

        # fix timestamp
        try:
            if isinstance(timestamp, str):
                timestamp = float(datetime.fromisoformat(timestamp).timestamp())
        except Exception:
            timestamp = 0.0

        normalized.append({
            "event_type": etype,
            "payload": payload,
            "timestamp": timestamp
        })

    return normalized


def clean_and_normalize_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Removes duplicates, invalid entries, and sorts by timestamp.
    """
    seen = set()
    clean = []

    for ev in events:
        if not isinstance(ev, dict):
            continue
        etype = ev.get("event_type")
        ts = ev.get("timestamp")
        key = (etype, ts)
        if key in seen:
            continue
        seen.add(key)

        # minimal validation
        if etype not in ["run", "edit", "ai_query", "paste", "self_explanation"]:
            continue
        clean.append(ev)

    clean.sort(key=lambda e: e.get("timestamp", 0))
    return clean


# ------------------------------------------------
# Main preprocessing entry
# ------------------------------------------------
def preprocess_session_data(raw_data: Any) -> Dict[str, Any]:
    """
    Full preprocessing pipeline:
    - load raw data
    - normalize and clean events
    - produce structured candidate dict for evaluation
    """
    events = load_raw_session(raw_data)
    if not events:
        logger.warning("No events found in raw data")
        return {"events": []}

    normalized = normalize_event_types(events)
    cleaned = clean_and_normalize_events(normalized)
    return {"events": cleaned}


# ------------------------------------------------
# Combined helper for direct evaluation
# ------------------------------------------------
def evaluate_raw_session(raw_data: Any) -> Dict[str, Any]:
    """
    One-line helper that preprocesses and runs the full evaluation.
    """
    processed = preprocess_session_data(raw_data)
    if not processed.get("events"):
        return {"error": "No valid events to evaluate"}
    result = evaluate_candidate_session(processed)
    return result


# ------------------------------------------------
# Demo / Test
# ------------------------------------------------
if __name__ == "__main__":
    demo_data = [
        {"type": "run_code", "payload": {"result": "success"}, "timestamp": "2025-10-30T12:00:00"},
        {"type": "text_edit", "payload": {"keystrokes": 45}, "timestamp": "2025-10-30T12:01:00"},
        {"type": "query_ai", "payload": {"relevant": True}, "timestamp": "2025-10-30T12:02:00"},
        {"type": "self_explanation", "payload": {"text": "fixed index error"}, "timestamp": "2025-10-30T12:03:00"},
    ]

    result = evaluate_raw_session(demo_data)
    import pprint
    pprint.pprint(result)
