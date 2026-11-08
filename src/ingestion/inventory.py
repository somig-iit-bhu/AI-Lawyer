"""Inspect source PDFs without using their filenames as legal truth."""
from __future__ import annotations
import hashlib
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

DEVANAGARI = re.compile(r"[\u0900-\u097F]")
LATIN = re.compile(r"[A-Za-z]")

def _pdf():
    try:
        import pymupdf
        return pymupdf
    except ImportError as error:
        raise RuntimeError("PyMuPDF is required. Install requirements.txt.") from error

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def detect_language(text: str) -> str:
    hindi, english = len(DEVANAGARI.findall(text)), len(LATIN.findall(text))
    if hindi and english: return "mixed"
    if hindi: return "hi"
    if english: return "en"
    return "unknown"

def inspect_pdf(path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {"filename": path.name, "size_bytes": path.stat().st_size, "sha256": sha256(path), "status": "ok", "warnings": []}
    try:
        document = _pdf().open(path)
        samples, unreadable, languages = [], [], defaultdict(int)
        for number, page in enumerate(document, 1):
            text = page.get_text("text").strip()
            languages[detect_language(text)] += 1
            if not text: unreadable.append(number)
            elif len(samples) < 3: samples.append(text[:600])
        count = len(document)
        title = next((line.strip() for line in samples[0].splitlines() if len(line.strip()) > 12), None) if samples else None
        record.update({"page_count": count, "language_pages": dict(languages), "unreadable_pages": unreadable, "representative_text": samples, "detected_title": title, "document_type": "unknown", "extraction_quality": round((count-len(unreadable))/max(count,1),3), "likely_scanned": bool(unreadable)})
        if unreadable: record["warnings"].append("Blank extraction found; OCR/manual review may be required.")
    except Exception as error:
        record.update({"status": "error", "error": str(error), "page_count": 0})
    return record

def inspect_directory(directory: Path) -> list[dict[str, Any]]:
    records = [inspect_pdf(path) for path in sorted(directory.glob("*.pdf"))]
    duplicate_groups: defaultdict[str, list[str]] = defaultdict(list)
    for record in records: duplicate_groups[record.get("sha256", "")].append(record["filename"])
    for record in records: record["likely_duplicates"] = [name for name in duplicate_groups[record.get("sha256", "")] if name != record["filename"]]
    return records
