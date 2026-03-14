import numpy as np
from unittest.mock import patch


def test_embed_texts_returns_correct_shape():
    """N개 텍스트 → (N, 1024) float32 배열"""
    fake_vec = [[0.1] * 1024]
    with patch("rag.embedder._embed_client") as mock_client:
        mock_client.feature_extraction.return_value = fake_vec
        from rag.embedder import embed_texts
        result = embed_texts(["hello", "world"])
        assert result.shape == (2, 1024)
        assert result.dtype == np.float32


def test_embed_texts_is_l2_normalized():
    """각 벡터의 L2 노름 ≈ 1.0"""
    fake_vec = [[0.1] * 1024]
    with patch("rag.embedder._embed_client") as mock_client:
        mock_client.feature_extraction.return_value = fake_vec
        from rag.embedder import embed_texts
        result = embed_texts(["test"])
        norm = np.linalg.norm(result[0])
        assert abs(norm - 1.0) < 1e-5


def test_embed_query_returns_1d():
    """단일 쿼리 → 1D 벡터 (1024,)"""
    fake_vec = [[0.1] * 1024]
    with patch("rag.embedder._embed_client") as mock_client:
        mock_client.feature_extraction.return_value = fake_vec
        from rag.embedder import embed_query
        result = embed_query("비자 추천")
        assert result.shape == (1024,)
