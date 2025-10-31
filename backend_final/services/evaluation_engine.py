"""
evaluation_engine.py

Core orchestrator for evaluating a candidate session.

Functions:
- evaluate_candidate_session(candidate_data: dict) -> dict
- evaluate_session_from_sqlite(db_path: str, session_id: str) -> dict

This module:
1. extracts numerical features from raw events
2. computes normalized core metrics
3. calls ai_usage_analyzer (if available) for ethical_ai_usage
4. calls fuzzy_logic_engine (if available) for fuzzy scoring; otherwise uses internal fallback
5. returns a structured evaluation result suitable for storing or returning to frontend
"""

from typing import Dict, Any, List, Tuple, Optional
import math
import json
import logging

# Optional imports (if provided elsewhere in your codebase).
try:
    from app.services.ai_usage_analyzer import analyze_ai_usage  # type: ignore
except (ImportError, ModuleNotFoundError):
    analyze_ai_usage = None  # fallback used below

try:
    from app.services.fuzzy_logic_engine import fuzzy_evaluate  # type: ignore
except (ImportError, ModuleNotFoundError):
    fuzzy_evaluate = None  # fallback defined below

# Logging setup
logger = logging.getLogger("evaluation_engine")
if not logger.handlers:
    h = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    h.setFormatter(fmt)
    logger.addHandler(h)
logger.setLevel(logging.INFO)


# -----------------------------
# Helper feature extraction
# -----------------------------
def _safe_get(ev: Dict[str, Any], key: str, default=None):
    return ev.get(key, default) if isinstance(ev, dict) else default


