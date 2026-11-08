"""Build a reproducible FAISS index and its compatibility manifest."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from src.ingestion.inventory import sha256
from .embeddings import SentenceTransformerEmbedder
from .vector_store import create_flat_ip, save_index

def read_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file: return [json.loads(line) for line in file if line.strip()]

def build_index(settings, chunks_path: Path) -> dict:
    chunks = read_jsonl(chunks_path)
    if not chunks: raise RuntimeError(f"No chunks in {chunks_path}; run scripts/parse_documents.py first.")
    chunks.sort(key=lambda item: item["chunk_id"])
    unique_chunks: dict[str, dict] = {}
    for chunk in chunks:
        existing = unique_chunks.get(chunk["chunk_id"])
        if existing is None:
            unique_chunks[chunk["chunk_id"]] = chunk
        else:
            existing.setdefault("duplicate_source_files", []).append(chunk["source_file"])
    chunks = list(unique_chunks.values())
    embedder = SentenceTransformerEmbedder(settings.embeddings)
    vectors = embedder.encode_passages([chunk["text"] for chunk in chunks])
    index = create_flat_ip(vectors)
    index_path = settings.resolve_path(settings.vector_store.index_path)
    metadata_path = settings.resolve_path(settings.vector_store.metadata_path)
    manifest_path = settings.resolve_path(settings.vector_store.manifest_path)
    save_index(index, index_path)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with metadata_path.open("w", encoding="utf-8") as file:
        for position, chunk in enumerate(chunks):
            file.write(json.dumps({"vector_id": position, **chunk}, ensure_ascii=False) + "\n")
    sources = {item["source_file"]: item.get("document_id") for item in chunks}
    checksums = {item["source_file"]: item.get("source_checksum") for item in chunks if item.get("source_checksum")}
    manifest = {"format_version": 1, "built_at": datetime.now(timezone.utc).isoformat(), "embedding_model_id": settings.embeddings.model_id, "embedding_dimensions": int(vectors.shape[1]), "normalize": settings.embeddings.normalize, "query_prefix": settings.embeddings.query_prefix, "passage_prefix": settings.embeddings.passage_prefix, "chunking": settings.chunking.model_dump(), "source_documents": sources, "source_checksums": checksums, "chunk_count": len(chunks), "chunk_fingerprint": hashlib.sha256("".join(item["chunk_id"] for item in chunks).encode()).hexdigest()}
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest
