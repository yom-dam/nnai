import numpy as np
from rag.embedder import embed_query
from rag.vector_store import load_index

_index = None
_docs  = None


def _ensure_loaded():
    global _index, _docs
    if _index is None:
        _index, _docs = load_index()


def retrieve(query: str, top_k: int = 6) -> list[dict]:
    _ensure_loaded()
    q_vec = embed_query(query).reshape(1, -1).astype(np.float32)
    scores, indices = _index.search(q_vec, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        doc = _docs[idx].copy()
        doc["score"] = float(score)
        results.append(doc)
    return results


def retrieve_as_context(query: str, top_k: int = 6) -> str:
    docs = retrieve(query, top_k=top_k)
    if not docs:
        return "관련 데이터를 찾지 못했습니다."
    lines = ["=== RAG 검색 결과 (관련 비자·도시 데이터) ==="]
    for i, doc in enumerate(docs, 1):
        lines.append(f"\n[{i}] {doc['text']}")
    return "\n".join(lines)
