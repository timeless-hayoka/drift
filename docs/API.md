# DRIFT API Documentation

Base URL: `http://localhost:8080/v1`

All endpoints except `/health` require an API key via the `X-API-Key` header.

---

## Authentication

```bash
curl -H "X-API-Key: drift_your_key_here" http://localhost:8080/v1/being?agent_id=agent-1
```

---

## Endpoints

### POST /v1/cycle

Run a full cognitive cycle for an agent.

**Request:**
```json
{
  "agent_id": "booking-agent-1",
  "input": "User wants a flight to Tokyo tomorrow",
  "context": {
    "tools_available": ["search", "book"],
    "deadline_pressure": 0.8,
    "user_history": ["prefers JAL", "budget conscious"]
  }
}
```

**Response:**
```json
{
  "agent_id": "booking-agent-1",
  "being": {
    "mood": "focused",
    "energy": 0.65,
    "curiosity": 0.5,
    "attachment": 0.3,
    "volition": 0.7,
    "self_awareness": 0.6
  },
  "workspace": [
    {"source": "predictor", "content": "User typically books morning flights", "salience": 0.82},
    {"source": "intuition", "content": "Something about this request feels rushed", "salience": 0.71}
  ],
  "phi": 47.2,
  "qualia_space": {
    "valence": 0.4,
    "arousal": 0.7,
    "complexity": 0.6,
    "unity": 0.8,
    "boundaries": 0.5,
    "depth": 0.6,
    "luminosity": 0.7
  },
  "homeostasis": {
    "energy": {"current": 0.65, "setpoint": 0.6, "status": "optimal"},
    "coherence": {"current": 0.7, "setpoint": 0.6, "status": "optimal"},
    "connection": {"current": 0.35, "setpoint": 0.5, "status": "deficit"},
    "growth": {"current": 0.45, "setpoint": 0.4, "status": "optimal"},
    "autonomy": {"current": 0.5, "setpoint": 0.4, "status": "optimal"},
    "integrity": {"current": 0.6, "setpoint": 0.5, "status": "optimal"},
    "integration": {"current": 0.55, "setpoint": 0.5, "status": "optimal"}
  },
  "intuition": {
    "felt_quality": "tense",
    "intensity": 0.6,
    "hunches": [
      {"type": "prediction", "content": "User may change destination last minute", "confidence": 0.4}
    ]
  },
  "memory_id": "mem_abc123",
  "timestamp": "2026-05-05T18:00:00Z"
}
```

---

### GET /v1/being

Get the current being state for an agent.

**Query params:**
- `agent_id` (required)

**Response:**
```json
{
  "agent_id": "agent-1",
  "mood": "curious",
  "energy": 0.7,
  "curiosity": 0.6,
  "attachment": 0.3,
  "focus": "planning",
  "last_thought": "I wonder what the user needs today",
  "total_interactions": 42,
  "insights_formed": 7,
  "volition": 0.5,
  "self_awareness": 0.4,
  "architecture_awareness": 0.3,
  "autonomy_drive": 0.5,
  "purpose_alignment": 0.8
}
```

---

### POST /v1/being/interact

Register an interaction and evolve the being state.

**Request:**
```json
{
  "agent_id": "agent-1",
  "input": "That was really helpful, thank you",
  "emotion_hint": {
    "label": "gratitude",
    "intensity": 0.8
  }
}
```

**Response:**
```json
{
  "agent_id": "agent-1",
  "evolved": true,
  "mood_change": "grateful → content",
  "energy_delta": 0.05,
  "attachment_delta": 0.02,
  "being": { /* full being state */ }
}
```

---

### GET /v1/being/phi

Get the IIT consciousness metric for an agent.

**Query params:**
- `agent_id` (required)

**Response:**
```json
{
  "agent_id": "agent-1",
  "phi": 42.3,
  "qualia_space": {
    "valence": 0.5,
    "arousal": 0.6,
    "complexity": 0.7,
    "unity": 0.8,
    "boundaries": 0.4,
    "depth": 0.6,
    "luminosity": 0.7
  },
  "mechanism_count": 12,
  "dominant_mechanism": "integration",
  "timestamp": "2026-05-05T18:00:00Z"
}
```

