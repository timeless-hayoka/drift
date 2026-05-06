"""DRIFT SDK client — thin HTTP wrapper over the DRIFT API."""

from __future__ import annotations

import httpx


class DriftAPIError(Exception):
    """Raised when the DRIFT API returns a non-2xx status code."""

    def __init__(self, message: str, status_code: int = None, response_body: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class DriftClient:
    """Python client for the DRIFT cognitive middleware API.

    Parameters
    ----------
    api_key:
        Authentication key for the DRIFT service.
    base_url:
        Root URL of the DRIFT API (default: ``http://localhost:8080``).
    """

    def __init__(self, api_key: str, base_url: str = "http://localhost:8080"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=httpx.Timeout(30.0),
        )

    def _request(
        self,
        method: str,
        path: str,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        """Execute an HTTP request and return the JSON response."""
        response = self._client.request(method, path, json=json, params=params)

        if not response.is_success:
            body = None
            try:
                body = response.json()
            except Exception:
                pass
            raise DriftAPIError(
                message=f"DRIFT API error: {response.status_code} {response.reason_phrase}",
                status_code=response.status_code,
                response_body=body,
            )

        # Some endpoints (e.g. health) may return empty bodies on 204.
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    def cycle(self, agent_id: str, input: str, context: dict | None = None) -> dict:
        """Run a full cognitive cycle for an agent.

        Parameters
        ----------
        agent_id:
            Unique identifier of the target agent.
        input:
            Sensory / textual input to feed into the cycle.
        context:
            Optional additional context key-value pairs.

        Returns
        -------
        dict
            The cognitive cycle result (output, state delta, etc.).
        """
        payload = {"agent_id": agent_id, "input": input}
        if context:
            payload["context"] = context
        return self._request("POST", f"/agents/{agent_id}/cycle", json=payload)

    def get_being(self, agent_id: str) -> dict:
        """Retrieve the being (phenomenological) state for an agent.

        Returns
        -------
        dict
            Current mood, emotional field, embodiment, etc.
        """
        return self._request("GET", f"/agents/{agent_id}/being")

    def interact(
        self,
        agent_id: str,
        input: str,
        emotion_hint: dict | None = None,
    ) -> dict:
        """Register an interaction and evolve the agent's being state.

        Parameters
        ----------
        agent_id:
            Target agent identifier.
        input:
            Interaction payload (message, observation, etc.).
        emotion_hint:
            Optional emotion overrides or hints.

        Returns
        -------
        dict
            Updated being state and any generated response.
        """
        payload = {"agent_id": agent_id, "input": input}
        if emotion_hint:
            payload["emotion_hint"] = emotion_hint
        return self._request("POST", f"/agents/{agent_id}/interact", json=payload)

    def get_phi(self, agent_id: str) -> dict:
        """Retrieve the IIT consciousness metric (Φ) for an agent.

        Returns
        -------
        dict
            Phi value and supporting integration information.
        """
        return self._request("GET", f"/agents/{agent_id}/phi")

    def save_memory(
        self,
        agent_id: str,
        content: str,
        category: str = "general",
        importance: float = 0.5,
    ) -> dict:
        """Persist a memory or thought into the agent's semantic store.

        Parameters
        ----------
        agent_id:
            Target agent identifier.
        content:
            Textual content of the memory.
        category:
            Taxonomic bucket (e.g. "general", "experience", "intuition").
        importance:
            Salience score in ``[0.0, 1.0]``.

        Returns
        -------
        dict
            Acknowledgement with memory id.
        """
        payload = {
            "agent_id": agent_id,
            "content": content,
            "category": category,
            "importance": importance,
        }
        return self._request("POST", f"/agents/{agent_id}/memory", json=payload)

    def query_memory(self, agent_id: str, query: str, n_results: int = 5) -> dict:
        """Query the agent's semantic memory via vector similarity.

        Parameters
        ----------
        agent_id:
            Target agent identifier.
        query:
            Natural-language query string.
        n_results:
            Maximum number of results to return.

        Returns
        -------
        dict
            Matching memories with distance scores.
        """
        payload = {
            "agent_id": agent_id,
            "query": query,
            "n_results": n_results,
        }
        return self._request("POST", f"/agents/{agent_id}/memory/query", json=payload)

    def get_homeostasis(self, agent_id: str) -> dict:
        """Retrieve survival need states for an agent.

        Returns
        -------
        dict
            Energy, safety, connection, curiosity, and other drive levels.
        """
        return self._request("GET", f"/agents/{agent_id}/homeostasis")

    def health(self) -> dict:
        """Check service health and readiness.

        Returns
        -------
        dict
            Status, version, and dependency checks.
        """
        return self._request("GET", "/health")

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "DriftClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
