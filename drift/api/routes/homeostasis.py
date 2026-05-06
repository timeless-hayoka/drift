"""Homeostasis endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query

from drift.api.agent_context import get_agent_context
from drift.api.models import HomeostasisRegulateRequest, HomeostasisResponse
from drift.api.routes.auth import verify_api_key
from drift.core.cognitive_architecture import CycleContext

router = APIRouter(prefix="/homeostasis", tags=["homeostasis"])


def _homeostasis_snapshot(homeo) -> HomeostasisResponse:
    needs: dict[str, dict[str, object]] = {}
    for name, need in homeo.needs.items():
        status = "optimal"
        if need.current < need.critical_low:
            status = "critical"
        elif need.current < need.setpoint * 0.7:
            status = "deficit"
        needs[name] = {
            "current": round(need.current, 3),
            "setpoint": round(need.setpoint, 3),
            "critical_low": round(need.critical_low, 3),
            "status": status,
        }
    homeo.compute_allostatic_load()
    crisis = homeo.check_crisis()
    return HomeostasisResponse(
        needs=needs,
        crisis_mode=crisis,
        allostatic_load=round(homeo.allostatic_load, 3),
        last_regulation=homeo.last_regulation_action or "",
    )


@router.get("", response_model=HomeostasisResponse)
async def get_homeostasis(
    agent_id: str = Query(..., description="Unique agent identifier"),
    authorized: bool = Depends(verify_api_key),
):
    """Return survival-need levels for the agent (same DB files as /v1/cycle)."""
    try:
        agent = get_agent_context(agent_id)
        homeo = agent["homeostasis"]
        being = agent["being"]
        ctx = CycleContext(
            being=being,
            memory=agent["memory"],
            state=homeo,
            brain=None,
            iteration=0,
            minutes_since_interaction=0.0,
            last_interaction_time=None,
            last_user_input="",
            last_interaction=None,
        )
        homeo.read_module_signals(ctx)
        return _homeostasis_snapshot(homeo)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/regulate", response_model=HomeostasisResponse)
async def regulate_homeostasis(
    req: HomeostasisRegulateRequest,
    authorized: bool = Depends(verify_api_key),
):
    """Apply one homeostatic regulation step (see core `HomeostaticRegulator.regulate`)."""
    try:
        agent = get_agent_context(req.agent_id)
        homeo = agent["homeostasis"]
        being = agent["being"]
        ctx = CycleContext(
            being=being,
            memory=agent["memory"],
            state=homeo,
            brain=None,
            iteration=0,
            minutes_since_interaction=0.0,
            last_interaction_time=None,
            last_user_input="",
            last_interaction=None,
        )
        homeo.read_module_signals(ctx)
        homeo.compute_allostatic_load()
        homeo.regulate(ctx)
        return _homeostasis_snapshot(homeo)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
