"""Persistent FAISS vector-store construction and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.rag.embeddings import (
    generate_embeddings,
    get_embedding_dimension,
    load_chunks,
    load_embedding_model,
    validate_embeddings,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "vector_store"
FAISS_INDEX_PATH = VECTOR_STORE_DIR / "abes_knowledge.index"
METADATA_PATH = VECTOR_STORE_DIR / "chunk_metadata.json"
TOP_K = 5


def ensure_storage_directory() -> None:
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)


def prepare_metadata(chunks: list[Any]) -> list[dict[str, Any]]:
    return [
        {
            "vector_position": position,
            "chunk_id": chunk.metadata["chunk_id"],
            "text": chunk.page_content,
            "metadata": dict(chunk.metadata),
        }
        for position, chunk in enumerate(chunks)
    ]


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    if embeddings.ndim != 2 or embeddings.shape[0] == 0:
        raise ValueError(f"Expected a non-empty 2D embedding matrix, got {embeddings.shape}.")
    vectors = np.ascontiguousarray(embeddings, dtype=np.float32)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index


def save_faiss_index(index: faiss.Index) -> None:
    ensure_storage_directory()
    faiss.write_index(index, str(FAISS_INDEX_PATH))


def save_metadata(records: list[dict[str, Any]]) -> None:
    ensure_storage_directory()
    with METADATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)


def load_faiss_index() -> faiss.Index:
    if not FAISS_INDEX_PATH.exists():
        raise FileNotFoundError(f"FAISS index not found: {FAISS_INDEX_PATH}")
    return faiss.read_index(str(FAISS_INDEX_PATH))


def load_metadata() -> list[dict[str, Any]]:
    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Vector metadata not found: {METADATA_PATH}")
    with METADATA_PATH.open("r", encoding="utf-8") as file:
        records = json.load(file)
    if not isinstance(records, list):
        raise RuntimeError("Vector metadata must contain a JSON list.")
    return records


def validate_persisted_store(
    index: faiss.Index,
    metadata_records: list[dict[str, Any]],
    expected_dimension: int,
) -> None:
    if index.ntotal != len(metadata_records):
        raise RuntimeError("FAISS vector count does not match metadata record count.")
    if index.d != expected_dimension:
        raise RuntimeError("FAISS dimension does not match embedding dimension.")

    expected_positions = list(range(len(metadata_records)))
    actual_positions = [record.get("vector_position") for record in metadata_records]
    if actual_positions != expected_positions:
        raise RuntimeError("Vector positions are not sequential or correctly aligned.")

    chunk_ids = [record.get("chunk_id") for record in metadata_records]
    if not all(chunk_ids) or len(chunk_ids) != len(set(chunk_ids)):
        raise RuntimeError("Persisted chunk IDs are missing or duplicated.")

    for record in metadata_records:
        if not str(record.get("text", "")).strip():
            raise RuntimeError(f"Empty persisted text for chunk {record.get('chunk_id')}.")
        if not isinstance(record.get("metadata"), dict):
            raise RuntimeError(f"Invalid metadata mapping for chunk {record.get('chunk_id')}.")


def build_vector_store() -> None:
    ensure_storage_directory()
    model = load_embedding_model()
    dimension = get_embedding_dimension(model)
    chunks = load_chunks()
    embeddings = generate_embeddings(model, chunks)
    validate_embeddings(chunks, embeddings, dimension)

    matrix = np.asarray(embeddings, dtype=np.float32)
    index = build_faiss_index(matrix)
    metadata_records = prepare_metadata(chunks)

    save_faiss_index(index)
    save_metadata(metadata_records)

    reloaded_index = load_faiss_index()
    reloaded_metadata = load_metadata()
    validate_persisted_store(reloaded_index, reloaded_metadata, dimension)

    print(f"Vectors indexed: {reloaded_index.ntotal}")
    print(f"Index dimension: {reloaded_index.d}")
    print("VECTOR STORE CREATION COMPLETED")


if __name__ == "__main__":
    build_vector_store()
