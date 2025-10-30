
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.candidate_model import CandidateAttempt
try:
    from services import data_processing, evaluation_engine, summary_generator, firebase_service
    from services.evaluation_engine import evaluate_attempt
except ImportError:
    data_processing = None
    evaluation_engine = None
    summary_generator = None
    firebase_service = None
    evaluate_attempt = None

router = APIRouter()

@router.post("/submit", summary="Submit candidate attempt JSON")
def submit_candidate(attempt: CandidateAttempt, store_to_firebase: Optional[bool]=False):
    if not all([data_processing, evaluate_attempt, summary_generator, firebase_service]):
        raise HTTPException(status_code=503, detail="Service unavailable")
    # Basic validation done by Pydantic
    cleaned = data_processing.clean_candidate_attempt(attempt.dict())
    scores = evaluate_attempt(cleaned)
    summary = summary_generator.generate_summary(cleaned, scores)
    # persist result
    firebase_service.save_evaluation(cleaned["candidate_id"], cleaned["task_id"], scores, summary)
    return {"candidate_id": cleaned["candidate_id"], "task_id": cleaned["task_id"], "scores": scores, "summary": summary}

@router.post("/evaluate", summary="Evaluate using events path (firebase or direct payload)")
def evaluate_direct(attempt: CandidateAttempt):
    if not all([data_processing, evaluate_attempt]):
        raise HTTPException(status_code=503, detail="Service unavailable")
    cleaned = data_processing.clean_candidate_attempt(attempt.dict())
    scores = evaluate_attempt(cleaned)
    return {"candidate_id": cleaned["candidate_id"], "task_id": cleaned["task_id"], "scores": scores}