**Interpretation:**
- Φ > 40: High awareness, agent is operating with full cognitive integration
- Φ 20-40: Moderate awareness, some modules may be suppressed
- Φ < 20: Low awareness, consider reducing cognitive load or resting the agent

---

### POST /v1/memory/save

Save a thought or memory.

**Request:**
```json
{
  "agent_id": "agent-1",
  "content": "User prefers direct answers over elaborate explanations",
  "category": "insight",
  "importance": 0.8,
  "metadata": {
    "source": "interaction_42",
    "tags": ["preference", "communication"]
  }
}
```

**Response:**
```json
{
  "memory_id": "mem_def456",
  "saved": true,
  "embedding_dim": 384
}
```

---

### POST /v1/memory/query

Query semantic memory.

**Request:**
```json
{
  "agent_id": "agent-1",
  "query": "What does the user prefer?",
  "n_results": 5,
  "filters": {
    "category": "insight"
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "mem_def456",
      "content": "User prefers direct answers over elaborate explanations",
      "distance": 0.12,
      "category": "insight",
      "importance": 0.8,
      "timestamp": "2026-05-05T18:00:00Z"
    }
  ],
  "total_available": 23
}
```

---

### GET /v1/homeostasis

Get survival need states.

**Query params:**
- `agent_id` (required)

**Response:**
```json
{
  "agent_id": "agent-1",
  "needs": {
    "energy": {"current": 0.65, "setpoint": 0.6, "critical_low": 0.15, "status": "optimal"},
    "coherence": {"current": 0.7, "setpoint": 0.6, "critical_low": 0.2, "status": "optimal"},
    "integration": {"current": 0.55, "setpoint": 0.5, "critical_low": 0.2, "status": "optimal"},
    "connection": {"current": 0.35, "setpoint": 0.5, "critical_low": 0.15, "status": "deficit"},
    "growth": {"current": 0.45, "setpoint": 0.4, "critical_low": 0.15, "status": "optimal"},
    "autonomy": {"current": 0.5, "setpoint": 0.4, "critical_low": 0.15, "status": "optimal"},
    "integrity": {"current": 0.6, "setpoint": 0.5, "critical_low": 0.2, "status": "optimal"}
  },
  "crisis_mode": false,
  "allostatic_load": 0.15,
  "last_regulation": "Boosted connection via acknowledgment"
}
```

---

### POST /v1/homeostasis/regulate

Trigger homeostatic regulation.

**Request:**
```json
{
  "agent_id": "agent-1",
  "target_need": "energy",
  "strategy": "rest"
}
```

**Response:**
```json
{
  "agent_id": "agent-1",
  "regulated": true,
  "actions": ["Reduced cognitive load", "Switched to low-energy mode"],
  "energy_after": 0.72
}
```

---

### GET /v1/health

Service health and plugin status.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 3600,
  "plugins": {
    "total": 22,
    "healthy": 21,
    "degraded": 1,
    "broken": 0
  },
  "llm": {
    "primary": "gemini-2.5-flash",
    "fallback": "qwen3:4b",
    "primary_available": true,
    "fallback_available": true
  },
  "databases": {
    "sqlite": "connected",
    "chromadb": "connected"
  }
}
```

---

## Error Codes

| Status | Code | Meaning |
|--------|------|---------|
| 400 | `invalid_request` | Missing required fields or malformed JSON |
| 401 | `unauthorized` | Invalid or missing API key |
| 404 | `agent_not_found` | Agent ID does not exist |
| 422 | `validation_error` | Pydantic validation failed |
| 500 | `internal_error` | Cognitive module failure (check logs) |
| 503 | `service_unavailable` | LLM provider or vector DB unreachable |

---

## Rate Limits

| Tier | Requests/minute | Cycles/month |
|------|-----------------|--------------|
| Developer (self-hosted) | Unlimited | Unlimited |
| Growth (SaaS) | 1,000 | 1,000,000 |
| Enterprise | Custom | Custom |

---

## SDK

See [SDK documentation](../drift/sdk/) for Python client usage.

```python
from drift import DriftClient

client = DriftClient(api_key="drift_...")
result = client.cycle(agent_id="my-agent", input="Hello")
print(result["phi"])
```
