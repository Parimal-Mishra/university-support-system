"""BGE-M3 embedding utilities for the ABES RAG pipeline."""

from __future__ import annotations

from typing import Any

from sentence_transformers import SentenceTransformer

from app.rag.ingest import build_chunks

EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
BATCH_SIZE = 8


def load_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_text(model: SentenceTransformer, text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Cannot generate an embedding for empty text.")
    vector = model.encode(text.strip(), normalize_embeddings=True)
    return vector.tolist()


def embed_documents(model: SentenceTransformer, texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    vectors = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return vectors.tolist()


def get_embedding_dimension(model: SentenceTransformer) -> int:
    dimension = model.get_embedding_dimension()
    if dimension is None:
        raise RuntimeError("Unable to determine embedding dimension.")
    return int(dimension)


def load_chunks():
    return build_chunks()


def validate_embeddings(
    chunks: list[Any],
    embeddings: list[list[float]],
    expected_dimension: int,
) -> None:
    if len(embeddings) != len(chunks):
        raise RuntimeError("Embedding count does not match chunk count.")
    if expected_dimension <= 0:
        raise ValueError("Embedding dimension must be positive.")

    chunk_ids = [chunk.metadata.get("chunk_id") for chunk in chunks]
    if len(chunk_ids) != len(set(chunk_ids)):
        raise RuntimeError("Duplicate chunk IDs detected during embedding validation.")

    for index, embedding in enumerate(embeddings):
        if len(embedding) != expected_dimension:
            raise RuntimeError(
                f"Embedding {index} has dimension {len(embedding)}; expected {expected_dimension}."
            )
        if not all(isinstance(value, (float, int)) for value in embedding):
            raise RuntimeError(f"Embedding {index} contains a non-numeric value.")


def generate_embeddings(model: SentenceTransformer, chunks: list[Any]) -> list[list[float]]:
    texts = [chunk.page_content for chunk in chunks]
    return embed_documents(model, texts)


def main() -> None:
    model = load_embedding_model()
    dimension = get_embedding_dimension(model)
    chunks = load_chunks()
    embeddings = generate_embeddings(model, chunks)
    validate_embeddings(chunks, embeddings, dimension)
    print(f"Model: {EMBEDDING_MODEL_NAME}")
    print(f"Chunks: {len(chunks)}")
    print(f"Embeddings: {len(embeddings)}")
    print(f"Dimensions: {dimension}")
    print("EMBEDDING GENERATION COMPLETED")


if __name__ == "__main__":
    main()
