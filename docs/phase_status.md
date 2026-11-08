# Delivery status

## Phase 1 — implementation complete, runtime validation pending

The PDF inspection, parsing, bilingual safety handling, chunking, embedding adapter, FAISS index builder, manifest validation, and retrieval command are implemented. Runtime validation remains pending until an embedding model ID is configured and the index is built successfully with the selected local environment.

## Phases 2–6 — implementation complete, runtime validation pending

The provider abstraction, Gemini provider, OpenAI-compatible provider, retry/timeout behavior, prompt loader, structured response contract, structured case state, RAG answer service, constrained draft service, and Streamlit UI are implemented. Provider calls are intentionally disabled until credentials and model configuration are supplied.

## Phase 7 — explicitly deferred optional features

Voice input, rental disputes, uploads, and opposing-party simulation are feature-flagged but not implemented.

## Phase 8 — delivery assets complete, runtime validation pending

Multilingual evaluation cases, a raw-output evaluation script, container packaging, setup documentation, and limitations documentation are present. Actual evaluation must run after the user configures the embedding model and generation provider.
