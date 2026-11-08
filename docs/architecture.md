# Phase 1 architecture

PDFs are inspected with PyMuPDF, parsed into page-level JSONL records, cleaned conservatively, section-split and chunked. Chunks are embedded locally using the configured Sentence Transformers model with configurable query/passage prefixes. Normalized float32 vectors are stored in FAISS `IndexFlatIP`; JSONL metadata uses the identical insertion order. A manifest prevents loading an index built with incompatible embedding settings.

For Phase 2, `src/llm/` isolates Gemini and OpenAI-compatible generation behind `LLMProvider`. Configuration chooses the provider; environment variables hold secrets; `LLMService` applies a versioned system prompt. The provider layer returns raw text or validates JSON through caller-provided Pydantic schemas. It does not yet make legal determinations or combine user facts with retrieval.
