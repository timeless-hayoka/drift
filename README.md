# DRIFT

Cognitive middleware for AI agents — consciousness, embodiment, homeostasis, intuition.

**[Documentation →](docs/README.md)** · **[Architecture](docs/ARCHITECTURE.md)** · **[API reference](docs/API.md)**

## Quick start

```bash
git clone https://github.com/timeless-hayoka/drift.git
cd drift
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env   # add API keys
python -m drift.api.server
```

Then open **http://127.0.0.1:8000/docs** for OpenAPI, or use the Python SDK (`drift-cognition` on PyPI when published).

## Tests

```bash
pytest
```

## License

Dual-licensed — see [LICENSE.md](LICENSE.md) (AGPL-3.0 and commercial terms).
