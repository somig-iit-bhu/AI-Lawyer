"""Extract statutory boundaries without attempting legal consolidation."""
from __future__ import annotations
import re
from dataclasses import dataclass

BOUNDARY = re.compile(r"(?im)^(?:(section|rule|chapter)\s+)?(\d+[A-Za-z]?(?:\s*\([^\n)]{1,40}\))?)\s*[.:-]\s*(.{0,180})$")

@dataclass(frozen=True)
class SectionBlock:
    identifier: str | None
    heading: str | None
    text: str

def split_sections(text: str) -> list[SectionBlock]:
    matches = list(BOUNDARY.finditer(text))
    if not matches: return [SectionBlock(None, None, text)] if text else []
    blocks = []
    if matches[0].start() > 0: blocks.append(SectionBlock(None, None, text[:matches[0].start()].strip()))
    for index, match in enumerate(matches):
        end = matches[index+1].start() if index+1 < len(matches) else len(text)
        identifier = f"{(match.group(1) or 'section').lower()} {match.group(2)}"
        blocks.append(SectionBlock(identifier, match.group(3).strip() or None, text[match.start():end].strip()))
    return [block for block in blocks if block.text]
