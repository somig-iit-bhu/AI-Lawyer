"""Create exactly the provider named in configuration."""
from __future__ import annotations

from .gemini import GeminiProvider
from .openai_compatible import OpenAICompatibleProvider


def create_provider(settings):
    providers = {"gemini": GeminiProvider, "openai_compatible": OpenAICompatibleProvider}
    if not settings.provider:
        raise ValueError("llm.provider is empty. Choose gemini or openai_compatible in config/settings.yaml.")
    try:
        return providers[settings.provider](settings)
    except KeyError as error:
        supported = ", ".join(sorted(providers))
        raise ValueError(f"Unsupported llm.provider={settings.provider!r}; supported: {supported}") from error
