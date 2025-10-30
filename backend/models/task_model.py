from pydantic import BaseModel
from typing import List

class Task(BaseModel):
    id: str
    title: str
    description: str
    tags: List[str] = []
    difficulty: int = 3  # 1-10 scale
