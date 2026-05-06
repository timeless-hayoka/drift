"""Health check and plugin registry endpoint."""

import time

from fastapi import APIRouter, Depends, Request

from drift.api.models import HealthResponse
from drift.api.routes.auth import verify_api_key

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request, authorized: bool = Depends(verify_api_key)):
    """Return service status, the list of registered cognitive plugins, and uptime in seconds."""
    arch = getattr(request.app.state, "architecture", None)
    plugins = arch.list_plugins() if arch else []
    started_at = getattr(request.app.state, "started_at", time.time())
    uptime = time.time() - started_at
    return HealthResponse(status="ok", plugins=plugins, uptime=uptime)
