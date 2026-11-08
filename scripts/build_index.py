"""Build the local FAISS index from the current legal chunks."""
from __future__ import annotations
import json
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import load_settings
from src.retrieval.index_builder import build_index

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def main() -> int:
    settings = load_settings()
    manifest = build_index(settings, settings.resolve_path("data/chunks/legal_chunks.jsonl"))
    logging.info("Indexed %(chunk_count)s chunks at %(embedding_dimensions)s dimensions", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__": raise SystemExit(main())
