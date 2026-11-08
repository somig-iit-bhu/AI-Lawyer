"""Constrained complaint/demand-letter draft generation from confirmed facts only."""
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel
from src.case.models import CaseState, FactStatus
from src.llm.base import GenerationRequest, Message
from src.llm.prompt_loader import load_prompt

class DraftKind(str, Enum):
    CONSUMER_COMPLAINT = "consumer_complaint"
    REFUND_DEMAND = "refund_demand"
    CASE_SUMMARY = "case_summary"

class DraftDocument(BaseModel):
    kind: DraftKind
    title: str
    body: str
    missing_fields: list[str]
    disclaimer: str

class DocumentDraftingService:
    def __init__(self, llm_provider, prompt_path: str) -> None:
        self.llm_provider = llm_provider
        self.prompt = load_prompt(prompt_path)

    def draft(self, kind: DraftKind, case: CaseState, source_labels: list[str]) -> DraftDocument:
        confirmed = {key: fact.value for key, fact in case.facts.items() if fact.status in {FactStatus.CONFIRMED, FactStatus.CORRECTED}}
        request = GenerationRequest(messages=[Message(role="user", content=f"Document type: {kind.value}\nConfirmed facts only: {confirmed}\nAvailable source labels: {source_labels}")], system_instruction=self.prompt, response_schema=DraftDocument)
        document = self.llm_provider.generate(request).parse_as(DraftDocument)
        document.kind = kind
        return document
