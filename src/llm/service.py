"""High-level LLM service that applies the configured versioned prompt."""
from __future__ import annotations

from pydantic import BaseModel
from .base import GenerationRequest, Message
from .factory import create_provider
from .prompt_loader import load_prompt


class LLMService:
    def __init__(self, settings) -> None:
        self.settings = settings
        self.provider = create_provider(settings.llm)
        self.default_prompt = load_prompt(settings.llm.system_prompt_path)

    def generate(self, user_message: str, schema: type[BaseModel] | None = None):
        result = self.provider.generate(GenerationRequest(messages=[Message(role="user", content=user_message)], system_instruction=self.default_prompt, response_schema=schema))
        return result.parse_as(schema) if schema else result
