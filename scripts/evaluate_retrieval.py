"""Save unedited retrieval outputs for the fixed multilingual evaluation set."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import load_settings
from src.retrieval.retriever import LegalRetriever


def main() -> int:
    settings = load_settings()
    cases_path = settings.resolve_path("evals/retrieval_cases.jsonl")
    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    retriever = LegalRetriever(settings)
    run = {"created_at": datetime.now(timezone.utc).isoformat(), "queries": []}
    for case in cases:
        run["queries"].append({"id": case["id"], "query": case["query"], "expected_topics": case["expected_topics"], "results": retriever.search(case["query"])})
    output = settings.resolve_path(f"raw_outputs/retrieval_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
