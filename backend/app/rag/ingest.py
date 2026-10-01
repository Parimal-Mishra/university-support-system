"""Knowledge-base discovery, normalization, chunking and validation."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.document_loader import SUPPORTED_EXTENSIONS, load_file

PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "data" / "raw" / "ABES_RAG_Knowledge_Base_2026"

ALLOWED_DIRECTORIES = {
    "academics", "examinations", "faculty_navigation", "fees",
    "policies_notices", "student_services", "university",
}

REQUIRED_METADATA_FIELDS = [
    "document_id", "category", "document_type", "document_name",
    "relative_source", "knowledge_status", "chunk_id",
]

DOCUMENT_TYPES = {
    "academics": "ACADEMIC_INFORMATION",
    "examinations": "EXAMINATION_INFORMATION",
    "faculty_navigation": "FACULTY_NAVIGATION",
    "fees": "FEES_INFORMATION",
    "policies_notices": "POLICY_OR_NOTICE",
    "student_services": "STUDENT_SERVICES",
    "university": "UNIVERSITY_INFORMATION",
}

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def create_document_id(relative_path: Path) -> str:
    """Create a stable ID from the full relative path, including extension."""
    value = str(relative_path).replace("\\", "_").replace("/", "_")
    for character in (" ", "-", "."):
        value = value.replace(character, "_")
    return value.upper()


def get_document_type(category: str) -> str:
    return DOCUMENT_TYPES.get(category, "GENERAL_UNIVERSITY_INFORMATION")


def _display_title(file_name: str) -> str:
    """Create a human-readable title from the filename without inventing content."""
    return Path(file_name).stem.replace("_", " ").replace("-", " ").strip().title()


def discover_files() -> list[Path]:
    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(f"Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}")

    files: list[Path] = []
    for category_dir in sorted(KNOWLEDGE_BASE_DIR.iterdir()):
        if not category_dir.is_dir() or category_dir.name not in ALLOWED_DIRECTORIES:
            continue
        files.extend(
            path for path in category_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )
    return sorted(files)


def load_knowledge_base() -> list[Document]:
    """Load all approved knowledge-base files and attach stable metadata."""
    documents: list[Document] = []
    for file_path in discover_files():
        loaded = load_file(file_path)
        relative_path = file_path.relative_to(KNOWLEDGE_BASE_DIR)
        category = relative_path.parts[0]
        base_metadata = {
            "document_id": create_document_id(relative_path),
            "category": category,
            "document_type": get_document_type(category),
            "document_name": file_path.name,
            "document_title": _display_title(file_path.name),
            "relative_source": str(relative_path),
            "knowledge_status": "OFFICIAL_PUBLIC",
        }
        for document in loaded:
            document.metadata.update(base_metadata)
            documents.append(document)
    return documents


def normalize_documents(documents: list[Document]) -> list[Document]:
    """Normalize whitespace while preserving document metadata and meaning."""
    normalized: list[Document] = []
    for document in documents:
        text = document.page_content.replace("\r\n", "\n").replace("\r", "\n")
        lines: list[str] = []
        previous_blank = False
        for raw_line in text.split("\n"):
            line = raw_line.rstrip()
            if not line.strip():
                if previous_blank:
                    continue
                previous_blank = True
                lines.append("")
            else:
                previous_blank = False
                lines.append(line.strip())
        cleaned = "\n".join(lines).strip()
        if cleaned:
            normalized.append(Document(page_content=cleaned, metadata=dict(document.metadata)))
    return normalized


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def add_chunk_ids(chunks: list[Document]) -> list[Document]:
    counters: Counter[str] = Counter()
    for chunk in chunks:
        document_id = chunk.metadata.get("document_id")
        if not document_id:
            raise ValueError("Chunk is missing document_id before chunk ID creation.")
        counters[document_id] += 1
        chunk.metadata["chunk_id"] = f"{document_id}_C{counters[document_id]:03d}"
    return chunks


def validate_chunks(chunks: list[Document]) -> None:
    if not chunks:
        raise RuntimeError("No chunks were generated.")
    missing = [i for i, c in enumerate(chunks) if not c.metadata.get("chunk_id")]
    empty = [i for i, c in enumerate(chunks) if not c.page_content.strip()]
    ids = [c.metadata.get("chunk_id") for c in chunks]
    duplicates = [chunk_id for chunk_id, count in Counter(ids).items() if count > 1]
    if missing:
        raise RuntimeError(f"Chunks missing chunk_id: {missing[:10]}")
    if empty:
        raise RuntimeError(f"Empty chunks found: {empty[:10]}")
    if duplicates:
        raise RuntimeError(f"Duplicate chunk IDs found: {duplicates[:10]}")

    metadata_result = validate_required_metadata(chunks)
    if not metadata_result["passed"]:
        raise RuntimeError(f"Required metadata validation failed: {metadata_result['errors'][:3]}")
    consistency = validate_metadata_consistency(chunks)
    if not consistency["passed"]:
        raise RuntimeError(f"Metadata consistency validation failed: {consistency['errors'][:3]}")


def validate_required_metadata(chunks: list[Document]) -> dict[str, Any]:
    errors = []
    for index, chunk in enumerate(chunks):
        missing = [field for field in REQUIRED_METADATA_FIELDS if not chunk.metadata.get(field)]
        if missing:
            errors.append({"chunk_index": index, "chunk_id": chunk.metadata.get("chunk_id"), "missing_fields": missing})
    return {"passed": not errors, "errors": errors}


def validate_empty_chunks(chunks: list[Document]) -> dict[str, Any]:
    errors = [
        {"chunk_index": i, "chunk_id": c.metadata.get("chunk_id")}
        for i, c in enumerate(chunks) if not c.page_content.strip()
    ]
    return {"passed": not errors, "errors": errors}


def validate_duplicate_chunk_ids(chunks: list[Document]) -> dict[str, Any]:
    ids = [c.metadata.get("chunk_id") for c in chunks]
    counts = Counter(ids)
    duplicates = {key: value for key, value in counts.items() if key and value > 1}
    missing = sum(value is None for value in ids)
    return {"passed": not duplicates and missing == 0, "duplicates": duplicates, "missing_ids": missing}


def validate_metadata_consistency(chunks: list[Document]) -> dict[str, Any]:
    fields = ["category", "document_type", "document_name", "document_title", "relative_source", "knowledge_status"]
    by_document: dict[str, dict[str, Any]] = {}
    errors = []
    for chunk in chunks:
        document_id = chunk.metadata.get("document_id")
        if not document_id:
            continue
        current = {field: chunk.metadata.get(field) for field in fields}
        previous = by_document.setdefault(document_id, current)
        differences = {
            field: {"first_value": previous.get(field), "current_value": current.get(field)}
            for field in fields if previous.get(field) != current.get(field)
        }
        if differences:
            errors.append({"document_id": document_id, "differences": differences})
    return {"passed": not errors, "errors": errors}


def get_chunk_statistics(chunks: list[Document]) -> dict[str, Any]:
    lengths = [len(c.page_content) for c in chunks]
    if not lengths:
        return {"count": 0}
    return {
        "count": len(lengths),
        "minimum": min(lengths),
        "maximum": max(lengths),
        "average": sum(lengths) / len(lengths),
        "at_most_200": sum(n <= 200 for n in lengths),
        "201_to_500": sum(201 <= n <= 500 for n in lengths),
        "501_to_1000": sum(501 <= n <= 1000 for n in lengths),
        "above_1000": sum(n > 1000 for n in lengths),
    }


def build_chunks() -> list[Document]:
    documents = normalize_documents(load_knowledge_base())
    chunks = add_chunk_ids(split_documents(documents))
    validate_chunks(chunks)
    return chunks


def main() -> None:
    files = discover_files()
    documents = load_knowledge_base()
    normalized = normalize_documents(documents)
    chunks = add_chunk_ids(split_documents(normalized))
    validate_chunks(chunks)
    stats = get_chunk_statistics(chunks)
    print(f"Files discovered: {len(files)}")
    print(f"Documents loaded: {len(documents)}")
    print(f"Documents after normalization: {len(normalized)}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Chunk statistics: {stats}")
    print("INGESTION PIPELINE COMPLETED")


if __name__ == "__main__":
    main()
