"""Local Sentence Transformers embedding adapter."""
from __future__ import annotations
import numpy as np

class SentenceTransformerEmbedder:
    def __init__(self, settings) -> None:
        if not settings.model_id:
            raise ValueError("embeddings.model_id is empty. Set it in config/settings.yaml before building or querying an index.")
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise RuntimeError("sentence-transformers is required. Install requirements.txt.") from error
        self.settings = settings
        model_source = settings.model_id
        if settings.local_files_only:
            try:
                from huggingface_hub import snapshot_download
            except ImportError as error:
                raise RuntimeError("huggingface-hub is required to resolve a cached embedding model.") from error
            model_source = snapshot_download(
                repo_id=settings.model_id,
                cache_dir=settings.cache_folder,
                local_files_only=True,
            )
        self.model = SentenceTransformer(
            model_source,
            cache_folder=settings.cache_folder,
            device=settings.device,
            trust_remote_code=settings.trust_remote_code,
            local_files_only=settings.local_files_only,
        )

    def encode_passages(self, passages: list[str]) -> np.ndarray:
        return self._encode([f"{self.settings.passage_prefix}{item}" for item in passages])

    def encode_queries(self, queries: list[str]) -> np.ndarray:
        return self._encode([f"{self.settings.query_prefix}{item}" for item in queries])

    def _encode(self, texts: list[str]) -> np.ndarray:
        vectors = self.model.encode(texts, batch_size=self.settings.batch_size, normalize_embeddings=self.settings.normalize, convert_to_numpy=True, show_progress_bar=False)
        return np.ascontiguousarray(vectors, dtype=np.float32)
