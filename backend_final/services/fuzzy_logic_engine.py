"""
fuzzy_logic_engine.py

Implements a fuzzy inference system for candidate evaluation.
Takes normalized metrics (0–1) and produces a final score (0–100) with human-readable summary.
"""

from typing import Dict, Tuple
import math


# -----------------------------
# Membership functions
# -----------------------------
def low(x: float) -> float:
    """Triangular fuzzy set for 'Low'."""
    if x <= 0: return 1.0
    if 0 < x < 0.4: return (0.4 - x) / 0.4
    return 0.0

def medium(x: float) -> float:
    """Triangular fuzzy set for 'Medium'."""
    if 0.2 < x < 0.5: return (x - 0.2) / 0.3
    if 0.5 <= x < 0.8: return (0.8 - x) / 0.3
    return 0.0

def high(x: float) -> float:
    """Triangular fuzzy set for 'High'."""
    if x <= 0.5: return 0.0
    if 0.5 < x < 0.8: return (x - 0.5) / 0.3
    if x >= 0.8: return 1.0
    return 0.0


# -----------------------------
# Fuzzy rule base
# -----------------------------
def fuzzy_rules(metrics: Dict[str, float]) -> Tuple[float, str]:
    """
    Apply fuzzy logic rules to compute candidate final score.
    Inputs: metrics dict with normalized values (0–1)
    Output: (final_score_0_100, summary_text)
    """

    rs = metrics.get("reasoning_score", 0)
    de = metrics.get("debugging_efficiency", 0)
    ad = metrics.get("adaptability", 0)
    ea = metrics.get("ethical_ai_usage", 0)

    # Membership degrees
    μ = {
        "reasoning": {"low": low(rs), "med": medium(rs), "high": high(rs)},
        "debugging": {"low": low(de), "med": medium(de), "high": high(de)},
        "adapt": {"low": low(ad), "med": medium(ad), "high": high(ad)},
        "ethical": {"low": low(ea), "med": medium(ea), "high": high(ea)},
    }

    # Define fuzzy rules as (activation_strength, output_value)
    # Output_value: poor=0.3, average=0.55, good=0.8, excellent=0.95
    rules = []

    # Rule 1: all high -> excellent
    act = min(μ["reasoning"]["high"], μ["debugging"]["high"], μ["adapt"]["high"], μ["ethical"]["high"])
    rules.append((act, 0.95))

    # Rule 2: debugging & ethical high -> good
    act = min(μ["debugging"]["high"], μ["ethical"]["high"])
    rules.append((act, 0.8))

    # Rule 3: reasoning medium & debugging medium & ethical medium -> average
    act = min(μ["reasoning"]["med"], μ["debugging"]["med"], μ["ethical"]["med"])
    rules.append((act, 0.55))

    # Rule 4: ethical low OR debugging low -> poor
    act = max(μ["ethical"]["low"], μ["debugging"]["low"])
    rules.append((act, 0.3))

    # Rule 5: adaptability high & reasoning med/high -> good
    act = min(max(μ["reasoning"]["med"], μ["reasoning"]["high"]), μ["adapt"]["high"])
    rules.append((act, 0.75))

    # Defuzzification (centroid-like)
    try:
        numerator = sum(act * val for act, val in rules)
        denominator = sum(act for act, _ in rules) or 1e-6
        score = round((numerator / denominator) * 100, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        score = 50.0  # fallback score

    # Generate summary
    summary_parts = []
    if μ["debugging"]["high"] > 0.5: summary_parts.append("strong debugging")
    elif μ["debugging"]["med"] > 0.5: summary_parts.append("moderate debugging")
    else: summary_parts.append("weak debugging")

    if μ["ethical"]["high"] > 0.5: summary_parts.append("ethical AI use")
    elif μ["ethical"]["med"] > 0.5: summary_parts.append("balanced AI use")
    else: summary_parts.append("questionable AI dependence")

    if μ["adapt"]["high"] > 0.5: summary_parts.append("high adaptability")
    elif μ["adapt"]["med"] > 0.5: summary_parts.append("moderate adaptability")

    if μ["reasoning"]["high"] > 0.5: summary_parts.append("strong reasoning")
    elif μ["reasoning"]["med"] > 0.5: summary_parts.append("partial reasoning")

    summary = "; ".join(summary_parts)

    return score, summary


# -----------------------------
# Public interface
# -----------------------------
def fuzzy_evaluate(**kwargs) -> Tuple[float, str]:
    """
    External callable used by evaluation_engine.py.
    Input can be:
      - runs, ai_queries, edits (raw counts)
      - OR normalized metrics dict
    """
    # If metrics already normalized (0–1), just use them
    if all(0.0 <= v <= 1.0 for v in kwargs.values()):
        return fuzzy_rules(kwargs)

    # otherwise, normalize from raw-ish numbers
    runs = kwargs.get("runs", 0)
    ai_queries = kwargs.get("ai_queries", 0)
    edits = kwargs.get("edits", 0)

    metrics = {
        "reasoning_score": min(1.0, edits / 10.0),
        "debugging_efficiency": min(1.0, runs / 10.0),
        "adaptability": min(1.0, edits / 15.0),
        "ethical_ai_usage": max(0.0, 1.0 - (ai_queries / (edits + 1.0)))
    }

    return fuzzy_rules(metrics)


# -----------------------------
# Debug run
# -----------------------------
if __name__ == "__main__":
    demo = {
        "reasoning_score": 0.7,
        "debugging_efficiency": 0.8,
        "adaptability": 0.6,
        "ethical_ai_usage": 0.9
    }
    score, summary = fuzzy_rules(demo)
    print("Score:", score, "Summary:", summary)
