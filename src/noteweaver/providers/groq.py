"""Explicit Groq configuration using the existing structured-note transport."""
import os

from noteweaver.models import ContractError

from .base import GenerationError
from .openai_compatible import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    """Generate through Groq; read only GROQ_API_KEY unless a key is provided.

    The user's Groq account plan determines quotas and billing. This provider
    never falls back to another service or model, and never retries automatically.
    Keys are held in memory only and are not part of a ProjectState.
    """

    def __init__(
        self, *, api_key: str | None = None, model: str = "openai/gpt-oss-20b",
        timeout: float = 60, max_completion_tokens: int = 4096,
    ) -> None:
        if type(model) is not str or not model.strip():
            raise ContractError("model must be nonblank text")
        if type(max_completion_tokens) is not int or max_completion_tokens <= 0:
            raise ContractError("max_completion_tokens must be a positive integer")
        super().__init__(
            api_key=api_key, base_url="https://api.groq.com/openai/v1",
            model=model, timeout=timeout, max_completion_tokens=max_completion_tokens,
        )

    def _credentials(self) -> str:
        key = self._configured_key if self._configured_key is not None else os.environ.get("GROQ_API_KEY")
        if not key or not key.strip():
            raise GenerationError("Groq API key missing; set GROQ_API_KEY or pass api_key to GroqProvider.")
        return key.strip()
