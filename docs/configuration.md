# Configuration checklist

Use Python 3.11 to create the virtual environment. The observed Python 3.13 `faiss-cpu` wheel fails during native DLL initialization on this machine. Copy `.env.example` to `E:\Projects\AI Lawyer\.env`; never commit `.env`.

## Required for Phase 1 retrieval

In `config/settings.yaml`, set `embeddings.model_id` to the exact Sentence Transformers-compatible model identifier or local model path. Optionally set `cache_folder`, `device`, `batch_size`, prefixes, and `local_files_only`. Set `local_files_only: true` when model files are already cached and the machine should not contact Hugging Face. Build the index after changing any of these values.

## Required for Phase 2–6 generation

Set these `llm` values in `config/settings.yaml`:

| Setting | What to provide |
| --- | --- |
| `provider` | `gemini` or `openai_compatible` |
| `model` | The exact model ID accepted by your provider |
| `api_key_env` | The environment-variable name holding the secret |
| `api_base_url` | Required only when your OpenAI-compatible endpoint is not the default |
| `system_prompt_path` | Optional path to your versioned policy prompt |

Set the actual secret only in `.env`. For example, if `api_key_env: GEMINI_API_KEY`, add `GEMINI_API_KEY=...` to `.env`. For an OpenAI-compatible provider, you may instead use `OPENAI_COMPATIBLE_API_KEY=...` and configure that variable name.

## Optional legal-source metadata

Add manually verified filenames, titles, original URLs, document types, and legal statuses to `config/sources.yaml`. Do not put unverified URLs there.
