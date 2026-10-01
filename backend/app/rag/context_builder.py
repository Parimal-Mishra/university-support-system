"""Convert ranked retrieval results into controlled LLM evidence context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.rag.retriever import ABESRetriever, RetrievalResult

MAX_CONTEXT_CHUNKS = 5
MAX_CHARS_PER_CHUNK = 2500


@dataclass(frozen=True)
class ContextSource:
    source_number: int
    rank: int
    score: float
    chunk_id: str
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ConstructedContext:
    query: str
    sources: list[ContextSource]
    context_text: str
    has_evidence: bool
    source_count: int


class ContextBuilder:
    def __init__(
        self,
        max_chunks: int = MAX_CONTEXT_CHUNKS,
        max_chars_per_chunk: int = MAX_CHARS_PER_CHUNK,
    ) -> None:
        if max_chunks <= 0:
            raise ValueError("max_chunks must be greater than zero.")
        if max_chars_per_chunk <= 0:
            raise ValueError("max_chars_per_chunk must be greater than zero.")
        self.max_chunks = max_chunks
        self.max_chars_per_chunk = max_chars_per_chunk

    @staticmethod
    def _clean_text(text: str) -> str:
        return "\n".join(line.strip() for line in text.splitlines() if line.strip()).strip()

    def _prepare_text(self, text: str) -> str:
        cleaned = self._clean_text(text)
        if len(cleaned) <= self.max_chars_per_chunk:
            return cleaned
        return cleaned[: self.max_chars_per_chunk].rstrip() + "\n[Source text truncated]"

    def _build_source(self, result: RetrievalResult, number: int) -> ContextSource | None:
        text = self._prepare_text(result.text)
        if not text:
            return None
        return ContextSource(
            source_number=number,
            rank=result.rank,
            score=result.score,
            chunk_id=result.chunk_id,
            text=text,
            metadata=dict(result.metadata),
        )

    @staticmethod
    def _metadata_value(metadata: dict[str, Any], *keys: str, default: str = "N/A") -> str:
        for key in keys:
            value = metadata.get(key)
            if value is not None and str(value).strip():
                return str(value)
        return default

    def _format_context(self, sources: list[ContextSource]) -> str:
        sections: list[str] = []
        for source in sources:
            metadata = source.metadata
            title = self._metadata_value(metadata, "document_title", "title", "document_name", default="Unknown document")
            document_type = self._metadata_value(metadata, "document_type", default="Unknown")
            department = self._metadata_value(metadata, "department", default="N/A")
            source_name = self._metadata_value(metadata, "relative_source", "source", default="N/A")
            sections.append(
                f"[SOURCE {source.source_number}]\n"
                f"Title: {title}\n"
                f"Document Type: {document_type}\n"
                f"Department: {department}\n"
                f"Chunk ID: {source.chunk_id}\n"
                f"Retrieval Score: {source.score:.6f}\n"
                f"Source: {source_name}\n"
                f"Content:\n{source.text}"
            )
        return "\n\n" + ("\n" + "-" * 60 + "\n").join(sections) if sections else ""

    def build(self, query: str, retrieval_results: list[RetrievalResult]) -> ConstructedContext:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        sources: list[ContextSource] = []
        for result in retrieval_results[: self.max_chunks]:
            source = self._build_source(result, len(sources) + 1)
            if source is not None:
                sources.append(source)

        context_text = self._format_context(sources)
        return ConstructedContext(
            query=query.strip(),
            sources=sources,
            context_text=context_text,
            has_evidence=bool(sources),
            source_count=len(sources),
        )


def main() -> None:
    retriever = ABESRetriever()
    builder = ContextBuilder()
    context = builder.build("What is the academic calendar?", retriever.retrieve("What is the academic calendar?"))
    if not context.has_evidence:
        raise RuntimeError("Context construction produced no evidence.")
    print(f"Sources included: {context.source_count}")
    print("CONTEXT CONSTRUCTION COMPLETED")


if __name__ == "__main__":
    main()
