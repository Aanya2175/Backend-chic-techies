from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import candidate_routes, task_routes, recruiter_routes, api_routes
from config import firebase_config, langchain_config
import os

app = FastAPI(title="FutureHire Backend - Hackathon MVP")

# Allow frontend dev server (Vite default port 5173 or 8080 depending on setup)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize config (mock-safe)
firebase_config.init_app()
try:
    langchain_config.init_app()
except Exception:
    # langchain config may be optional in local dev
    pass

app.include_router(candidate_routes.router, prefix="/candidate", tags=["Candidate"])
app.include_router(task_routes.router, prefix="/tasks", tags=["Tasks"])
app.include_router(recruiter_routes.router, prefix="/recruiter", tags=["Recruiter"])
app.include_router(api_routes.router, prefix="/api", tags=["API"])


@app.get("/")
def root():
    return {"message": "FutureHire backend running. Visit /docs for API."}

