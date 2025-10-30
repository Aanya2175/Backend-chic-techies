from pydantic import BaseModel
from typing import Dict

class MetricWeights(BaseModel):
    adaptability: float = 0.25
    debug_efficiency: float = 0.25
    ethical_ai: float = 0.25
    time_efficiency: float = 0.15
    creativity: float = 0.10

DEFAULT_WEIGHTS = MetricWeights().dict()
