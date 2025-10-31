from pydantic import BaseModel
from typing import Dict

class MetricWeights(BaseModel):
    """Weights for different evaluation metrics."""
    adaptability: float = 0.25
    debug_efficiency: float = 0.25
    ethical_ai: float = 0.25
    time_efficiency: float = 0.15
    creativity: float = 0.10

# Default weights configuration
DEFAULT_WEIGHTS = MetricWeights().dict()
