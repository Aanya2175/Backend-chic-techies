
from fastapi import APIRouter, HTTPException
from services import firebase_service, ga_engine

router = APIRouter()

@router.get("/report/{candidate_id}/{task_id}")
def get_report(candidate_id: str, task_id: str):
    data = firebase_service.get_evaluation(candidate_id, task_id)
    if not data:
        raise HTTPException(status_code=404, detail="Report not found")
    return data

@router.get("/recommend")
def recommend():
    # returns a simple recommended candidate shortlist using GA engine on available evaluations
    evaluations = firebase_service.list_all_evaluations()
    suggested = ga_engine.suggest(evaluations)
    return {"suggested": suggested}
