"""Minimal deterministic cleanup that preserves legal numbering and punctuation."""
from __future__ import annotations
import re
from collections import Counter

def repeated_edge_lines(pages: list[str], edge: str, ratio: float) -> set[str]:
    candidates = []
    for page in pages:
        lines = [line.strip() for line in page.splitlines() if line.strip()]
        if lines: candidates.append(lines[0] if edge == "header" else lines[-1])
    cutoff = max(2, round(len(pages) * ratio))
    return {line for line, count in Counter(candidates).items() if count >= cutoff and len(line) > 3}

def clean_text(text: str, headers: set[str] | None = None, footers: set[str] | None = None) -> str:
    removed = (headers or set()) | (footers or set())
    lines = [line.strip() for line in text.replace("\u00ad", "").replace("\xa0", " ").splitlines()]
    compact = "\n".join(line for line in lines if line not in removed)
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", compact)).strip()
