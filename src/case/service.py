"""Deterministic case-state updates; LLM output is treated as proposed data."""
from __future__ import annotations

from .models import CaseFact, CaseMessage, CaseState, FactExtraction, FactStatus


class CaseService:
    def add_user_message(self, case: CaseState, content: str) -> CaseMessage:
        message = CaseMessage(role="user", content=content)
        case.messages.append(message)
        return message

    def apply_extraction(self, case: CaseState, extraction: FactExtraction, source_message_id: str) -> list[str]:
        changes: list[str] = []
        if extraction.issue_type and not case.issue_type:
            case.issue_type = extraction.issue_type
            changes.append("issue_type")
        for proposed in extraction.facts:
            proposed.source_message_id = source_message_id
            existing = case.facts.get(proposed.key)
            if existing and existing.value != proposed.value:
                proposed.status = FactStatus.CORRECTED
            case.facts[proposed.key] = proposed
            changes.append(proposed.key)
        case.missing_information = sorted(set(extraction.missing_information))
        return changes

    def correct_fact(self, case: CaseState, key: str, value: str, note: str | None = None) -> None:
        case.facts[key] = CaseFact(key=key, value=value, status=FactStatus.CONFIRMED, note=note or "User-corrected fact")

    def next_questions(self, case: CaseState, candidates: list[str], limit: int = 3) -> list[str]:
        unanswered = [question for question in candidates if question not in case.missing_information]
        return (case.missing_information + unanswered)[:limit]
