"""Pydantic contracts persisted between ingestion and retrieval stages."""
from __future__ import annotations

from pydantic import BaseModel, Field


class PageRecord(BaseModel):
    document_id: str
    source_file: str
    source_checksum: str
    document_title: str | None = None
    document_type: str = "unknown"
    page_number: int = Field(gt=0)
    text: str
    raw_text_characters: int = Field(ge=0)
    language: str
    extraction_quality: float = Field(ge=0, le=1)
    requires_ocr: bool = False
    manual_review_required: bool = False
    warnings: list[str] = Field(default_factory=list)


class LegalChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str | None = None
    document_type: str = "unknown"
    source_file: str
    source_url: str | None = None
    language: str
    page_start: int
    page_end: int
    section: str | None = None
    heading: str | None = None
    text: str
    token_count: int = Field(gt=0)
    legal_status: str = "unverified"
    warnings: list[str] = Field(default_factory=list)
