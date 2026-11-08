import numpy as np
import pytest
from src.retrieval.vector_store import create_flat_ip

def test_faiss_preserves_vector_count():
    pytest.importorskip("faiss")
    index = create_flat_ip(np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32))
    assert index.ntotal == 2
