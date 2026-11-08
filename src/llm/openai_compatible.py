"""OpenAI-compatible provider using the configured endpoint and key."""
from __future__ import annotations

import os

from .base import GenerationRequest, GenerationResult, LLMError, LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    provider_name = "openai_compatible"

    def __init__(self, settings) -> None:
        super().__init__(settings)
        if not settings.api_key_env:
            raise ValueError("llm.api_key_env must name the API-key environment variable.")
        api_key = os.getenv(settings.api_key_env)
        if not api_key:
            raise ValueError(f"Environment variable {settings.api_key_env!r} is not set.")
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError("openai is required for the OpenAI-compatible provider.") from error
        self.client = OpenAI(api_key=api_key, base_url=settings.api_base_url, timeout=settings.timeout_seconds, max_retries=0)

    def _generate_once(self, request: GenerationRequest) -> GenerationResult:
        instructions = request.system_instruction
        if request.response_schema:
            schema = request.response_schema.model_json_schema()
            instructions = (instructions or "") + "\nReturn only JSON that validates against this schema:\n" + str(schema)
        response = self.client.responses.create(model=self.settings.model, input=[{"role": message.role, "content": message.content} for message in request.messages], instructions=instructions, temperature=self.settings.temperature, max_output_tokens=self.settings.max_output_tokens)
        text = getattr(response, "output_text", None)
        if not text:
            raise LLMError("Provider returned no text content.")
        return GenerationResult(text=text, provider=self.provider_name, model=self.settings.model, raw_response={"response_id": getattr(response, "id", None)})
