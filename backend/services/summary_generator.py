"""
summary_generator.py

Takes evaluation output and produces readable summaries and structured insights
for display or storage.

Functions:
- generate_summary(evaluation_result: dict) -> dict
"""

from typing import Dict, Any

GRADE_THRESHOLDS = {
    "A": 85,
    "B": 70,
    "C": 55,
    "D": 40,
    "F": 0
}

def grade_from_score(score: float) -> str:
    for grade, threshold in GRADE_THRESHOLDS.items():
        if score >= threshold:
            return grade
    return "F"


def generate_summary(evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given the output of evaluation_engine.evaluate_candidate_session,
    produce a structured summary.
    """
    fuzzy = evaluation_result.get("fuzzy_result", {})
    metrics = evaluation_result.get("core_metrics", {})
    recs = evaluation_result.get("recommendations", [])

    score = fuzzy.get("score", 0.0)
    summary_text = fuzzy.get("summary", "")
    grade = grade_from_score(score)

    reasoning = metrics.get("reasoning_score", 0)
    debugging = metrics.get("debugging_efficiency", 0)
    adaptability = metrics.get("adaptability", 0)
    ethical = metrics.get("ethical_ai_usage", 0)

    # Interpret metrics into qualitative tags
    def tag(v):
        if v >= 0.75: return "strong"
        if v >= 0.5: return "moderate"
        return "weak"

    tags = {
        "reasoning": tag(reasoning),
        "debugging": tag(debugging),
        "adaptability": tag(adaptability),
        "ethical_ai": tag(ethical)
    }

    # Construct long-form narrative
    narrative_parts = [
        f"Overall performance grade: {grade} ({score:.1f}/100).",
        f"The candidate demonstrated {tags['debugging']} debugging ability and {tags['reasoning']} reasoning clarity.",
        f"Adaptability was {tags['adaptability']}, with {tags['ethical_ai']} AI usage behavior.",
    ]

    if recs:
        narrative_parts.append("Recommended improvements: " + " ".join(recs))

    long_summary = " ".join(narrative_parts)
    short_summary = f"{grade}-grade candidate: {summary_text or 'consistent performance across metrics'}."

    return {
        "grade": grade,
        "score": round(score, 1),
        "short_summary": short_summary,
        "long_summary": long_summary,
        "tags": tags,
        "recommendations": recs
    }


if __name__ == "__main__":
    # smoke test
    demo_eval = {
        "core_metrics": {
            "reasoning_score": 0.8,
            "debugging_efficiency": 0.6,
            "adaptability": 0.7,
            "ethical_ai_usage": 0.9
        },
        "fuzzy_result": {
            "score": 86.4,
            "summary": "strong debugging; ethical AI use; high adaptability; clear reasoning"
        },
        "recommendations": ["Probe advanced design skills in next round."]
    }

    out = generate_summary(demo_eval)
    import pprint
    pprint.pprint(out)
