"""Conservative language classification; ambiguous content is never discarded."""
from __future__ import annotations
import re
from .inventory import detect_language

def classify_page(text: str, preferred_language: str) -> tuple[str, bool, list[str]]:
    language = detect_language(text)
    if not text.strip(): return language, True, ["No extractable text; OCR is required for this page."]
    if language == "mixed": return language, True, ["Mixed Hindi/English page retained intact; translation boundaries were not inferred."]
    if preferred_language != "all" and language not in {preferred_language, "unknown"}:
        return language, False, [f"Non-preferred {language} page retained to avoid discarding legal content."]
    return language, False, []


def english_blocks_from_mixed_page(text: str, minimum_letters: int = 220) -> str | None:
    """Keep substantive English runs from a bilingual page without line-by-line translation guesses."""
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        latin = len(re.findall(r"[A-Za-z]", line))
        devanagari = len(re.findall(r"[\u0900-\u097F]", line))
        is_english = latin >= 3 and latin > devanagari * 1.5
        is_neutral = not latin and not devanagari
        if is_english or (current and is_neutral):
            current.append(line)
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    substantive = ["\n".join(block).strip() for block in blocks if len(re.findall(r"[A-Za-z]", "\n".join(block))) >= minimum_letters]
    return "\n\n".join(substantive) if substantive else None
