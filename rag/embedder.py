import os
import numpy as np
from huggingface_hub import InferenceClient

HF_TOKEN    = os.getenv("HF_TOKEN", "")
EMBED_MODEL = "BAAI/bge-m3"

_embed_client = InferenceClient(provider="hf-inference", api_key=HF_TOKEN)


def embed_texts(texts: list[str]) -> np.ndarray:
    """텍스트 리스트 → (N, 1024) float32, L2 정규화 적용"""
    embeddings = []
    for text in texts:
        result = _embed_client.feature_extraction(
            text[:512],
            model=EMBED_MODEL,
        )
        vec = np.array(result, dtype=np.float32)
        if vec.ndim > 1:
            vec = vec.mean(axis=0)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        embeddings.append(vec)
    return np.stack(embeddings)


def embed_query(query: str) -> np.ndarray:
    """단일 쿼리 → 1D 벡터 (1024,)"""
    return embed_texts([query])[0]
