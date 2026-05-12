"""Central configuration and path resolution for the DRIFT bot."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*args, **kwargs) -> bool:  # type: ignore[misc]
        return False

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parent.parent
DATA_DIR = REPO_ROOT / "data"
PERSIST_DIRECTORY = DATA_DIR / "chroma_db"
HISTORY_PATH = DATA_DIR / "history.jsonl"

API_KEY = os.getenv("API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
REFLECTION_INTERVAL = int(os.getenv("REFLECTION_INTERVAL", "10"))

DRIFT_PRIMARY_MODEL = os.getenv("DRIFT_PRIMARY_MODEL", "gemini-2.5-flash")
DRIFT_CRITIC_MODEL = os.getenv("DRIFT_CRITIC_MODEL", "gemini-2.5-flash")

# Security: comma-separated list of domains the bughunter tools are pre-authorized to scan
_authorized_raw = os.getenv("DRIFT_AUTHORIZED_TARGETS", "")
DEFAULT_AUTHORIZED_TARGETS = set(d.strip().lower() for d in _authorized_raw.split(",") if d.strip())

# Local LLM fallback via Ollama
DRIFT_LOCAL_MODEL = os.getenv("DRIFT_LOCAL_MODEL", "qwen3:4b")
DRIFT_USE_LOCAL_FALLBACK = os.getenv("DRIFT_USE_LOCAL_FALLBACK", "true").lower() in ("1", "true", "yes", "on")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
