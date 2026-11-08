"""Validated, centralized runtime configuration for NyayaSaathi."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, model_validator

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class AppSettings(BaseModel):
    name: str = "NyayaSaathi"
    environment: str = "development"
    default_language: Literal["auto", "en", "hi", "hinglish"] = "auto"
    supported_languages: list[str] = Field(default_factory=lambda: ["en", "hi", "hinglish"])


class LLMSettings(BaseModel):
    provider: str | None = None
    model: str | None = None
    api_base_url: str | None = None
    api_key_env: str | None = None
    system_prompt_path: str = "config/prompts/legal_assistant_v1.md"
    structured_output: bool = True
    temperature: float = Field(default=0.2, ge=0, le=2)
    max_output_tokens: int = Field(default=2048, gt=0)
    timeout_seconds: int = Field(default=45, gt=0)
    max_retries: int = Field(default=2, ge=0)


class EmbeddingSettings(BaseModel):
    provider: Literal["sentence_transformers"] = "sentence_transformers"
    model_id: str | None = None
    cache_folder: str | None = None
    device: str | None = None
    trust_remote_code: bool = False
    local_files_only: bool = False
    normalize: bool = True
    batch_size: int = Field(default=32, gt=0)
    query_prefix: str = "query: "
    passage_prefix: str = "passage: "
    tokenizer: Literal["regex", "huggingface"] = "regex"


class PDFProcessingSettings(BaseModel):
    input_directory: str = "data/raw"
    output_directory: str = "data/parsed"
    preferred_language: Literal["en", "hi", "all"] = "en"
    preserve_page_references: bool = True
    remove_repeated_headers: bool = True
    remove_repeated_footers: bool = True
    repeated_line_ratio: float = Field(default=0.6, gt=0, le=1)
    min_extraction_quality: float = Field(default=0.75, ge=0, le=1)
    enable_ocr: bool = False


class ChunkingSettings(BaseModel):
    strategy: Literal["section_aware"] = "section_aware"
    target_tokens: int = Field(default=450, gt=0)
    max_tokens: int = Field(default=650, gt=0)
    overlap_tokens: int = Field(default=60, ge=0)
    preserve_headings: bool = True

    @model_validator(mode="after")
    def validate_sizes(self) -> "ChunkingSettings":
        if self.target_tokens > self.max_tokens:
            raise ValueError("chunking.target_tokens cannot exceed max_tokens")
        if self.overlap_tokens >= self.max_tokens:
            raise ValueError("chunking.overlap_tokens must be less than max_tokens")
        return self


class VectorStoreSettings(BaseModel):
    provider: Literal["faiss"] = "faiss"
    index_type: Literal["flat_ip"] = "flat_ip"
    index_path: str = "data/index/legal.faiss"
    metadata_path: str = "data/index/metadata.jsonl"
    manifest_path: str = "data/index/manifest.json"


class RetrievalSettings(BaseModel):
    dense_top_k: int = Field(default=8, gt=0)
    final_top_k: int = Field(default=5, gt=0)
    hybrid_enabled: bool = True
    dense_weight: float = Field(default=0.75, ge=0, le=1)
    lexical_weight: float = Field(default=0.25, ge=0, le=1)
    min_similarity: float | None = Field(default=None, ge=-1, le=1)

    @model_validator(mode="after")
    def validate_depth(self) -> "RetrievalSettings":
        if self.final_top_k > self.dense_top_k:
            raise ValueError("retrieval.final_top_k cannot exceed dense_top_k")
        if self.hybrid_enabled and not (self.dense_weight or self.lexical_weight):
            raise ValueError("At least one hybrid retrieval weight must be greater than zero")
        return self


class FeatureSettings(BaseModel):
    consumer_disputes: bool = True
    rental_disputes: bool = False
    voice_input: bool = False
    document_upload: bool = False
    document_export: bool = True


class SafetySettings(BaseModel):
    require_source_citations: bool = True
    allow_unsupported_legal_claims: bool = False
    require_professional_help_disclaimer: bool = True


class Settings(BaseModel):
    app: AppSettings = Field(default_factory=AppSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    embeddings: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    pdf_processing: PDFProcessingSettings = Field(default_factory=PDFProcessingSettings)
    chunking: ChunkingSettings = Field(default_factory=ChunkingSettings)
    vector_store: VectorStoreSettings = Field(default_factory=VectorStoreSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    features: FeatureSettings = Field(default_factory=FeatureSettings)
    safety: SafetySettings = Field(default_factory=SafetySettings)

    def resolve_path(self, value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else PROJECT_ROOT / path


@lru_cache(maxsize=4)
def load_settings(path: str | Path = PROJECT_ROOT / "config/settings.yaml") -> Settings:
    settings_path = Path(path)
    if not settings_path.exists():
        raise FileNotFoundError(f"Settings file does not exist: {settings_path}")
    with settings_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return Settings.model_validate(data)
