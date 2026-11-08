"""Persist unedited structured chat outputs for non-personal evaluation prompts."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.case.models import CaseState
from src.case.service import CaseService
from src.config import PROJECT_ROOT, load_settings
from src.llm.factory import create_provider
from src.retrieval.retriever import LegalRetriever
from src.services.case_intake import CaseIntakeService
from src.services.legal_answer import LegalAnswerService

EVALUATIONS = [
    {"id": "defective-phone-en", "query": "I bought a defective phone from an online seller. The seller has refused my refund. What can I do?"},
    {"id": "refund-hinglish", "query": "Maine online defective product liya tha, seller refund nahi de raha. Mere paas invoice aur chats hain. Kya steps lene chahiye?"},
    {"id": "jurisdiction-en", "query": "I was sold a defective appliance. How do I identify the Consumer Commission that may have jurisdiction?"},
]


def run_case(query: str, provider, retriever, settings) -> dict:
    case = CaseState()
    case_service = CaseService()
    message = case_service.add_user_message(case, query)
    extraction = CaseIntakeService(provider, "config/prompts/case_extraction_v1.md").extract(case, query)
    case_service.apply_extraction(case, extraction, message.message_id)
    answer, sources = LegalAnswerService(retriever, provider, "config/prompts/rag_answer_v1.md", settings.safety).answer(case, query)
    return {
        "query": query,
        "fact_extraction": extraction.model_dump(mode="json"),
        "case_state": case.model_dump(mode="json"),
        "answer": answer.model_dump(mode="json"),
        "retrieved_sources": sources,
    }


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    settings = load_settings()
    provider = create_provider(settings.llm)
    retriever = LegalRetriever(settings)
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "llm_provider": settings.llm.provider,
        "llm_model": settings.llm.model,
        "evaluations": [],
    }
    path = PROJECT_ROOT / "raw_outputs" / f"problem2_chat_outputs_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    for scenario in EVALUATIONS:
        output["evaluations"].append({"id": scenario["id"], **run_case(scenario["query"], provider, retriever, settings)})
        # Persist each completed case unedited, even if a later provider call fails.
        path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
