"""Run controlled English, Hinglish, and Hindi retrieval probes."""
from __future__ import annotations
import json
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import load_settings
from src.retrieval.retriever import LegalRetriever

QUERIES = ["What remedies are available for defective goods?", "How can a consumer complain about a denied refund?", "What is an unfair trade practice?", "Which Consumer Commission has jurisdiction?", "What obligations apply to e-commerce sellers?", "Mujhe defective product ka refund nahi mil raha.", "मैंने एक खराब प्रोडक्ट खरीदा है और रिफंड नहीं मिल रहा।"]
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def main() -> int:
    settings = load_settings(); retriever = LegalRetriever(settings); results = {}
    for query in QUERIES:
        hits = retriever.search(query); results[query] = hits
        logging.info("Query: %s", query)
        for rank, hit in enumerate(hits, 1): logging.info("%d | %.4f | %s | %s | p.%s", rank, hit["similarity"], hit["document_title"], hit.get("section"), hit["page_start"])
    path = settings.resolve_path("reports/retrieval_results.json")
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0

if __name__ == "__main__": raise SystemExit(main())
