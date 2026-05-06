"""DRIFT API — Cognitive Middleware for AI Agents.

FastAPI application with lazy initialization of heavy cognitive dependencies.
Lightweight modules are loaded during lifespan startup; torch, chromadb,
and sentence-transformers are deferred to first request.
"""

import time
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from drift.api.routes import being, cycle, health, memory


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the cognitive architecture on startup.

    Only lightweight core modules and plugins are imported eagerly so the
    server starts in milliseconds regardless of heavy ML runtime state.
    Modules that pull in torch, sentence-transformers, or chromadb
    embeddings are deferred to first request.
    """
    from drift.core.cognitive_architecture import CognitiveArchitecture

    arch = CognitiveArchitecture()

    # Lightweight core modules — self-register on import
    import drift.core.being
    import drift.core.global_workspace
    import drift.core.homeostasis
    import drift.core.iit_consciousness
    import drift.core.emotional_field

    # Lightweight plugins — self-register on import
    import drift.core.plugins.preferences
    import drift.core.plugins.growth
    import drift.core.plugins.growth_trajectory
    import drift.core.plugins.relationship
    import drift.core.plugins.inner_voice
    import drift.core.plugins.self_eval
    import drift.core.plugins.goals
    import drift.core.plugins.predictor
    import drift.core.plugins.values
    import drift.core.plugins.explorer
    import drift.core.plugins.creativity
    import drift.core.plugins.temporal
    import drift.core.plugins.humanity
    import drift.core.plugins.emotion
    import drift.core.plugins.aspirations
    import drift.core.plugins.dreamer

    app.state.architecture = arch
    app.state.started_at = time.time()
    app.state.cycle_counter = 0
    yield
    # Shutdown: no explicit teardown required


app = FastAPI(
    title="DRIFT API — Cognitive Middleware for AI Agents",
    version="0.1.0",
    lifespan=lifespan,
)

legacy = APIRouter(prefix="/api")


@legacy.get("/health")
async def legacy_health():
    """Minimal health check without auth (legacy bot compatibility)."""
    return {"ok": True}


@legacy.get("/tools")
async def legacy_tools():
    from drift.core.tools import build_tool_prompt

    return {"reply": build_tool_prompt()}


@legacy.post("/chat")
async def legacy_chat(request: Request):
    try:
        await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid JSON in request body"},
        )
    return JSONResponse({"reply": ""})

# CORS enabled for demo purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(legacy)
app.include_router(health.router, prefix="/v1")
app.include_router(cycle.router, prefix="/v1")
app.include_router(being.router, prefix="/v1")
app.include_router(memory.router, prefix="/v1")


if __name__ == "__main__":
    import os

    host = os.getenv("DRIFT_API_HOST", "0.0.0.0")
    port = int(os.getenv("DRIFT_API_PORT", "8080"))
    uvicorn.run("drift.api.server:app", host=host, port=port, reload=False)
