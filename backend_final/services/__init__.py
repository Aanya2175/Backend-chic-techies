"""services package

This package exposes the individual service modules. Avoid importing
submodules at package import time to prevent circular / missing-name
ImportError issues during app startup. Import the modules directly where
required, e.g. `from services import data_processing` or
`from services import evaluation_engine`.
"""

__all__ = [
    "data_processing",
    "evaluation_engine",
    "ai_usage_analyzer",
    "fuzzy_logic_engine",
    "summary_generator",
    "firebase_service",
]
