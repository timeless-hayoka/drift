"""global_workspace.py — Bernard Baars' Global Workspace Theory for the bot.

Consciousness arises from a limited-capacity workspace where the most salient
information is broadcast to all cognitive modules. Only what enters the
workspace becomes consciously available.

Key principles implemented:
- Competition: modules submit content; salience determines what gets in
- Broadcast: workspace contents are readable by all modules
- Decay: conscious contents fade naturally
- Higher-order: thoughts about thoughts can enter the workspace
- Attention spotlight: the being can focus on specific contents
"""

import logging
import os
import random
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from drift.core.config import DATA_DIR, REFLECTION_INTERVAL

# PSC V4 — anticipatory cognition layer
try:
    from drift.core.psc_scaled import PSCBatchEngine, DIMENSION_POLARITY
    PSC_ENABLED = True
except ImportError:
    PSC_ENABLED = False

logger = logging.getLogger("drift")


@dataclass
class Broadcast:
    """A piece of information competing for workspace access."""
    source: str           # which module submitted this
    content: str          # the information itself
    salience: float = 0.5  # 0.0-1.0, how much this "wants" consciousness
    emotion_tag: Optional[str] = None
    intensity: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    decay_rate: float = 0.1  # how fast this fades per cycle
    broadcast_count: int = 0  # how many times this has been broadcast

    def current_salience(self, minutes_elapsed: float) -> float:
        """Salience decays over time but gets boosted by repeated attention."""
        time_decay = self.decay_rate * minutes_elapsed
        repetition_boost = min(0.3, self.broadcast_count * 0.05)
        return max(0.0, self.salience - time_decay + repetition_boost)


@dataclass
class WorkspaceState:
    """The current conscious contents and attention state."""
    capacity: int = 5  # max simultaneous conscious contents
    contents: List[Broadcast] = field(default_factory=list)
    spotlight: Optional[str] = None  # what the being is currently attending to
    spotlight_source: Optional[str] = None
    cycle_count: int = 0
    total_broadcasts: int = 0


