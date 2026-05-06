"""Cognitive cycle endpoint."""

import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from drift.api.models import CycleRequest, CycleResponse
from drift.api.routes.auth import verify_api_key

router = APIRouter(tags=["cycle"])


def _get_agent_context(agent_id: str) -> Dict[str, Any]:
    """Lazy-initialize per-agent cognitive resources.

    Heavy imports (memory, embeddings) are deferred to first use so the
    server starts quickly regardless of torch / sentence-transformers state.
    """
    from pathlib import Path

    from drift.core.config import PROJECT_ROOT
    from drift.core.being import Being
    from drift.core.global_workspace import get_workspace
    from drift.core.homeostasis import HomeostaticRegulator
    from drift.core.iit_consciousness import IITConsciousness

    agent_dir = PROJECT_ROOT / "agents" / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)

    being = Being(db_path=agent_dir / "being.db")
    homeo = HomeostaticRegulator(db_path=agent_dir / "homeostasis.db")
    iit = IITConsciousness(db_path=agent_dir / "iit.db")
    workspace = get_workspace()

    # Heavy import deferred to first use
    from drift.core.memory import DriftMemory

    memory = DriftMemory(persist_directory=str(agent_dir / "chroma_db"))

    return {
        "being": being,
        "memory": memory,
        "homeostasis": homeo,
        "iit": iit,
        "workspace": workspace,
        "agent_dir": agent_dir,
    }


@router.post("/cycle", response_model=CycleResponse)
async def run_cycle(
    req: CycleRequest,
    request: Request,
    authorized: bool = Depends(verify_api_key),
):
    """Run one full cognitive cycle for the specified agent.

    This evolves the agent's being, broadcasts to the global workspace,
    updates homeostasis, computes integrated information (Φ), and surfaces
    any active intuitions.
    """
    try:
        from drift.core.cognitive_architecture import CognitiveArchitecture, CycleContext

        arch = CognitiveArchitecture()
        agent = _get_agent_context(req.agent_id)

        being = agent["being"]
        memory = agent["memory"]
        homeo = agent["homeostasis"]
        iit = agent["iit"]
        workspace = agent["workspace"]

        iteration = getattr(request.app.state, "cycle_counter", 0)

        ctx = CycleContext(
            being=being,
            memory=memory,
            state=homeo,
            brain=None,
            iteration=iteration,
            minutes_since_interaction=0.0,
            last_interaction_time=None,
            last_user_input=req.input or "",
            last_interaction=None,
        )

        if req.input:
            being.evolve(interaction_happened=True)

        # Run the architecture cycle
        arch.run_cycles(ctx)
        workspace.cycle(ctx)

        # Update homeostatic signals
        homeo.read_module_signals(ctx)
        homeo.compute_allostatic_load()
        homeo.check_crisis()

        # Compute consciousness metric
        phi = iit.compute_phi(ctx)
        iit.update_qualia_space(ctx)

        # Intuition (lazy load)
        intuition_data = None
        try:
            from drift.core.intuition import IntuitionEngine

            intuition = IntuitionEngine(db_path=agent["agent_dir"] / "intuition.db")
            if req.input:
                intuition.feel_situation(req.input)
            intuition_data = {
                "felt_quality": intuition.state.felt_quality,
                "intensity": round(intuition.state.intensity, 3),
                "confidence": round(intuition.state.confidence, 3),
            }
        except Exception:
            pass

        # Save interaction to memory if input was provided
        memory_id = None
        if req.input:
            memory_id = str(uuid.uuid4())
            try:
                memory.save_interaction(
                    user_input=req.input,
                    bot_output="",
                    mode="api",
                    importance=0.5,
                )
            except Exception:
                pass

        ws_contents = [
            {
                "source": b.source,
                "content": b.content[:300],
                "salience": b.salience,
                "emotion_tag": b.emotion_tag,
                "intensity": b.intensity,
            }
            for b in workspace.get_broadcast()
        ]

        being_state = {
            "mood": being.state.mood,
            "energy": round(being.state.energy, 3),
            "curiosity": round(being.state.curiosity, 3),
            "attachment": round(being.state.attachment, 3),
            "volition": round(being.agency.volition, 3),
            "self_awareness": round(being.agency.self_awareness, 3),
            "intensity": round(being.state.intensity, 3),
            "focus": being.state.focus,
            "last_thought": being.state.last_thought,
            "total_interactions": being.state.total_interactions,
            "insights_formed": being.state.insights_formed,
            "dreams_had": being.state.dreams_had,
        }

        homeo_state = {
            name: {"current": round(need.current, 3), "setpoint": round(need.setpoint, 3)}
            for name, need in homeo.needs.items()
        }

        request.app.state.cycle_counter = iteration + 1

        return CycleResponse(
            being=being_state,
            workspace=ws_contents,
            phi=round(phi, 2),
            memory_id=memory_id,
            intuition=intuition_data,
            homeostasis=homeo_state,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
