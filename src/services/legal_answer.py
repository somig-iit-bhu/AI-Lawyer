"""RAG response service that supplies explicit sources to the LLM."""
from __future__ import annotations

from pydantic import BaseModel, Field

from src.case.models import CaseState, FactStatus
from src.llm.base import GenerationRequest, Message
from src.llm.prompt_loader import load_prompt


class Citation(BaseModel):
    source_file: str
    page: int
    section: str | None = None


class LegalAnswer(BaseModel):
    answer: str
    practical_next_steps: list[str] = Field(default_factory=list)
    evidence_checklist: list[str] = Field(default_factory=list)
    uncertainty: str | None = None
    professional_help_recommended: bool = False
    citations: list[Citation] = Field(default_factory=list)


class LegalAnswerService:
    def __init__(self, retriever, llm_provider, prompt_path: str, safety_settings) -> None:
        self.retriever = retriever
        self.llm_provider = llm_provider
        self.prompt = load_prompt(prompt_path)
        self.safety = safety_settings

    def answer(self, case: CaseState, question: str) -> tuple[LegalAnswer, list[dict]]:
        sources = self.retriever.search(question)
        confirmed = {key: fact.value for key, fact in case.facts.items() if fact.status in {FactStatus.CONFIRMED, FactStatus.CORRECTED}}
        alleged = {key: fact.value for key, fact in case.facts.items() if fact.status == FactStatus.ALLEGED}
        source_context = [{"label": f"{item['source_file']} p.{item['page_start']} {item.get('section') or ''}".strip(), "text": item["text"], "legal_status": item.get("legal_status", "unverified")} for item in sources]
        message = f"Question: {question}\nConfirmed facts: {confirmed}\nUser allegations: {alleged}\nRetrieved sources: {source_context}"
        response = self.llm_provider.generate(GenerationRequest(messages=[Message(role="user", content=message)], system_instruction=self.prompt, response_schema=LegalAnswer)).parse_as(LegalAnswer)
        if self.safety.require_source_citations and not response.citations:
            raise ValueError("Generated legal response omitted required citations.")
        available = {(item["source_file"], item["page_start"]) for item in sources}
        invalid = [(citation.source_file, citation.page) for citation in response.citations if (citation.source_file, citation.page) not in available]
        if invalid:
            raise ValueError(f"Generated response cited sources that were not retrieved: {invalid}")
        return response, sources
