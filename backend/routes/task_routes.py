
from fastapi import APIRouter
from typing import List
from models.task_model import Task

router = APIRouter()

# Simple in-memory tasks for hackathon
_TASKS = [
    Task(id="TAPI1", title="API Debug", description="Fix and document bug in API", tags=["backend","debug"], difficulty=3),
    Task(id="TFE1", title="React Integration", description="Integrate public API into dashboard", tags=["frontend","integration"], difficulty=3),
    Task(id="TFS1", title="Dockerize Service", description="Create Dockerfile and run container", tags=["devops"], difficulty=4),
]

@router.get("/", response_model=List[Task])
def list_tasks():
    return _TASKS

@router.get("/{task_id}", response_model=Task)
def get_task(task_id: str):
    for t in _TASKS:
        if t.id == task_id:
            return t
    raise Exception("Task not found")
