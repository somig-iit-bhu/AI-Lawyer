"""Provider-independent request, response, error, and retry behavior."""
from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    """A provider request failed after configuration and retry handling."""


class Message(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1)


class GenerationRequest(BaseModel):
    messages: list[Message] = Field(min_length=1)
    system_instruction: str | None = None
    response_schema: type[BaseModel] | None = None


class GenerationResult(BaseModel):
    text: str
    provider: str
    model: str
    raw_response: dict[str, Any] | None = None

    def parse_as(self, schema: type[T]) -> T:
        try:
            payload = json.loads(self.text)
        except json.JSONDecodeError as error:
            raise LLMError("Provider response was not valid JSON for the requested schema.") from error
        return schema.model_validate(payload)


class LLMProvider(ABC):
    provider_name: str

    def __init__(self, settings) -> None:
        if not settings.model:
            raise ValueError("llm.model is empty. Configure it before creating an LLM provider.")
        self.settings = settings

    def generate(self, request: GenerationRequest) -> GenerationResult:
        last_error: Exception | None = None
        for attempt in range(self.settings.max_retries + 1):
            try:
                return self._generate_once(request)
            except Exception as error:
                last_error = error
                if attempt == self.settings.max_retries or not self._is_retryable(error):
                    break
                delay = min(2**attempt, 8)
                logger.warning("%s request failed (attempt %s/%s): %s; retrying in %ss", self.provider_name, attempt + 1, self.settings.max_retries + 1, error, delay)
                time.sleep(delay)
        raise LLMError(f"{self.provider_name} generation failed after retries: {last_error}") from last_error

    @staticmethod
    def _is_retryable(error: Exception) -> bool:
        """Avoid retrying invalid keys, unavailable models, and other permanent 4xx errors."""
        message = str(error).lower()
        transient_markers = ("429", "500", "502", "503", "504", "timeout", "temporarily", "unavailable", "connection", "network")
        permanent_markers = ("400", "401", "403", "404", "invalid api key", "not found")
        return any(marker in message for marker in transient_markers) and not any(marker in message for marker in permanent_markers)

    @abstractmethod
    def _generate_once(self, request: GenerationRequest) -> GenerationResult:
        """Execute exactly one provider request."""
