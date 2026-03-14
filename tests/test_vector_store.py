import os, pickle
import numpy as np
import faiss
from unittest.mock import patch


def _fake_embed(texts):
    n = len(texts)
    vecs = np.random.rand(n, 1024).astype(np.float32)
    vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs


def test_build_and_load_index(tmp_path, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "dummy")
    monkeypatch.setattr("rag.vector_store.INDEX_PATH", str(tmp_path / "index.faiss"))
    monkeypatch.setattr("rag.vector_store.DOCS_PATH",  str(tmp_path / "docs.pkl"))

    with patch("rag.vector_store.embed_texts", side_effect=_fake_embed), \
         patch("rag.vector_store._chunk_visa_db", return_value=[
             {"id":"test1","text":"말레이시아 비자 정보","metadata":{"type":"visa"}}
         ]), \
         patch("rag.vector_store._chunk_city_scores", return_value=[
             {"id":"test2","text":"쿠알라룸푸르 도시 정보","metadata":{"type":"city"}}
         ]):
        from rag.vector_store import build_index, load_index
        build_index(force=True)
        index, docs = load_index()
        assert index.ntotal == 2
        assert len(docs) == 2


def test_build_index_skip_if_exists(tmp_path, monkeypatch):
    monkeypatch.setattr("rag.vector_store.INDEX_PATH", str(tmp_path / "index.faiss"))
    monkeypatch.setattr("rag.vector_store.DOCS_PATH",  str(tmp_path / "docs.pkl"))
    (tmp_path / "index.faiss").touch()
    (tmp_path / "docs.pkl").touch()

    with patch("rag.vector_store.embed_texts") as mock_embed:
        from rag.vector_store import build_index
        build_index(force=False)
        mock_embed.assert_not_called()
