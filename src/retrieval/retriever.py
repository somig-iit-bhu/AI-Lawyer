"""Strict manifest-validated dense retrieval over legal chunks."""
from __future__ import annotations
import json
import re
from pathlib import Path
import numpy as np
from .embeddings import SentenceTransformerEmbedder
from .vector_store import load_index

class LegalRetriever:
    def __init__(self, settings) -> None:
        self.settings = settings
        manifest_path = settings.resolve_path(settings.vector_store.manifest_path)
        if not manifest_path.exists(): raise FileNotFoundError("Index manifest is missing. Run scripts/build_index.py.")
        self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self._validate_manifest()
        self.index = load_index(settings.resolve_path(settings.vector_store.index_path))
        metadata_path = settings.resolve_path(settings.vector_store.metadata_path)
        with metadata_path.open("r", encoding="utf-8") as file: self.metadata = [json.loads(line) for line in file if line.strip()]
        if self.index.ntotal != len(self.metadata): raise RuntimeError("FAISS index and metadata row counts differ. Rebuild the index.")
        if self.index.d != self.manifest["embedding_dimensions"]: raise RuntimeError("FAISS dimension does not match manifest. Rebuild the index.")
        self.embedder = SentenceTransformerEmbedder(settings.embeddings)
        self._bm25 = None
        if settings.retrieval.hybrid_enabled:
            try:
                from rank_bm25 import BM25Okapi
            except ImportError as error:
                raise RuntimeError("rank-bm25 is required when retrieval.hybrid_enabled is true.") from error
            self._bm25 = BM25Okapi([self._tokens(item["text"]) for item in self.metadata])

    def _validate_manifest(self) -> None:
        expected = {"embedding_model_id": self.settings.embeddings.model_id, "normalize": self.settings.embeddings.normalize, "query_prefix": self.settings.embeddings.query_prefix, "passage_prefix": self.settings.embeddings.passage_prefix, "chunking": self.settings.chunking.model_dump()}
        mismatch = [key for key, value in expected.items() if self.manifest.get(key) != value]
        if mismatch: raise RuntimeError(f"Index configuration mismatch ({', '.join(mismatch)}). Rebuild using scripts/build_index.py.")

    def search(self, query: str, limit: int | None = None) -> list[dict]:
        if not query.strip(): raise ValueError("A retrieval query cannot be blank.")
        top_k = min(limit or self.settings.retrieval.final_top_k, self.settings.retrieval.dense_top_k)
        candidate_count = min(self.settings.retrieval.dense_top_k, len(self.metadata))
        scores, vector_ids = self.index.search(self.embedder.encode_queries([query]), candidate_count)
        dense_scores = {int(vector_id): float(score) for score, vector_id in zip(scores[0], vector_ids[0]) if vector_id >= 0}
        if self._bm25:
            lexical = self._bm25.get_scores(self._tokens(query))
            candidate_ids = set(dense_scores) | set(np.argpartition(lexical, -candidate_count)[-candidate_count:])
            min_score, max_score = float(np.min(lexical)), float(np.max(lexical))
            ranked = []
            for vector_id in candidate_ids:
                dense = dense_scores.get(vector_id, 0.0)
                lexical_normalized = 0.0 if max_score == min_score else float((lexical[vector_id] - min_score) / (max_score - min_score))
                combined = self.settings.retrieval.dense_weight * dense + self.settings.retrieval.lexical_weight * lexical_normalized
                ranked.append((combined, dense, vector_id))
            ranked.sort(reverse=True)
        else:
            ranked = [(score, score, vector_id) for vector_id, score in dense_scores.items()]
            ranked.sort(reverse=True)
        results = []
        for combined_score, dense_score, vector_id in ranked:
            if self.settings.retrieval.min_similarity is not None and dense_score < self.settings.retrieval.min_similarity: continue
            result = dict(self.metadata[int(vector_id)])
            result["similarity"] = dense_score
            result["hybrid_score"] = combined_score
            results.append(result)
            if len(results) == top_k: break
        return results

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return re.findall(r"\w+", text.lower(), flags=re.UNICODE)
