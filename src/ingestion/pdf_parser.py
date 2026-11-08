"""PyMuPDF parser producing page-level JSONL provenance records."""
from __future__ import annotations
import json
from pathlib import Path
from .cleaner import clean_text, repeated_edge_lines
from .inventory import sha256
from .language_filter import classify_page, english_blocks_from_mixed_page

def _pdf():
    try:
        import pymupdf
        return pymupdf
    except ImportError as error:
        raise RuntimeError("PyMuPDF is required. Install requirements.txt.") from error

def document_id(checksum: str) -> str:
    return f"pdf-{checksum[:20]}"

def parse_pdf(path: Path, output_path: Path, settings, source_metadata: dict | None = None) -> list[dict]:
    try:
        document = _pdf().open(path)
    except Exception as error:
        raise RuntimeError(f"Cannot open PDF {path.name}: {error}") from error
    checksum = sha256(path)
    raw_pages = [page.get_text("text") for page in document]
    headers = repeated_edge_lines(raw_pages, "header", settings.repeated_line_ratio) if settings.remove_repeated_headers else set()
    footers = repeated_edge_lines(raw_pages, "footer", settings.repeated_line_ratio) if settings.remove_repeated_footers else set()
    source_metadata = source_metadata or {}
    detected_title = next((line.strip() for line in raw_pages[0].splitlines() if len(line.strip()) > 12), None) if raw_pages else None
    title = source_metadata.get("title") or detected_title
    rows: list[dict] = []
    for number, raw_text in enumerate(raw_pages, 1):
        cleaned = clean_text(raw_text, headers, footers)
        language, manual_review, warnings = classify_page(cleaned, settings.preferred_language)
        indexable_text = cleaned
        if language == "mixed" and settings.preferred_language == "en":
            extracted = english_blocks_from_mixed_page(cleaned)
            if extracted:
                indexable_text = extracted
                language = "en"
                warnings.append("Indexed a substantive English block; original bilingual extraction remains in raw_text.")
            else:
                indexable_text = ""
                warnings.append("No reliable substantive English block was found; this bilingual page was excluded from the English index.")
        quality = min(1.0, len(cleaned.strip()) / 500)
        rows.append({"document_id": document_id(checksum), "source_file": path.name, "source_checksum": checksum, "document_title": title, "document_type": source_metadata.get("document_type", "unknown"), "source_url": source_metadata.get("url"), "legal_status": source_metadata.get("legal_status", "unverified"), "page_number": number, "text": indexable_text, "raw_text": cleaned, "raw_text_characters": len(raw_text), "language": language, "extraction_quality": round(quality, 3), "requires_ocr": not bool(cleaned.strip()), "manual_review_required": manual_review, "warnings": warnings})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as output:
        for row in rows: output.write(json.dumps(row, ensure_ascii=False) + "\n")
    return rows
