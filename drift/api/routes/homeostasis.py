"""Homeostasis endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from drift.api.models import HomeostasisResponse
from drift.api.routes.auth import validate_api_key

router = APIRouter(prefix="/homeostasis", tags=["homeostasis"])


@router.get("", response_model=HomeostasisResponse)
async def get_homeostasis(agent_id: str, api_key: str = Depends(validate_api_key)):
    """Get survival need states for an agent."""
    try:
        from drift.core.homeostasis import HomeostaticRegulator
        homeo = HomeostaticRegulator()
        homeo.cycle({})
        needs = {}
        for name, need in homeo.NEEDS.items():
            status = "optimal"
            if need["current"] < need["critical_low"]:
                status = "critical"
            elif need["current"] < need["setpoint"] * 0.7:
                status = "deficit"
            needs[name] = {
                "current": round(need["current"], 2),
                "setpoint": need["setpoint"],
                "critical_low": need["critical_low"],
                "status": status,
            }
        return HomeostasisResponse(
            needs=needs,
            crisis_mode=homeo.check_crisis(),
            allostatic_load=round(homeo.allostatic_load, 2),
            last_regulation=homeo.last_regulation_action,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Homeostasis query failed: {exc}")
