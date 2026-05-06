"""Pydantic models for the DRIFT API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CycleRequest(BaseModel):
    """Request body for running a cognitive cycle."""

    agent_id: str
    context: Dict[str, Any] = Field(default_factory=dict)
    input: Optional[str] = None


class CycleResponse(BaseModel):
    """Response from a cognitive cycle."""

    being: Dict[str, Any]
    workspace: List[Dict[str, Any]]
    phi: float
    memory_id: Optional[str] = None
    intuition: Optional[Dict[str, Any]] = None
    homeostasis: Optional[Dict[str, Any]] = None


class BeingStateResponse(BaseModel):
    """Snapshot of an agent's subjective state."""

    mood: str = "curious"
    energy: float = 0.7
    curiosity: float = 0.6
    attachment: float = 0.3
    volition: float = 0.4
    self_awareness: float = 0.3
    intensity: float = 0.5
    focus: str = ""
    last_thought: str = ""
    total_interactions: int = 0
    insights_formed: int = 0
    dreams_had: int = 0


class InteractRequest(BaseModel):
    """Request body for direct agent interaction."""

    agent_id: str
    input: str
    emotion_hint: Optional[str] = None


class MemorySaveRequest(BaseModel):
    """Request body for saving a memory fragment."""

    agent_id: str
    content: str
    category: str = "general"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class MemoryQueryRequest(BaseModel):
    """Request body for querying semantic memory."""

    agent_id: str
    query: str
    n_results: int = Field(default=5, ge=1, le=50)


class HomeostasisResponse(BaseModel):
    """Current homeostatic state of an agent."""

    needs: Dict[str, Dict[str, Any]]
    crisis_mode: bool = False
    allostatic_load: float = 0.0
    last_regulation: str = ""


class HomeostasisRegulateRequest(BaseModel):
    """Trigger one regulatory step for an agent (after needs are refreshed)."""

    agent_id: str


class HealthResponse(BaseModel):
    """Service health and plugin registry."""

    status: str
    plugins: List[str]
    uptime: float


class PhiResponse(BaseModel):
    """Integrated information (Φ) and qualia-space snapshot."""

    agent_id: str
    phi: float
    qualia_space: Dict[str, float]
