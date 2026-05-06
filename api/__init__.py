"""Legacy import alias: ``from api import app`` maps to the DRIFT FastAPI app."""

from drift.api.server import app

__all__ = ["app"]
