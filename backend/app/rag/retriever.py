"""Semantic retrieval from the persisted ABES FAISS vector store."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import faiss
import numpy as np

from app.rag.embeddings import embed_text, load_embedding_model
from app.rag.vector_store import TOP_K, load_faiss_index, load_metadata

DEFAULT_TOP_K = TOP_K
DEFAULT_SIMILARITY_THRESHOLD = 0.45


@dataclass(frozen=True)
class RetrievalResult:
    rank: int
    score: float
    vector_position: int
    chunk_id: str
    text: str
    metadata: dict[str, Any]


class ABESRetriever:
    def __init__(
        self,
        top_k: int = DEFAULT_TOP_K,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be between 0.0 and 1.0.")

        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.model = load_embedding_model()
        self.index = load_faiss_index()
        self.metadata_records = load_metadata()
        self._validate_store()

    def _validate_store(self) -> None:
        if self.index.ntotal <= 0:
            raise RuntimeError("FAISS index contains no vectors.")
        if self.index.ntotal != len(self.metadata_records):
            raise RuntimeError("FAISS and metadata counts are not aligned.")
        positions = [record.get("vector_position") for record in self.metadata_records]
        if positions != list(range(len(self.metadata_records))):
            raise RuntimeError("FAISS vector positions and metadata are not aligned.")
        for record in self.metadata_records:
            if not record.get("chunk_id") or not str(record.get("text", "")).strip():
                raise RuntimeError("Persisted vector metadata contains an invalid record.")

    def _embed_query(self, query: str) -> np.ndarray:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        vector = np.asarray(embed_text(self.model, query.strip()), dtype=np.float32)
        if vector.ndim != 1 or vector.shape[0] != self.index.d:
            raise RuntimeError("Query embedding dimension does not match FAISS index.")
        return vector.reshape(1, -1)

    def retrieve(self, query: str) -> list[RetrievalResult]:
        query_vector = self._embed_query(query)
        search_k = min(self.top_k, self.index.ntotal)
        scores, positions = self.index.search(query_vector, search_k)

        results: list[RetrievalResult] = []
        seen: set[str] = set()
        for score, position in zip(scores[0], positions[0]):
            position = int(position)
            score = float(score)
            if position < 0 or score < self.similarity_threshold:
                continue
            record = self.metadata_records[position]
            chunk_id = record["chunk_id"]
            if chunk_id in seen:
                continue
            seen.add(chunk_id)
            results.append(
                RetrievalResult(
                    rank=len(results) + 1,
                    score=score,
                    vector_position=position,
                    chunk_id=chunk_id,
                    text=record["text"],
                    metadata=dict(record["metadata"]),
                )
            )
        return results


def print_results(results: list[RetrievalResult]) -> None:
    if not results:
        print("[INFO] No chunks passed the similarity threshold.")
        return
    for result in results:
        print(
            f"Rank {result.rank} | score={result.score:.6f} | "
            f"chunk={result.chunk_id} | source={result.metadata.get('relative_source', 'N/A')}"
        )


def run_retrieval_tests(retriever: ABESRetriever) -> None:
    queries = [
        "What is the academic calendar?",
        "What are the examination rules?",
        "Where can I find student services?",
        "Where is a CSE faculty member's cabin?",
        "What programs and departments are available?",
    ]
    passed = 0
    for query in queries:
        results = retriever.retrieve(query)
        if results:
            passed += 1
        print(f"Query: {query}")
        print_results(results[:3])
    print(f"Retrieval tests with results: {passed}/{len(queries)}")


def main() -> None:
    retriever = ABESRetriever()
    run_retrieval_tests(retriever)
    print("RETRIEVAL ENGINE VALIDATION COMPLETED")


if __name__ == "__main__":
    main()
