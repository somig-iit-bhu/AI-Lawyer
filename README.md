# NyayaSaathi — Phase 1

Phase 1 is a production-oriented ingestion and retrieval foundation: PDF inspection with PyMuPDF, page-level provenance JSONL, conservative bilingual parsing, deterministic cleanup, section-aware chunking, local Sentence Transformers embeddings, FAISS persistence, and manifest-validated retrieval. It deliberately does **not** include a chatbot, LLM calls, legal advice generation, or document drafting.

## Setup and run

```powershell
# Use Python 3.11: faiss-cpu's Windows DLL is not reliable on Python 3.13.
& "C:\Users\USER\AppData\Local\Programs\Python\Python311\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/inspect_documents.py
python scripts/parse_documents.py
python scripts/build_index.py
python scripts/test_retrieval.py
python -m pytest
```

Create `E:\Projects\AI Lawyer\.env` (not `.env.example` and not inside `.venv`) before launching the app. Its variable name must exactly match `llm.api_key_env` in `config/settings.yaml`.

To save unedited multilingual retrieval evaluation outputs after indexing:

```powershell
python scripts/evaluate_retrieval.py
```

Before building the index, set `embeddings.model_id` in `config/settings.yaml` to your approved Sentence Transformers model. Configure its cache/device/prefixes there as needed. The code refuses to build or query without it, and changing it requires rebuilding the index.

The supplied PDFs are configured from `Data/`, because that is the location currently present in this workspace. Change `pdf_processing.input_directory` to use `data/raw/` if you move them. The parser retains mixed Hindi/English pages and flags them instead of guessing translation boundaries.

## Phase 2: generation providers

The LLM layer is implemented but disabled by default. Configure `llm.provider`, `llm.model`, `llm.api_key_env`, and optionally `llm.api_base_url`; set the named key only in `.env`, never in YAML. The supported provider values are `gemini` and `openai_compatible`. `src/llm/` supplies one interface, timeout/retry behavior, a versioned system prompt, and Pydantic JSON-response validation for later case-management and RAG stages.
