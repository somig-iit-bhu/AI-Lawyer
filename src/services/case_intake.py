"""Turns user messages into explicit, reviewable fact proposals."""
from __future__ import annotations

from src.case.models import CaseState, FactExtraction
from src.llm.base import GenerationRequest, Message
from src.llm.prompt_loader import load_prompt


class CaseIntakeService:
    def __init__(self, llm_provider, prompt_path: str) -> None:
        self.llm_provider = llm_provider
        self.prompt = load_prompt(prompt_path)

    def extract(self, case: CaseState, user_message: str) -> FactExtraction:
        context = {key: fact.model_dump(mode="json") for key, fact in case.facts.items()}
        request = GenerationRequest(messages=[Message(role="user", content=f"Existing structured facts: {context}\n\nNew user message: {user_message}")], system_instruction=self.prompt, response_schema=FactExtraction)
        return self.llm_provider.generate(request).parse_as(FactExtraction)
