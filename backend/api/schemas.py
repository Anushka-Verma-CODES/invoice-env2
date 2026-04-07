from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ActionPayload(BaseModel):
    extracted_fields: Dict[str, str] = Field(default_factory=dict)
    category: Optional[str] = None
    anomaly_flag: Optional[bool] = None


class ResetRequest(BaseModel):
    batch_size: int = 12


class RunAgentRequest(BaseModel):
    batch_size: int = 12
    mode: str = "auto"


class StepRequest(BaseModel):
    action: ActionPayload


class StepResponse(BaseModel):
    observation: Dict[str, Any]
    reward: Dict[str, Any]
    done: bool
    info: Dict[str, Any]


class ResetResponse(BaseModel):
    observation: Dict[str, Any]
    state: Dict[str, Any]


class RunAgentResponse(BaseModel):
    run_id: str
    final_score: float
    steps: int
    results: List[Dict[str, Any]]
    timestamp: str


class ResultsResponse(BaseModel):
    latest_run: Optional[Dict[str, Any]] = None
    runs: List[Dict[str, Any]] = Field(default_factory=list)