def extract_core_features(events: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    From a list of event dicts, extract numeric features used by the evaluator.
    Expects events to be dictionaries with fields: 'type', 'payload' (optional dict), 'timestamp' (optional).
    Returns a feature dict with raw counts / durations.
    """
    runs = 0
    successful_runs = 0
    edits = 0
    ai_queries = 0
    relevant_ai = 0
    paste_events = 0
    keystrokes = 0
    unique_versions = set()
    self_explanations = 0
    timestamps = []

    for ev in events:
        ev_type = ev.get("event_type") or ev.get("type") or ev.get("event")  # support variations
        payload = ev.get("payload") or {}
        # payload may be JSON string
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except (json.JSONDecodeError, ValueError):
                payload = {"raw": payload}

        if "timestamp" in ev:
            try:
                timestamps.append(float(ev["timestamp"]))
            except (ValueError, TypeError):
                pass

        if ev_type == "run":
            runs += 1
            # attempt to detect success flag
            meta = payload if isinstance(payload, dict) else {}
            result = meta.get("result") or meta.get("status")
            if isinstance(result, str) and result.lower() in ("pass", "ok", "success"):
                successful_runs += 1
            elif result is True:
                successful_runs += 1
        elif ev_type == "edit" or ev_type == "code_change":
            edits += 1
            code_hash = payload.get("code_hash") if isinstance(payload, dict) else None
            if code_hash:
                unique_versions.add(code_hash)
            # keystroke count optional
            ks = payload.get("keystrokes") if isinstance(payload, dict) else None
            if isinstance(ks, (int, float)):
                keystrokes += int(ks)
        elif ev_type == "ai_query" or ev_type == "ai_interaction":
            ai_queries += 1
            meta = payload if isinstance(payload, dict) else {}
            if meta.get("relevant") or meta.get("used") or meta.get("response_snippet_used"):
                relevant_ai += 1
        elif ev_type == "paste" or ev_type == "copy_paste":
            paste_events += 1
        elif ev_type == "self_explanation" or ev_type == "explain":
            self_explanations += 1
        # other event types can be added as needed

    duration_s = 0.0
    if timestamps:
        try:
            duration_s = max(timestamps) - min(timestamps)
            if duration_s < 0:
                duration_s = 0.0
        except (ValueError, TypeError):
            duration_s = 0.0

    features = {
        "runs": runs,
        "successful_runs": successful_runs,
        "edits": edits,
        "unique_versions": len(unique_versions),
        "ai_queries": ai_queries,
        "relevant_ai": relevant_ai,
        "paste_events": paste_events,
        "keystrokes": keystrokes,
        "self_explanations": self_explanations,
        "duration_s": duration_s,
    }
    return features


# -----------------------------
# Core metric computations (normalize 0..1)
# -----------------------------
def compute_core_metrics(features: Dict[str, float]) -> Dict[str, float]:
    """
    Compute normalized core metrics from raw features.
    Returns values between 0 and 1:
      - reasoning_score
      - debugging_efficiency
      - adaptability
      - ethical_ai_usage
    These formulas are heuristic and can be tuned or replaced later.
    """

    runs = features.get("runs", 0)
    successful = features.get("successful_runs", 0)
    edits = features.get("edits", 0)
    unique_versions = features.get("unique_versions", 0)
    ai_queries = features.get("ai_queries", 0)
    relevant_ai = features.get("relevant_ai", 0)
    duration_s = max(1.0, features.get("duration_s", 0.0))  # avoid div by zero
    paste_events = features.get("paste_events", 0)
    self_explanations = features.get("self_explanations", 0)

    # Debugging efficiency: ratio of successful runs per run, scaled with diminishing returns
    debug_eff = (successful / runs) if runs > 0 else 0.0
    # scale to smooth behaviour:
    debugging_efficiency = max(0.0, min(1.0, debug_eff))

    # Adaptability: edits + unique versions normalized by session duration
    edits_per_min = (edits / (duration_s / 60.0)) if duration_s > 0 else edits
    # normalize edits_per_min roughly: 0..10 -> 0..1
    adaptability = 1.0 - math.exp(-edits_per_min / 3.0)  # quick saturating transform
    adaptability = max(0.0, min(1.0, adaptability))

    # Reasoning score: presence & length of self_explanations and moderate edit patterns
    # More self explanations indicate better reasoning; if none, degrade
    reasoning_base = min(1.0, self_explanations / 2.0)  # 0, 0.5, 1.0 for 0,1,2+ explanations
    # combine with unique_versions signal
    reasoning_score = 0.6 * reasoning_base + 0.4 * (min(1.0, unique_versions / (edits + 1)))
    reasoning_score = max(0.0, min(1.0, reasoning_score))

    # Ethical AI usage: prefer relevant_ai / ai_queries; penalize excessive AI relative to edits
    if ai_queries == 0:
        ethical_ai = 1.0  # used none: neutral/ok
    else:
        relevance_ratio = relevant_ai / ai_queries
        # penalty for AI queries >> edits (copy-paste-like)
        ai_per_edit = ai_queries / max(1.0, edits)
        penalty = min(1.0, ai_per_edit / 3.0)  # if >3 queries per edit, heavy penalty
        ethical_ai = max(0.0, min(1.0, relevance_ratio * (1.0 - 0.5 * penalty)))

    # reduce ethical score if there are many paste events
    if paste_events > 0:
        ethical_ai *= max(0.0, 1.0 - min(0.6, paste_events * 0.15))

    # clamp
    ethical_ai = max(0.0, min(1.0, ethical_ai))

    metrics = {
        "reasoning_score": round(reasoning_score, 3),
        "debugging_efficiency": round(debugging_efficiency, 3),
        "adaptability": round(adaptability, 3),
        "ethical_ai_usage": round(ethical_ai, 3),
    }
    return metrics


# -----------------------------
# Fallback fuzzy evaluator (if external fuzzy_logic_engine not present)
# -----------------------------
def _fallback_fuzzy_evaluate(metrics: Dict[str, float]) -> Tuple[float, str, Dict[str, float]]:
    """
    Small Mamdani-style fallback that maps the 4 core metrics to a final score.
    Returns (score_0_100, textual_summary, membership_details).
    """
    rs = metrics["reasoning_score"]
    de = metrics["debugging_efficiency"]
    ad = metrics["adaptability"]
    ea = metrics["ethical_ai_usage"]

    # simple rule weights (you can expand these rules)
    # compute membership-like degrees (low/med/high) per metric
    def mem_low(x): return max(0.0, min(1.0, (0.5 - x) / 0.5))
    def mem_med(x): return max(0.0, 1.0 - abs(x - 0.5) / 0.5)
    def mem_high(x): return max(0.0, min(1.0, (x - 0.5) / 0.5))

    parts = {
        "reasoning": {"low": mem_low(rs), "med": mem_med(rs), "high": mem_high(rs)},
        "debugging": {"low": mem_low(de), "med": mem_med(de), "high": mem_high(de)},
        "adaptability": {"low": mem_low(ad), "med": mem_med(ad), "high": mem_high(ad)},
        "ethical_ai": {"low": mem_low(ea), "med": mem_med(ea), "high": mem_high(ea)},
    }

    # rules -> (label_value, activation)
    # label_value is a numeric representative: poor=0.25, avg=0.55, good=0.8
    rule_list = []
    # Strong positive: high,high,high,high
    rule_list.append((0.95, min(parts["reasoning"]["high"], parts["debugging"]["high"], parts["adaptability"]["high"], parts["ethical_ai"]["high"])))
    # Good if debugging high and ethical ai not low
    rule_list.append((0.8, min(parts["debugging"]["high"], max(parts["ethical_ai"]["med"], parts["ethical_ai"]["high"]))))
    # Average base: med in most
    rule_list.append((0.55, min(parts["reasoning"]["med"], parts["debugging"]["med"], parts["adaptability"]["med"])))
    # Poor if ethical AI low or debugging low
    rule_list.append((0.25, max(parts["ethical_ai"]["low"], parts["debugging"]["low"])))
    # Adaptability rescue: if adaptability high, bump
    rule_list.append((0.75, parts["adaptability"]["high"]))

    # aggregate centroid-like
    numerator = sum(val * act for val, act in rule_list)
    denom = sum(act for _, act in rule_list) or 1e-6
    raw = numerator / denom
    final_score = round(float(raw * 100.0), 2)

    # produce a human summary
    desc = []
    if parts["debugging"]["high"] > 0.5:
        desc.append("strong debugging")
    elif parts["debugging"]["med"] > 0.5:
        desc.append("moderate debugging")
    else:
        desc.append("weak debugging")

    if parts["ethical_ai"]["high"] > 0.5:
        desc.append("ethical AI use")
    elif parts["ethical_ai"]["med"] > 0.5:
        desc.append("balanced AI use")
    else:
        desc.append("excessive AI dependence")

    if parts["adaptability"]["high"] > 0.5:
        desc.append("high adaptability")
    elif parts["adaptability"]["med"] > 0.5:
        desc.append("moderate adaptability")
    else:
        desc.append("limited adaptability")

    if parts["reasoning"]["high"] > 0.5:
        desc.append("clear reasoning")
    elif parts["reasoning"]["med"] > 0.5:
        desc.append("some reasoning evidence")

    summary = "; ".join(desc)
    membership_details = parts
    return final_score, summary, membership_details


# -----------------------------
# Top-level API
# -----------------------------
def evaluate_candidate_session(candidate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry: accepts candidate_data with key 'events' (list).
    Returns:
      {
        "features": {...},
        "core_metrics": {...},
        "fuzzy_result": {"score": float, "summary": str, "membership": {...}},
        "final_score": float,
        "recommendations": [str,...]
      }
    """
    events = candidate_data.get("events", []) if isinstance(candidate_data, dict) else []
    features = extract_core_features(events)
    core_metrics = compute_core_metrics(features)

    # AI usage analyzer (optional external)
    ai_analysis = None
    if analyze_ai_usage:
        try:
            ai_analysis = analyze_ai_usage(events)  # expected to return dict with more signals if implemented
        except (AttributeError, TypeError, ValueError) as e:
            logger.warning("analyze_ai_usage failed: %s", e)
            ai_analysis = None

    # Fuzzy scoring (prefer external if present)
    if fuzzy_evaluate:
        try:
            score, summary = fuzzy_evaluate(
                runs=int(features.get("runs", 0)),
                ai_queries=int(features.get("ai_queries", 0)),
                edits=int(features.get("edits", 0))
            )
            fuzzy_membership = None
        except (AttributeError, TypeError, ValueError) as e:
            logger.exception("external fuzzy_evaluate failed, falling back: %s", e)
            score, summary, fuzzy_membership = _fallback_fuzzy_evaluate(core_metrics)
    else:
        score, summary, fuzzy_membership = _fallback_fuzzy_evaluate(core_metrics)

    # Recommendations (simple heuristics)
    recs = []
    if core_metrics["debugging_efficiency"] < 0.4:
        recs.append("Focus on debugging fundamentals (test-driven runs).")
    if core_metrics["ethical_ai_usage"] < 0.5:
        recs.append("Encourage more selective and relevant AI prompts; avoid copy-paste.")
    if core_metrics["adaptability"] < 0.4:
        recs.append("Work on iterative problem decomposition and smaller refactors.")
    if not recs:
        recs.append("Ready for next-round interview (probe system design).")

    result = {
        "features": features,
        "core_metrics": core_metrics,
        "fuzzy_result": {
            "score": float(score),
            "summary": str(summary),
            "membership": fuzzy_membership,
            "ai_analysis": ai_analysis
        },
        "final_score": float(score),
        "recommendations": recs
    }
    return result


# -----------------------------
# DB helper for sqlite (optional convenience)
# -----------------------------
def evaluate_session_from_sqlite(db_path: str, session_id: str) -> Dict[str, Any]:
    """
    Convenience: load events from a SQLite db (schema: events table with session_id, event_type, payload)
    and evaluate.
    """
    import sqlite3
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT event_type, payload, timestamp FROM events WHERE session_id = ? ORDER BY timestamp", (session_id,))
        rows = cur.fetchall()
        events = []
        for r in rows:
            ev_type, payload, timestamp = r
            try:
                payload_obj = json.loads(payload) if isinstance(payload, str) else payload
            except (json.JSONDecodeError, ValueError):
                payload_obj = {"raw": payload}
            events.append({"event_type": ev_type, "payload": payload_obj, "timestamp": timestamp})
        return evaluate_candidate_session({"events": events})
    finally:
        if conn:
            conn.close()


# -----------------------------
# If run as script, run a small smoke demo
# -----------------------------
if __name__ == "__main__":
    demo_events = [
        {"event_type": "edit", "payload": {"keystrokes": 30}, "timestamp": 1},
        {"event_type": "run", "payload": {"result": "fail"}, "timestamp": 2},
        {"event_type": "ai_query", "payload": {"relevant": True}, "timestamp": 3},
        {"event_type": "run", "payload": {"result": "success"}, "timestamp": 60},
        {"event_type": "edit", "payload": {"keystrokes": 40}, "timestamp": 70},
        {"event_type": "self_explanation", "payload": {"text": "I fixed null pointer by checking endpoints"}, "timestamp": 80}
    ]
    out = evaluate_candidate_session({"events": demo_events})
    import pprint
    pprint.pprint(out)
