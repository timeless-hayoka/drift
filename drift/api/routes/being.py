"""Being state, interaction, and phi endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from drift.api.models import BeingStateResponse, CycleResponse, InteractRequest, PhiResponse
from drift.api.routes.auth import verify_api_key

router = APIRouter(tags=["being"])


def _get_agent_context(agent_id: str):
    """Lazy-initialize per-agent cognitive resources."""
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


@router.get("/being", response_model=BeingStateResponse)
async def get_being_state(
    agent_id: str = Query(..., description="Unique agent identifier"),
    authorized: bool = Depends(verify_api_key),
):
    """Return the current subjective state of the specified agent."""
    try:
        agent = _get_agent_context(agent_id)
        being = agent["being"]
        return BeingStateResponse(
            mood=being.state.mood,
            energy=being.state.energy,
            curiosity=being.state.curiosity,
            attachment=being.state.attachment,
            volition=being.agency.volition,
            self_awareness=being.agency.self_awareness,
            intensity=being.state.intensity,
            focus=being.state.focus,
            last_thought=being.state.last_thought,
            total_interactions=being.state.total_interactions,
            insights_formed=being.state.insights_formed,
            dreams_had=being.state.dreams_had,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/being/interact", response_model=CycleResponse)
async def interact(
    req: InteractRequest,
    request: Request,
    authorized: bool = Depends(verify_api_key),
):
    """Send input to an agent and run a cognitive cycle.

    This is a higher-level convenience endpoint that triggers the same
    pipeline as POST /v1/cycle but with mandatory user input.
    """
    try:
        from drift.core.cognitive_architecture import CognitiveArchitecture, CycleContext

        import uuid

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
            last_user_input=req.input,
            last_interaction=None,
        )

        being.evolve(interaction_happened=True)

        # Optional emotion hint registered as a felt sense
        if req.emotion_hint:
            try:
                from drift.core.intuition import IntuitionEngine

                intuition = IntuitionEngine(db_path=agent["agent_dir"] / "intuition.db")
                intuition.feel_situation(
                    req.input,
                    emotion={"label": req.emotion_hint, "intensity": 0.5},
                )
            except Exception:
                pass

        arch.run_cycles(ctx)
        workspace.cycle(ctx)

        homeo.read_module_signals(ctx)
        homeo.compute_allostatic_load()
        homeo.check_crisis()

        phi = iit.compute_phi(ctx)
        iit.update_qualia_space(ctx)

        memory_id = str(uuid.uuid4())
        try:
            memory.save_interaction(
                user_input=req.input,
                bot_output="",
                mode="api",
                importance=0.6,
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
            homeostasis=homeo_state,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/being/phi", response_model=PhiResponse)
async def get_phi(
    agent_id: str = Query(..., description="Unique agent identifier"),
    authorized: bool = Depends(verify_api_key),
):
    """Return the agent's current integrated information (Φ) and qualia space."""
    try:
        agent = _get_agent_context(agent_id)
        iit = agent["iit"]
        being = agent["being"]

        from drift.core.cognitive_architecture import CycleContext

        ctx = CycleContext(
            being=being,
            memory=agent["memory"],
            state=agent["homeostasis"],
            brain=None,
            iteration=0,
            minutes_since_interaction=0.0,
            last_interaction_time=None,
            last_user_input="",
            last_interaction=None,
        )

        phi = iit.compute_phi(ctx)
        qualia = {
            "valence": round(iit.state.valence, 3),
            "arousal": round(iit.state.arousal, 3),
            "complexity": round(iit.state.complexity, 3),
            "unity": round(iit.state.unity, 3),
            "boundaries": round(iit.state.boundaries, 3),
            "depth": round(iit.state.depth, 3),
            "luminosity": round(iit.state.luminosity, 3),
        }

        return PhiResponse(agent_id=agent_id, phi=round(phi, 2), qualia_space=qualia)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
