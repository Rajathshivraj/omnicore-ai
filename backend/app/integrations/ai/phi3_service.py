from __future__ import annotations

import asyncio
import json
from urllib import error, request


class Phi3IntegrationService:
    """Adapter for local or hosted Phi-3 inference.

    If no endpoint is configured, callers receive a deterministic fallback so AI
    workflows remain available as decision support instead of blocking core ops.
    """

    def __init__(
        self,
        *,
        endpoint_url: str | None = None,
        model_name: str = "phi-3",
        model_version: str = "local",
        timeout_seconds: int = 20,
    ) -> None:
        self.endpoint_url = endpoint_url
        self.model_name = model_name
        self.model_version = model_version
        self.timeout_seconds = timeout_seconds

    async def complete(self, prompt: str) -> str:
        if not self.endpoint_url:
            return self._fallback_completion(prompt)

        try:
            return await asyncio.to_thread(self._post_completion, prompt)
        except (OSError, TimeoutError, error.URLError, json.JSONDecodeError):
            return self._fallback_completion(prompt)

    def _post_completion(self, prompt: str) -> str:
        body = json.dumps({"model": self.model_name, "prompt": prompt, "stream": False}).encode()
        api_request = request.Request(
            self.endpoint_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(api_request, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode())

        if isinstance(payload, dict):
            for key in ("response", "completion", "text", "answer"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return self._fallback_completion(prompt)

    def _fallback_completion(self, prompt: str) -> str:
        return (
            "Model inference is not configured. Based on the retrieved operational "
            "context, review demand changes, inventory coverage, and reorder signals "
            "before approving an action."
        )