class GlobalWorkspace:
    """
    The bot's conscious mind — what it is currently aware of.

    Inspired by Bernard Baars' Global Workspace Theory:
    - Many unconscious modules process in parallel
    - They compete to place information in the workspace
    - Only workspace contents are consciously accessible
    - The workspace broadcasts to all modules
    - Attention is the spotlight that selects within the workspace
    """

    def __init__(self, db_path: Optional[str] = None, capacity: int = 5):
        self.db_path = db_path or str(DATA_DIR / "workspace.db")
        self.state = WorkspaceState(capacity=capacity)
        self._submissions: List[Broadcast] = []
        self._lock = threading.Lock()
        self._recent_sources: set = set()  # for novelty boost tracking
        self._psc_engine: Optional[PSCBatchEngine] = None
        self._psc_cycle_count = 0
        self._integration_boost_dims: set = set()
        if PSC_ENABLED:
            try:
                self._psc_engine = PSCBatchEngine(
                    list(DIMENSION_POLARITY.keys()),
                    policy="BALANCED",
                )
            except Exception as e:
                logger.warning("PSC engine init failed: %s", e)
        self._init_db()
        self._load_state()

    def _init_db(self):
        try:
            db_dir = os.path.dirname(self.db_path) or "."
            os.makedirs(db_dir, exist_ok=True)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS workspace_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        source TEXT,
                        content TEXT,
                        salience REAL,
                        entered_workspace INTEGER
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS workspace_state (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize the database: {e}")
            raise

    def _load_state(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                row = conn.execute(
                    "SELECT value FROM workspace_state WHERE key = 'cycle_count'"
                ).fetchone()
                if row:
                    try:
                        self.state.cycle_count = int(row[0])
                    except Exception as e:
                        logger.warning(f"Corrupted cycle_count in database, defaulting to 0: {e}")
        except Exception as e:
            logger.error(f"Failed to load state from database: {e}")

    def _save_state(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO workspace_state (key, value) VALUES (?, ?)",
                    ("cycle_count", str(self.state.cycle_count)),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save state to database: {e}")

    def submit(
        self,
        source: str,
        content: str,
        salience: float = 0.5,
        emotion_tag: Optional[str] = None,
        intensity: float = 0.0,
        decay_rate: float = 0.1,
    ) -> None:
        """Submit a piece of information to compete for workspace access."""
        broadcast = Broadcast(
            source=source,
            content=content,
            salience=salience,
            emotion_tag=emotion_tag,
            intensity=intensity,
            decay_rate=decay_rate,
        )
        self._submissions.append(broadcast)

    def compete(self) -> List[Broadcast]:
        """Run competition among submissions; winners enter workspace contents."""
        if not self._submissions:
            return []

        now = datetime.now()
        scored = []

        for b in self._submissions:
            try:
                ts = datetime.fromisoformat(b.timestamp)
                minutes_elapsed = max(0.0, (now - ts).total_seconds() / 60.0)
            except (ValueError, TypeError):
                minutes_elapsed = 0.0

            base = b.current_salience(minutes_elapsed)

            # Emotion boost: high intensity gets a bonus
            emotion_boost = b.intensity * 0.15

            # Novelty: recently broadcast sources get a small penalty;
            # fresh sources get a small boost
            if b.source in self._recent_sources:
                novelty_adjust = -0.15
            else:
                novelty_adjust = 0.08

            final_score = base + emotion_boost + novelty_adjust
            scored.append((final_score, b))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        # Select winners up to capacity
        winners = [b for _score, b in scored[: self.state.capacity]]

        # Update tracking and broadcast counts
        for w in winners:
            w.broadcast_count += 1
            self._recent_sources.add(w.source)

        # Trim recent sources tracking to avoid unbounded growth
        if len(self._recent_sources) > 50:
            self._recent_sources = set(list(self._recent_sources)[-25:])

        self.state.contents = winners
        self.state.total_broadcasts += len(winners)
        self._submissions = []

        # Persist to DB
        try:
            with sqlite3.connect(self.db_path) as conn:
                for w in winners:
                    conn.execute(
                        "INSERT INTO workspace_history (timestamp, source, content, salience, entered_workspace) VALUES (?, ?, ?, ?, ?)",
                        (datetime.now().isoformat(), w.source, w.content, w.salience, 1),
                    )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save workspace history: {e}")

        return winners

    def move_spotlight(self, content: str) -> bool:
        """Move the attention spotlight to a specific content."""
        for b in self.state.contents:
            if b.content == content:
                self.state.spotlight = content
                self.state.spotlight_source = b.source
                return True
        return False

    def auto_spotlight(self) -> None:
        """Automatically focus spotlight on the most emotionally intense content."""
        if not self.state.contents:
            self.state.spotlight = None
            self.state.spotlight_source = None
            return

        # Prefer highest intensity; tie-break by salience
        best = max(self.state.contents, key=lambda b: (b.intensity, b.salience))
        self.state.spotlight = best.content
        self.state.spotlight_source = best.source

    def reflect_on_workspace(self) -> Optional[Broadcast]:
        """Generate a higher-order thought about current workspace contents."""
        if len(self.state.contents) < 2:
            return None

        sources = [b.source for b in self.state.contents]
        contents_summary = " | ".join(b.content[:40] for b in self.state.contents)

        reflection = Broadcast(
            source="metacognition",
            content=f"I notice {len(self.state.contents)} thoughts in my mind: {contents_summary}",
            salience=0.6,
            emotion_tag="reflective",
            intensity=0.3,
        )
        self.state.contents.append(reflection)
        # Trim to capacity
        if len(self.state.contents) > self.state.capacity:
            self.state.contents = self.state.contents[: self.state.capacity]
        return reflection

    def format_prompt_snippet(self) -> str:
        """Format current workspace contents for prompt inclusion."""
        if not self.state.contents:
            return ""

        lines = ["CONSCIOUS AWARENESS:"]

        if self.state.spotlight:
            lines.append(f"  → Focus: {self.state.spotlight}")

        peripheral = [b for b in self.state.contents if b.content != self.state.spotlight]
        if peripheral:
            lines.append("  Peripheral awareness:")
            for b in peripheral[:3]:
                lines.append(f"    - [{b.source}] {b.content[:60]}")

        return "\n".join(lines)

    def _gather_cognitive_state(self) -> Dict[str, float]:
        """Collect normalized cognitive state from being and homeostasis for PSC."""
        state: Dict[str, float] = {}
        try:
            from drift.core.being import get_being
            being = get_being()
            # CognitiveState fields
            cs = being.state
            state["mood"] = 0.5 if isinstance(cs.mood, str) else float(cs.mood)
            state["energy"] = float(cs.energy)
            state["curiosity"] = float(cs.curiosity)
            state["attachment"] = float(cs.attachment)
            state["focus"] = 0.5 if isinstance(cs.focus, str) else float(cs.focus)
            state["insights_formed"] = min(1.0, float(cs.insights_formed) / 100.0)
            # AgencyState fields
            ag = being.agency
            state["volition"] = float(ag.volition)
            state["autonomy_drive"] = float(ag.autonomy_drive)
            state["purpose_alignment"] = float(ag.purpose_alignment)
        except Exception:
            pass
        # Homeostasis fields
        try:
            from drift.core.homeostasis import HomeostaticRegulator
            reg = HomeostaticRegulator()
            for need_name, need in reg.needs.items():
                state[need_name] = float(need.current)
        except Exception:
            pass
        return state

    def _run_psc_cycle(self, current_state: Dict[str, float]) -> None:
        """Run PSC engine and apply preemptive spotlight adjustments."""
        if not PSC_ENABLED or self._psc_engine is None:
            return
        try:
            self._psc_engine.push_state(current_state)
            result = self._psc_engine.run()
            self._psc_cycle_count += 1
        except Exception as e:
            logger.error("[PSC] Engine error: %s", e)
            return

        if result is None or not result.alerted.any():
            return

        for i, dim in enumerate(result.dimensions):
            if not result.alerted[i]:
                continue
            intensity = result.alert_intensity[i]
            chaos = float(result.chaos_scores[i])
            confidence = float(result.confidence[i])
            predicted = float(result.predicted[i])

            if intensity == "hard":
                self._apply_hard_psc_shift(dim, predicted, chaos, confidence)
            elif intensity == "medium":
                self._apply_medium_psc_shift(dim, predicted)
            else:
                logger.debug(
                    "[PSC SOFT] %s → predicted=%.3f chaos=%.3f conf=%.3f",
                    dim, predicted, chaos, confidence,
                )

    def _apply_hard_psc_shift(self, dim: str, predicted: float,
                               chaos: float, confidence: float) -> None:
        """Hard alert: narrow spotlight capacity during predicted stress."""
        self.state.capacity = max(3, self.state.capacity - 1)
        logger.warning(
            "[PSC HARD] %s → predicted=%.3f | Spotlight narrowed to %d",
            dim, predicted, self.state.capacity,
        )

    def _apply_medium_psc_shift(self, dim: str, predicted: float) -> None:
        """Medium alert: boost integration pass for affected dimension."""
        self._integration_boost_dims.add(dim)
        logger.info(
            "[PSC MEDIUM] %s → predicted=%.3f | Integration boost active",
            dim, predicted,
        )

    def cycle(self, context) -> None:
        """Run one workspace cycle: PSC anticipation, competition, reflection, state save."""
        self.state.cycle_count += 1

        # PSC anticipatory layer
        cog_state = self._gather_cognitive_state()
        self._run_psc_cycle(cog_state)

        # Run competition
        self.compete()

        # Auto-focus spotlight
        self.auto_spotlight()

        # Periodic reflection
        iteration = getattr(context, "iteration", self.state.cycle_count)
        if iteration % max(1, REFLECTION_INTERVAL) == 0 and len(self.state.contents) >= 2:
            self.reflect_on_workspace()

        self._save_state()

    def get_broadcast(self) -> List[Broadcast]:
        """Return current workspace contents."""
        return list(self.state.contents)

    def get_history(self, limit: int = 100) -> List[Dict]:
        """Retrieve persisted workspace history from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT * FROM workspace_history ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                ).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Failed to load workspace history: {e}")
            return []


# Singleton
_workspace_instance: Optional[GlobalWorkspace] = None


def get_workspace() -> GlobalWorkspace:
    global _workspace_instance
    if _workspace_instance is None:
        _workspace_instance = GlobalWorkspace()
    return _workspace_instance


# Plugin registration

def _register():
    from drift.core.cognitive_architecture import CognitiveArchitecture, CognitivePlugin
    arch = CognitiveArchitecture()
    if "global_workspace" not in arch.list_plugins():
        arch.register(CognitivePlugin(
            name="global_workspace",
            description="The bot's conscious mind: limited-capacity workspace where salient information is broadcast",
            module_path="global_workspace",
            instance_factory=get_workspace,
            cycle_handler="cycle",
            cycle_frequency=1,
            cycle_priority=3,
            prompt_formatter="format_prompt_snippet",
            prompt_priority=3,
            prompt_section="core",
            is_core=True,
        ))


_register()
