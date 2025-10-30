"""
services package

Contains all business logic modules:
- data_processing: input validation and normalization
- evaluation_engine: core metric computation
- ai_usage_analyzer: detects and scores AI interaction behavior
- fuzzy_logic_engine: optional adaptive scoring layer
- summary_generator: generates recruiter-facing summaries
"""

from .data_processing import evaluate_raw_session, preprocess_session_data
from .evaluation_engine import evaluate_candidate_session
from .ai_usage_analyzer import analyze_ai_usage
from .summary_generator import generate_summary

__all__ = [
    "evaluate_raw_session",
    "preprocess_session_data",
    "evaluate_candidate_session",
    "analyze_ai_usage",
    "generate_summary",
]
