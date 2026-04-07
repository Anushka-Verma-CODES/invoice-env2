from fastapi import APIRouter, HTTPException

from backend.api.schemas import ResetRequest, ResultsResponse, RunAgentRequest, StepRequest
from backend.api import services


router = APIRouter(prefix="/api", tags=["invoice-platform"])


@router.post("/reset")
def reset(request: ResetRequest):
    try:
        return services.reset_environment(batch_size=request.batch_size)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/step")
def step(request: StepRequest):
    try:
        return services.step_environment(action_payload=request.action.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/state")
def state():
    try:
        return services.get_state()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/run-agent")
def run_agent(request: RunAgentRequest):
    try:
        return services.run_agent_full(batch_size=request.batch_size, mode=request.mode)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/results", response_model=ResultsResponse)
def results(limit: int = 20):
    try:
        return services.get_results(limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
