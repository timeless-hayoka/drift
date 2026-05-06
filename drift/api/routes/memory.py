"""Memory save and query endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from drift.api.models import MemoryQueryRequest, MemorySaveRequest
from drift.api.routes.auth import verify_api_key

router = APIRouter(tags=["memory"])


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


@router.post("/memory/save")
async def memory_save(
    req: MemorySaveRequest,
    authorized: bool = Depends(verify_api_key),
):
    """Save a memory fragment for the specified agent."""
    try:
        agent = _get_agent_context(req.agent_id)
        memory = agent["memory"]

        import uuid

        memory_id = str(uuid.uuid4())

        # Map category to thought_type
        memory.save_thought(
            thought_text=req.content,
            thought_type=req.category,
            source="api",
            importance=req.importance,
        )

        return {"memory_id": memory_id, "status": "saved"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/memory/query")
async def memory_query(
    req: MemoryQueryRequest,
    authorized: bool = Depends(verify_api_key),
):
    """Query an agent's semantic memory."""
    try:
        agent = _get_agent_context(req.agent_id)
        memory = agent["memory"]

        results = memory.search(req.query, n_results=req.n_results)
        serialized = []
        for doc, meta in results:
            serialized.append({"document": doc, "metadata": meta})

        return {"agent_id": req.agent_id, "results": serialized}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
