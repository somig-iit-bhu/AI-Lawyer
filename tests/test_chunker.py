from src.config import ChunkingSettings, EmbeddingSettings
from src.ingestion.chunker import build_chunks

def test_chunks_are_stable_and_bounded():
    page = {"document_id": "doc", "source_checksum": "checksum", "source_file": "source.pdf", "page_number": 1, "document_title": "Title", "document_type": "act", "text": "Section 2. Definitions\n" + "consumer protection " * 500, "language": "en", "warnings": []}
    chunks = build_chunks([page], ChunkingSettings(), EmbeddingSettings(model_id=None))
    assert chunks == build_chunks([page], ChunkingSettings(), EmbeddingSettings(model_id=None))
    assert all(chunk["token_count"] <= 650 for chunk in chunks)
