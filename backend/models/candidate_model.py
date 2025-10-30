from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CodeSnapshot(BaseModel):
    timestamp: int
    code: Optional[str] = None
    run_status: Optional[str] = None
    error_message: Optional[str] = None
    ai_prompt_used: Optional[str] = None

class AIInteraction(BaseModel):
    timestamp: int
    query: str
    response_snippet_used: bool = False
    category: Optional[str] = None

class BehaviorMetrics(BaseModel):
    total_runs: int = 0
    successful_runs: int = 0
    avg_error_fix_time_sec: Optional[float] = None
    ai_usage_ratio: Optional[float] = None
    idle_time_sec: int = 0
    total_keystrokes: Optional[int] = None
    copy_paste_events: int = 0
    tabs_switched: int = 0
    unique_code_versions: int = 0

class CandidateAttempt(BaseModel):
    candidate_id: str
    task_id: str
    session_start: int
    session_end: int
    code_snapshots: List[CodeSnapshot] = []
    ai_interactions: List[AIInteraction] = []
    behavior_metrics: BehaviorMetrics = BehaviorMetrics()
    self_explanation: Optional[str] = None
    system_metadata: Optional[Dict[str, Any]] = {}
