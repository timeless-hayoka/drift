"""
DRIFT × CrewAI Integration Demo
================================

This script shows how to wrap a CrewAI agent decision with DRIFT's
cognitive middleware.  Before the agent acts, we run a DRIFT cycle to
read the agent's *being* (mood, embodiment) and *homeostasis* (energy,
drives).  If energy is too low, the agent rests instead of proceeding.

Requirements
------------
    pip install crewai drift-sdk  (or install drift from source)

Run
---
    python drift/demos/crewai_integration.py
"""

from __future__ import annotations

import os
import sys

# If running from the repo without an installed package, add the repo root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if os.path.isdir(os.path.join(PROJECT_ROOT, "drift")):
    sys.path.insert(0, PROJECT_ROOT)

from drift.sdk import DriftClient


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DRIFT_API_KEY = os.getenv("DRIFT_API_KEY", "dev-key")
DRIFT_BASE_URL = os.getenv("DRIFT_BASE_URL", "http://localhost:8080")
AGENT_ID = "crewai-researcher-01"

# ---------------------------------------------------------------------------
# 1. Initialise DRIFT client
# ---------------------------------------------------------------------------
client = DriftClient(api_key=DRIFT_API_KEY, base_url=DRIFT_BASE_URL)

# ---------------------------------------------------------------------------
# 2. Run a cognitive cycle before the CrewAI task
# ---------------------------------------------------------------------------
# This lets DRIFT process the incoming task as sensory input and update the
# agent's internal state (global workspace, emotional field, etc.).
task_input = "Analyse the latest Q3 earnings report for quantum computing stocks."
cycle_result = client.cycle(agent_id=AGENT_ID, input=task_input)
print("[DRIFT] Cognitive cycle completed.")
print(f"[DRIFT] Cycle output keys: {list(cycle_result.keys())}")

# ---------------------------------------------------------------------------
# 3. Read being state (mood) and homeostasis (energy)
# ---------------------------------------------------------------------------
being = client.get_being(agent_id=AGENT_ID)
homeostasis = client.get_homeostasis(agent_id=AGENT_ID)

mood = being.get("mood", "neutral")
energy = homeostasis.get("energy", 1.0)

print(f"[DRIFT] Being mood : {mood}")
print(f"[DRIFT] Energy     : {energy:.2f}")

# ---------------------------------------------------------------------------
# 4. Decision gate — should the CrewAI agent proceed or rest?
# ---------------------------------------------------------------------------
ENERGY_THRESHOLD = 0.3  # Tune to your agent's resilience profile

if energy < ENERGY_THRESHOLD:
    print("[CrewAI] ⚠️  Energy too low — agent chooses to REST instead of act.")
    # In a real app you might schedule a recovery sub-task here.
    sys.exit(0)

print("[CrewAI] ✅ Energy sufficient — proceeding with task execution.")

# ---------------------------------------------------------------------------
# 5. (Mock) CrewAI task execution
# ---------------------------------------------------------------------------
# In a real integration you would instantiate your CrewAI Agent / Crew here
# and kick off task execution.  We simulate the result for the demo.
crew_result = {
    "task": task_input,
    "status": "completed",
    "summary": "Top performers: IBM Quantum (+12%), IonQ (+8%), Rigetti (-3%).",
}
print(f"[CrewAI] Task result: {crew_result['summary']}")

# ---------------------------------------------------------------------------
# 6. Feed the outcome back into DRIFT as an interaction
# ---------------------------------------------------------------------------
# This closes the loop: the agent's being evolves based on the experience
# of having completed (or failed) the task.
interaction = client.interact(
    agent_id=AGENT_ID,
    input=f"Task completed. Outcome: {crew_result['summary']}",
)
print("[DRIFT] Interaction registered — being state updated.")

# ---------------------------------------------------------------------------
# 7. Save a distilled memory for future retrieval
# ---------------------------------------------------------------------------
memory = client.save_memory(
    agent_id=AGENT_ID,
    content=crew_result["summary"],
    category="experience",
    importance=0.8,
)
print(f"[DRIFT] Memory saved (id={memory.get('memory_id', 'n/a')}).")

# ---------------------------------------------------------------------------
# 8. Consciousness check — print the Φ (phi) metric
# ---------------------------------------------------------------------------
phi = client.get_phi(agent_id=AGENT_ID)
phi_value = phi.get("phi", 0.0)
print(f"[DRIFT] Consciousness metric Φ = {phi_value:.4f}")

# ---------------------------------------------------------------------------
# 9. Optional — query related memories to show RAG in action
# ---------------------------------------------------------------------------
related = client.query_memory(
    agent_id=AGENT_ID,
    query="quantum computing stock performance",
    n_results=3,
)
print(f"[DRIFT] Related memories retrieved: {len(related.get('results', []))}")

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
client.close()
print("\n🧠 Demo complete — agent has interior life.")
