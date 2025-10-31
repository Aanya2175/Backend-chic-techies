
from fastapi import APIRouter, HTTPException
try:
    from services import firebase_service, ga_engine
except ImportError:
    firebase_service = None
    ga_engine = None

router = APIRouter()

@router.get("/report/{candidate_id}/{task_id}")
def get_report(candidate_id: str, task_id: str):
    if not firebase_service:
        raise HTTPException(status_code=503, detail="Service unavailable")
    data = firebase_service.get_evaluation(candidate_id, task_id)
    if not data:
        raise HTTPException(status_code=404, detail="Report not found")
    return data

@router.get("/recommend")
def recommend():
    # returns a simple recommended candidate shortlist using GA engine on available evaluations
    if not firebase_service or not ga_engine:
        raise HTTPException(status_code=503, detail="Service unavailable")
    evaluations = firebase_service.list_all_evaluations()
    suggested = ga_engine.suggest(evaluations)
    return {"suggested": suggested}
