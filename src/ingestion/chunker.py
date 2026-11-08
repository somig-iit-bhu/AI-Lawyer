"""Section-aware chunker with deterministic IDs and configurable token counting."""
from __future__ import annotations
import hashlib
import re
from collections import Counter
from typing import Iterable
from .section_parser import split_sections

TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", re.UNICODE)

class TokenCounter:
    def __init__(self, method: str, model_id: str | None = None) -> None:
        self.method = method
        self._tokenizer = None
        if method == "huggingface":
            if not model_id: raise ValueError("embeddings.model_id is required for huggingface tokenization")
            from transformers import AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(model_id)
    def count(self, text: str) -> int:
        if self._tokenizer is not None: return len(self._tokenizer.encode(text, add_special_tokens=False))
        return len(TOKEN_PATTERN.findall(text))

def stable_chunk_id(document_id: str, page_start: int, page_end: int, section: str | None, text: str) -> str:
    material = "|".join([document_id, str(page_start), str(page_end), section or "", text])
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]

def _windows(words: list[str], counter: TokenCounter, maximum: int, overlap: int) -> Iterable[str]:
    start = 0
    while start < len(words):
        end = start
        while end < len(words) and counter.count(" ".join(words[start:end+1])) <= maximum: end += 1
        if end == start: end += 1
        yield " ".join(words[start:end])
        if end >= len(words): return
        consumed = 0; next_start = end
        while next_start > start and consumed < overlap:
            next_start -= 1; consumed += counter.count(words[next_start])
        start = max(next_start, start + 1)

def build_chunks(pages: list[dict], chunk_settings, embedding_settings) -> list[dict]:
    counter = TokenCounter(embedding_settings.tokenizer, embedding_settings.model_id)
    chunks: list[dict] = []
    for page in pages:
        if not page["text"].strip(): continue
        for block in split_sections(page["text"]):
            for part in _windows(block.text.split(), counter, chunk_settings.max_tokens, chunk_settings.overlap_tokens):
                token_count = counter.count(part)
                if token_count == 0: continue
                chunks.append({"chunk_id": stable_chunk_id(page["document_id"], page["page_number"], page["page_number"], block.identifier, part), "document_id": page["document_id"], "document_title": page.get("document_title"), "document_type": page.get("document_type", "unknown"), "source_file": page["source_file"], "source_checksum": page["source_checksum"], "source_url": page.get("source_url"), "language": page["language"], "page_start": page["page_number"], "page_end": page["page_number"], "section": block.identifier, "heading": block.heading, "text": part, "token_count": token_count, "legal_status": page.get("legal_status", "unverified"), "warnings": page.get("warnings", [])})
    duplicate_ids = [key for key, value in Counter(item["chunk_id"] for item in chunks).items() if value > 1]
    if duplicate_ids: raise RuntimeError(f"Duplicate stable chunk IDs: {duplicate_ids[:3]}")
    return chunks
