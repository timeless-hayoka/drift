"""Lazy per-agent resource bundle for API routes (being, memory, IIT, workspace)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from drift.core.config import PROJECT_ROOT


def get_agent_context(agent_id: str) -> Dict[str, Any]:
    """Provision on-disk state for one agent id (SQLite + Chroma under ./agents/<id>/)."""
    from drift.core.being import Being
    from drift.core.global_workspace import get_workspace
    from drift.core.homeostasis import HomeostaticRegulator
    from drift.core.iit_consciousness import IITConsciousness
    from drift.core.memory import DriftMemory

    agent_dir = PROJECT_ROOT / "agents" / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)

    return {
        "being": Being(db_path=agent_dir / "being.db"),
        "memory": DriftMemory(persist_directory=str(agent_dir / "chroma_db")),
        "homeostasis": HomeostaticRegulator(db_path=agent_dir / "homeostasis.db"),
        "iit": IITConsciousness(db_path=agent_dir / "iit.db"),
        "workspace": get_workspace(),
        "agent_dir": agent_dir,
    }
