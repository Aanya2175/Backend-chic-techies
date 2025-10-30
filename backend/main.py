from fastapi import FastAPI
from routes import candidate_routes, task_routes, recruiter_routes
from config import firebase_config, llm_config
import os

app = FastAPI(title="FutureHire Backend - Hackathon MVP")

# initialize config (mock-safe)
firebase_config.init_app()
llm_config.init_app()

app.include_router(candidate_routes.router, prefix="/candidate", tags=["Candidate"])
app.include_router(task_routes.router, prefix="/tasks", tags=["Tasks"])
app.include_router(recruiter_routes.router, prefix="/recruiter", tags=["Recruiter"])

@app.get("/")
def root():
    return {"message": "FutureHire backend running. Visit /docs for API."}

