"""FAISS persistence with explicit dimensionality validation."""
from __future__ import annotations
from pathlib import Path
import numpy as np

def _faiss():
    try:
        import faiss
        return faiss
    except ImportError as error:
        raise RuntimeError("faiss-cpu is required. Install requirements.txt.") from error

def create_flat_ip(vectors: np.ndarray):
    if vectors.ndim != 2 or not len(vectors): raise ValueError("Expected a non-empty 2D embedding array.")
    index = _faiss().IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index

def save_index(index, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    _faiss().write_index(index, str(destination))

def load_index(source: Path):
    if not source.exists(): raise FileNotFoundError(f"FAISS index not found: {source}. Run scripts/build_index.py.")
    return _faiss().read_index(str(source))
