"""Application service that orchestrates the ABES RAG pipeline."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.rag.context_builder import ContextBuilder, ConstructedContext
from app.rag.generator import ABESGenerator, GeneratedAnswer
from app.rag.grounding import ABESGrounder, GroundingResult
from app.rag.retriever import ABESRetriever, RetrievalResult


class RAGService:
    """Own long-lived RAG components and expose application-level operations."""

    def __init__(self) -> None:
        self.retriever = ABESRetriever()
        self.context_builder = ContextBuilder()
        self.generator = ABESGenerator()
        self.grounder = ABESGrounder()

    @staticmethod
    def _validate_query(query: str) -> str:
        cleaned = query.strip()
        if not cleaned:
            raise ValueError("Query cannot be empty.")
        if len(cleaned) > 2000:
            raise ValueError("Query cannot exceed 2000 characters.")
        return cleaned

    def retrieve(self, query: str) -> list[RetrievalResult]:
        cleaned = self._validate_query(query)
        return self.retriever.retrieve(cleaned)

    def answer(
        self,
        query: str,
    ) -> tuple[GeneratedAnswer, GroundingResult, ConstructedContext]:
        cleaned = self._validate_query(query)

        retrieval_results = self.retriever.retrieve(cleaned)
        context = self.context_builder.build(
            query=cleaned,
            retrieval_results=retrieval_results,
        )
        generated = self.generator.generate(
            query=cleaned,
            context=context,
        )
        grounding = self.grounder.validate(
            answer=generated,
            context=context,
        )
        return generated, grounding, context


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    """Create the RAG service once per backend process."""
    return RAGService()


def source_metadata(
    result: RetrievalResult,
    source_number: int,
) -> dict[str, Any]:
    metadata = result.metadata
    return {
        "source_number": source_number,
        "rank": result.rank,
        "score": result.score,
        "chunk_id": result.chunk_id,
        "document_name": str(metadata.get("document_name", "")),
        "document_title": str(
            metadata.get("document_title")
            or metadata.get("title")
            or metadata.get("document_name")
            or "Unknown document"
        ),
        "document_type": str(metadata.get("document_type", "")),
        "relative_source": str(metadata.get("relative_source", "")),
    }


def context_source_metadata(
    context: ConstructedContext,
) -> list[dict[str, Any]]:
    return [
        {
            "source_number": source.source_number,
            "rank": source.rank,
            "score": source.score,
            "chunk_id": source.chunk_id,
            "document_name": str(source.metadata.get("document_name", "")),
            "document_title": str(
                source.metadata.get("document_title")
                or source.metadata.get("title")
                or source.metadata.get("document_name")
                or "Unknown document"
            ),
            "document_type": str(source.metadata.get("document_type", "")),
            "relative_source": str(source.metadata.get("relative_source", "")),
        }
        for source in context.sources
    ]
