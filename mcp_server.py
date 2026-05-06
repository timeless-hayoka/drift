"""Small FastAPI surface for MCP-style HTTP demos and tests."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict


class InvokeBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    args: list[Any] = []


class AutonomyBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    plan: list[dict[str, Any]]


def create_http_app(token: str | None = None) -> FastAPI:
    app = FastAPI(title="DRIFT MCP HTTP")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/invoke/emotional_clarity")
    def emotional_clarity(invoke: InvokeBody) -> dict[str, str]:
        from drift.core.plugins.emotion import detect_emotion

        text = str(invoke.args[0]) if invoke.args else ""
        em = detect_emotion(text)
        result = (
            f"Emotional reading: label={em.get('label', 'unknown')} "
            f"intensity={float(em.get('intensity', 0.0)):.2f}"
        )
        return {"result": result}

    @app.post("/invoke/dissonance_map")
    def dissonance_map(invoke: InvokeBody) -> dict[str, str]:
        from cognition import map_dissonance

        text = str(invoke.args[0]) if invoke.args else ""
        return {"result": map_dissonance(text)}

    @app.post("/autonomy")
    def autonomy(
        autonomy_plan: AutonomyBody,
        authorization: str | None = Header(None),
    ) -> dict[str, Any]:
        if token is not None:
            if authorization != f"Bearer {token}":
                raise HTTPException(status_code=401, detail="Unauthorized")

        from drift.core.plugins.emotion import detect_emotion
        from cognition import map_dissonance

        results: list[dict[str, Any]] = []
        for step in autonomy_plan.plan:
            name = step.get("tool")
            args = step.get("args") or []
            if name == "emotional_clarity":
                text = str(args[0]) if args else ""
                em = detect_emotion(text)
                out = (
                    f"Emotional reading: label={em.get('label')} "
                    f"intensity={float(em.get('intensity', 0.0)):.2f}"
                )
            elif name == "dissonance_map":
                text = str(args[0]) if args else ""
                out = map_dissonance(text)
            else:
                out = f"Unknown tool {name}"
            results.append({"tool": name, "result": out})

        return {"results": results}

    return app
