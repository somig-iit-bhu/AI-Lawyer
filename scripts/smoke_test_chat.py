"""Exercise the exact Streamlit chat pipeline with a non-personal sample query."""
from __future__ import annotations

import json
import sys
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


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    settings = load_settings()
    provider = create_provider(settings.llm)
    retriever = LegalRetriever(settings)
    case = CaseState()
    query = "I bought a defective phone from an online seller. The seller has refused my refund. What can I do?"
    message = CaseService().add_user_message(case, query)
    extraction = CaseIntakeService(provider, "config/prompts/case_extraction_v1.md").extract(case, query)
    CaseService().apply_extraction(case, extraction, message.message_id)
    answer, sources = LegalAnswerService(retriever, provider, "config/prompts/rag_answer_v1.md", settings.safety).answer(case, query)
    report = {"query": query, "answer": answer.model_dump(), "sources": [{"source_file": source["source_file"], "page": source["page_start"], "section": source.get("section"), "similarity": source["similarity"]} for source in sources]}
    destination = PROJECT_ROOT / "reports" / "chat_smoke_result.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
