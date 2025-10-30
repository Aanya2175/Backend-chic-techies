from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import candidate_routes, task_routes, recruiter_routes, code_execution_routes
from config import firebase_config, llm_config
import os

app = FastAPI(title="FutureHire Backend - Hackathon MVP")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite and React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize config (mock-safe)
firebase_config.init_app()
llm_config.init_app()

app.include_router(candidate_routes.router, prefix="/candidate", tags=["Candidate"])
app.include_router(task_routes.router, prefix="/tasks", tags=["Tasks"])
app.include_router(recruiter_routes.router, prefix="/recruiter", tags=["Recruiter"])
app.include_router(code_execution_routes.router, tags=["Code Execution"])

@app.get("/")
def root():
    return {"message": "FutureHire backend running. Visit /docs for API."}

