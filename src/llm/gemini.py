"""Gemini provider, loaded only when explicitly configured."""
from __future__ import annotations

import os

from .base import GenerationRequest, GenerationResult, LLMError, LLMProvider


class GeminiProvider(LLMProvider):
    provider_name = "gemini"

    def __init__(self, settings) -> None:
        super().__init__(settings)
        if not settings.api_key_env:
            raise ValueError("llm.api_key_env must name the Gemini API-key environment variable.")
        api_key = os.getenv(settings.api_key_env)
        if not api_key:
            raise ValueError(f"Environment variable {settings.api_key_env!r} is not set.")
        try:
            from google import genai
        except ImportError as error:
            raise RuntimeError("google-genai is required for the Gemini provider.") from error
        self._genai = genai
        self.client = genai.Client(api_key=api_key)

    def _generate_once(self, request: GenerationRequest) -> GenerationResult:
        contents = [{"role": message.role, "parts": [{"text": message.content}]} for message in request.messages]
        config_values = {"temperature": self.settings.temperature, "max_output_tokens": self.settings.max_output_tokens}
        if request.system_instruction:
            config_values["system_instruction"] = request.system_instruction
        if request.response_schema:
            config_values["response_mime_type"] = "application/json"
            config_values["response_schema"] = request.response_schema
        response = self.client.models.generate_content(model=self.settings.model, contents=contents, config=self._genai.types.GenerateContentConfig(**config_values))
        text = getattr(response, "text", None)
        if not text:
            raise LLMError("Gemini returned no text content.")
        return GenerationResult(text=text, provider=self.provider_name, model=self.settings.model, raw_response={"response_id": getattr(response, "response_id", None)})
