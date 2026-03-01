"""
Flexible LLM backend — supports OpenAI-compatible APIs, Ollama, or graceful fallback.
"""

import json
import os
import urllib.request
import urllib.error
from typing import Any, Dict, List


class AIBackend:
    """
    Unified AI interface with automatic backend selection:
      1. If api_key is given → OpenAI-compatible API
      2. If Ollama is running locally → Ollama
      3. Otherwise → None (fallback to plain CLI)
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        ollama_url: str = "http://localhost:11434",
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model or os.environ.get("CARETAKER_MODEL", "gpt-3.5-turbo")
        self.ollama_url = ollama_url
        self._backend: str | None = None

        # Auto-detect OpenRouter keys and set correct base URL
        if self.api_key and self.api_key.startswith("sk-or-"):
            if not base_url and not os.environ.get("OPENAI_BASE_URL"):
                self.base_url = "https://openrouter.ai/api/v1"
            if not model and not os.environ.get("CARETAKER_MODEL"):
                self.model = "openai/gpt-3.5-turbo"

        self._detect_backend()

    def _detect_backend(self) -> None:
        """Auto-detect the best available backend."""
        if self.api_key:
            self._backend = "openai"
            return

        # Try Ollama
        try:
            req = urllib.request.Request(f"{self.ollama_url}/api/tags")
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read().decode())
                models = [m.get("name", "") for m in data.get("models", [])]
                if models:
                    self._backend = "ollama"
                    if not self.model or self.model == "gpt-3.5-turbo":
                        # Pick first available Ollama model
                        self.model = models[0]
                    return
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            pass

        self._backend = None

    @property
    def available(self) -> bool:
        return self._backend is not None

    @property
    def backend_name(self) -> str:
        return self._backend or "none"

    def ask(
        self,
        prompt: str,
        system: str = "You are PyCareTaker, a helpful Python package management assistant.",
        temperature: float = 0.3,
    ) -> str:
        """Send a prompt to the LLM and return the response text."""
        if self._backend == "openai":
            return self._ask_openai(prompt, system, temperature)
        elif self._backend == "ollama":
            return self._ask_ollama(prompt, system, temperature)
        else:
            return ""

    def _ask_openai(self, prompt: str, system: str, temperature: float) -> str:
        """Call an OpenAI-compatible chat completions endpoint."""
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
        }).encode()

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                return data["choices"][0]["message"]["content"].strip()
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError, TimeoutError, OSError) as exc:
            return f"[AI ERROR] {exc}"

    def _ask_ollama(self, prompt: str, system: str, temperature: float) -> str:
        """Call the local Ollama API."""
        url = f"{self.ollama_url}/api/chat"
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": temperature},
        }).encode()

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
                return data.get("message", {}).get("content", "").strip()
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError, TimeoutError, OSError) as exc:
            return f"[AI ERROR] {exc}"


# Singleton — created lazily by the CLI
_instance: AIBackend | None = None


def get_backend(
    api_key: str | None = None,
    model: str | None = None,
) -> AIBackend:
    """Return (or create) the global AIBackend singleton."""
    global _instance
    if _instance is None:
        _instance = AIBackend(api_key=api_key, model=model)
    return _instance
