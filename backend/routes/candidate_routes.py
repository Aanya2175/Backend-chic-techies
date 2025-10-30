
from fastapi import APIRouter, HTTPException
from typing import Optional
from models.candidate_model import CandidateAttempt
from services import data_processing, evaluation_engine, summary_generator, firebase_service
from services.evaluation_engine import evaluate_attempt

router = APIRouter()

@router.post("/submit", summary="Submit candidate attempt JSON")
def submit_candidate(attempt: CandidateAttempt, store_to_firebase: Optional[bool]=False):
    # Basic validation done by Pydantic
    cleaned = data_processing.clean_candidate_attempt(attempt.dict())
    scores = evaluate_attempt(cleaned)
    summary = summary_generator.generate_summary(cleaned, scores)
    # persist result
    firebase_service.save_evaluation(cleaned["candidate_id"], cleaned["task_id"], scores, summary)
    return {"candidate_id": cleaned["candidate_id"], "task_id": cleaned["task_id"], "scores": scores, "summary": summary}

@router.post("/evaluate", summary="Evaluate using events path (firebase or direct payload)")
def evaluate_direct(attempt: CandidateAttempt):
    cleaned = data_processing.clean_candidate_attempt(attempt.dict())
    scores = evaluate_attempt(cleaned)
    return {"candidate_id": cleaned["candidate_id"], "task_id": cleaned["task_id"], "scores": scores}
