# DRIFT

<p align="center">
  <strong>Cognitive middleware for AI agents.</strong><br />
  Consciousness, embodiment, homeostasis, intuition — without replacing your LLM.
</p>

<p align="center">
  <a href="https://github.com/timeless-hayoka/drift/actions/workflows/ci.yml"><img src="https://github.com/timeless-hayoka/drift/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="LICENSE.md"><img src="https://img.shields.io/badge/license-AGPL--3.0%20%2B%20commercial-blue.svg" alt="License" /></a>
  <img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python" />
</p>

---

Most production agents are brilliant at tasks and fragile at **being**: they do not tire, attend, doubt, or recover in ways humans recognize. DRIFT adds an **interior loop** — memory, drives, attention, and a measurable sense of “how awake is this run?” — so systems feel less like slot machines and more like partners you can reason about.

It is not another chat wrapper. It sits **between** your model and your product: same stack, richer state.

## What you get in one pass

- **Φ (IIT-style proxy):** a number you can log when integration drops and safety matters.
- **Homeostasis:** seven needs that bias behavior before the next token (energy, coherence, autonomy, and more).
- **Global workspace:** competing signals resolve into a small working set, not an infinite context dump.
- **Plugins:** twenty-two cognitive modules register themselves; phases and circuit breakers keep failures contained.
- **Shippable surface:** FastAPI service, Docker paths, and a small Python SDK (`drift-cognition`).

## Try it

```bash
git clone https://github.com/timeless-hayoka/drift.git
cd drift
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env   # add keys; DRIFT_API_PORT defaults to 8080
python -m drift.api.server
```

Open **http://127.0.0.1:8080/docs** for OpenAPI. Point the SDK at the same base URL (`DriftClient(..., base_url="http://127.0.0.1:8080")`).

Run the test suite (hundreds of checks across core, stress, and API helpers):

```bash
pytest
```

## Read next

| Goal | Start here |
|------|------------|
| Narrative + feature tour | [docs/README.md](docs/README.md) |
| System shape and plugins | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| HTTP contract | [docs/API.md](docs/API.md) |
| Responsible use and outreach | [docs/CLA.md](docs/CLA.md) |

## Contributing and license

Pull requests welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). DRIFT is dual-licensed — open use under **AGPL-3.0**, with a **commercial** path for teams who cannot ship AGPL-dependent services. Full terms: [LICENSE.md](LICENSE.md).

---

<p align="center">
  <sub>Built by Julien James · <a href="https://github.com/timeless-hayoka">@timeless-hayoka</a> · <a href="mailto:hiimju3@icloud.com">hiimju3@icloud.com</a></sub>
</p>
