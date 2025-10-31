from typing import Any, Dict, List, Optional
from config import firebase_config
import time

# Ensure firebase initialized (safe to call repeatedly)
firebase_config.init_app()
_db = getattr(firebase_config, "db", None)


def list_test_cases_for_question(question_id: str) -> List[Dict[str, Any]]:
    """Return test cases for a question from Firestore (collection: test_cases)."""
    if not _db:
        return []
    coll = _db.collection("test_cases")
    docs = coll.where("questionId", "==", question_id).stream()
    result = []
    for d in docs:
        doc = d.to_dict()
        doc["id"] = d.id
        result.append(doc)
    return result


def save_evaluation_result(result: Dict[str, Any]) -> Optional[str]:
    if not _db:
        return None
    ref = _db.collection("evaluationResults").document()
    result["createdAt"] = time.time()
    ref.set(result)
    return ref.id


def save_metric(metric: Dict[str, Any]) -> Optional[str]:
    if not _db:
        return None
    ref = _db.collection("metrics").document()
    metric["createdAt"] = time.time()
    ref.set(metric)
    return ref.id


def save_ai_analysis(analysis: Dict[str, Any]) -> Optional[str]:
    if not _db:
        return None
    ref = _db.collection("aiAnalysis").document()
    analysis["generatedAt"] = time.time()
    ref.set(analysis)
    return ref.id


def save_gpt_prompt(prompt: Dict[str, Any]) -> Optional[str]:
    if not _db:
        return None
    ref = _db.collection("gptPrompts").document()
    prompt["createdAt"] = time.time()
    ref.set(prompt)
    return ref.id


def get_question(question_id: str) -> Optional[Dict[str, Any]]:
    if not _db:
        return None
    ref = _db.collection("questions").document(question_id).get()
    if not ref.exists:
        return None
    d = ref.to_dict()
    d["id"] = ref.id
    return d
