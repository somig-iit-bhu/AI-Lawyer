"""Parse PDFs to page JSONL, then create reproducible legal chunks."""
from __future__ import annotations
import json
import logging
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import load_settings
from src.ingestion.chunker import build_chunks
from src.ingestion.pdf_parser import parse_pdf
from src.ingestion.sources import load_source_registry

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def main() -> int:
    settings = load_settings()
    source_directory = settings.resolve_path(settings.pdf_processing.input_directory)
    parsed_directory = settings.resolve_path(settings.pdf_processing.output_directory)
    parsed_directory.mkdir(parents=True, exist_ok=True)
    source_registry = load_source_registry(settings.resolve_path("config/sources.yaml"))
    all_chunks, documents, failures = [], [], []
    for pdf in sorted(source_directory.glob("*.pdf")):
        try:
            pages = parse_pdf(pdf, parsed_directory / f"{pdf.stem}.jsonl", settings.pdf_processing, source_registry.get(pdf.name))
            chunks = build_chunks(pages, settings.chunking, settings.embeddings)
            all_chunks.extend(chunks)
            documents.append({"source_file": pdf.name, "pages": len(pages), "chunks": len(chunks), "manual_review_pages": [item["page_number"] for item in pages if item["manual_review_required"]]})
        except Exception as error:
            logging.exception("Failed to parse %s", pdf.name)
            failures.append({"source_file": pdf.name, "error": str(error)})
    chunks_path = settings.resolve_path("data/chunks/legal_chunks.jsonl")
    chunks_path.parent.mkdir(parents=True, exist_ok=True)
    with chunks_path.open("w", encoding="utf-8") as output:
        for chunk in all_chunks: output.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    report = {"documents": documents, "failures": failures, "total_chunks": len(all_chunks), "language_distribution": Counter(item["language"] for item in all_chunks), "average_chunk_tokens": sum(item["token_count"] for item in all_chunks) / len(all_chunks) if all_chunks else 0, "maximum_chunk_tokens": max((item["token_count"] for item in all_chunks), default=0)}
    report_path = settings.resolve_path("reports/parsing_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=dict), encoding="utf-8")
    logging.info("Parsed %s PDFs into %s chunks; report: %s", len(documents), len(all_chunks), report_path)
    return 1 if failures else 0

if __name__ == "__main__": raise SystemExit(main())
