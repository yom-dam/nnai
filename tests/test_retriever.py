import numpy as np
from unittest.mock import patch
import faiss


def _make_fake_index(dim=1024, n=5):
    vecs = np.random.rand(n, dim).astype(np.float32)
    vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)
    index = faiss.IndexFlatIP(dim)
    index.add(vecs)
    return index


FAKE_DOCS = [
    {"id": f"doc_{i}", "text": f"텍스트 {i}", "metadata": {"type": "visa"}}
    for i in range(5)
]


def test_retrieve_returns_list_of_dicts():
    fake_index = _make_fake_index()
    fake_q_vec = np.random.rand(1024).astype(np.float32)
    fake_q_vec /= np.linalg.norm(fake_q_vec)

    with patch("rag.retriever.load_index", return_value=(fake_index, FAKE_DOCS)), \
         patch("rag.retriever.embed_query", return_value=fake_q_vec):
        import rag.retriever as r
        r._index = None
        r._docs  = None
        results = r.retrieve("비자 추천 쿼리", top_k=3)
        assert isinstance(results, list)
        assert len(results) == 3
        assert "score" in results[0]


def test_retrieve_as_context_returns_string():
    fake_index = _make_fake_index()
    fake_q_vec = np.random.rand(1024).astype(np.float32)
    fake_q_vec /= np.linalg.norm(fake_q_vec)

    with patch("rag.retriever.load_index", return_value=(fake_index, FAKE_DOCS)), \
         patch("rag.retriever.embed_query", return_value=fake_q_vec):
        import rag.retriever as r
        r._index = None
        r._docs  = None
        ctx = r.retrieve_as_context("테스트", top_k=2)
        assert isinstance(ctx, str)
        assert "RAG" in ctx
