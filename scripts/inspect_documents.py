"""Create a source-document inventory before parsing anything."""
from __future__ import annotations
import json
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import load_settings
from src.ingestion.inventory import inspect_directory

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def main() -> int:
    settings = load_settings()
    source_directory = settings.resolve_path(settings.pdf_processing.input_directory)
    if not source_directory.exists():
        logging.error("Configured PDF directory does not exist: %s", source_directory)
        return 2
    records = inspect_directory(source_directory)
    report_path = settings.resolve_path("reports/document_inventory.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    for record in records:
        logging.info("%s | status=%s pages=%s quality=%s languages=%s", record["filename"], record["status"], record.get("page_count"), record.get("extraction_quality"), record.get("language_pages"))
    return 1 if not records or any(record["status"] == "error" for record in records) else 0

if __name__ == "__main__": raise SystemExit(main())
