from pathlib import Path
from collections import Counter

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.document_loader import (
    SUPPORTED_EXTENSIONS,
    load_file,
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

KNOWLEDGE_BASE_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "ABES_RAG_Knowledge_Base_2026"
)


# ============================================================
# ALLOWED KNOWLEDGE-BASE DIRECTORIES
# ============================================================

ALLOWED_DIRECTORIES = {
    "academics",
    "examinations",
    "faculty_navigation",
    "fees",
    "policies_notices",
    "student_services",
    "university",
}


# ============================================================
# DOCUMENT METADATA
# ============================================================

def create_document_id(relative_path: Path) -> str:
    """
    Create a stable document identifier from the
    document's relative path.
    """

    return (
        str(relative_path.with_suffix(""))
        .replace("\\", "_")
        .replace("/", "_")
        .replace(" ", "_")
        .replace("-", "_")
        .upper()
    )


def get_document_type(category: str) -> str:
    """
    Convert a knowledge-base category into a
    standardized document type.
    """

    category_types = {
        "academics": "ACADEMIC_INFORMATION",
        "examinations": "EXAMINATION_INFORMATION",
        "faculty_navigation": "FACULTY_NAVIGATION",
        "fees": "FEES_INFORMATION",
        "policies_notices": "POLICY_OR_NOTICE",
        "student_services": "STUDENT_SERVICES",
        "university": "UNIVERSITY_INFORMATION",
    }

    return category_types.get(
        category,
        "GENERAL_UNIVERSITY_INFORMATION",
    )


# ============================================================
# FILE DISCOVERY
# ============================================================

def discover_files() -> list[Path]:
    """
    Find all supported files that belong to the
    student-facing knowledge base.
    """

    files = []

    for directory_name in ALLOWED_DIRECTORIES:

        directory = KNOWLEDGE_BASE_DIR / directory_name

        if not directory.exists():
            continue

        for file_path in directory.rglob("*"):

            if (
                file_path.is_file()
                and file_path.suffix.lower()
                in SUPPORTED_EXTENSIONS
            ):
                files.append(file_path)

    return sorted(files)


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

def load_knowledge_base() -> list[Document]:
    """
    Load all supported knowledge-base files and
    enrich them with project-level metadata.
    """

    documents = []

    files = discover_files()

    for file_path in files:

        try:

            loaded_documents = load_file(file_path)

        except Exception as error:

            print(
                f"\n[ERROR] Failed to load: "
                f"{file_path.name}"
            )

            print(
                f"Reason: {error}"
            )

            continue

        relative_path = file_path.relative_to(
            KNOWLEDGE_BASE_DIR
        )

        category = relative_path.parts[0]

        document_id = create_document_id(
            relative_path
        )

        document_type = get_document_type(
            category
        )

        for document in loaded_documents:

            document.metadata.update(
                {
                    "document_id": document_id,
                    "category": category,
                    "document_type": document_type,
                    "document_name": file_path.name,
                    "relative_source": str(
                        relative_path
                    ),
                    "knowledge_status": "OFFICIAL_PUBLIC",
                }
            )

            documents.append(document)

    return documents


# ============================================================
# DOCUMENT CHUNKING
# ============================================================

def split_documents(
    documents: list[Document],
) -> list[Document]:
    """
    Split loaded documents into retrieval-friendly chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    return splitter.split_documents(
        documents
    )


# ============================================================
# CHUNK STATISTICS
# ============================================================

def print_chunk_statistics(
    chunks: list[Document],
) -> None:
    """
    Print statistics describing the generated chunks.
    """

    print("\n--- CHUNK STATISTICS ---")

    if not chunks:

        print("No chunks were created.")

        return

    chunk_lengths = [
        len(chunk.page_content)
        for chunk in chunks
    ]

    minimum = min(chunk_lengths)
    maximum = max(chunk_lengths)

    average = (
        sum(chunk_lengths)
        / len(chunk_lengths)
    )

    very_small = sum(
        length <= 200
        for length in chunk_lengths
    )

    small = sum(
        201 <= length <= 500
        for length in chunk_lengths
    )

    normal = sum(
        501 <= length <= 1000
        for length in chunk_lengths
    )

    oversized = sum(
        length > 1000
        for length in chunk_lengths
    )

    print(
        f"Minimum chunk length : {minimum}"
    )

    print(
        f"Maximum chunk length : {maximum}"
    )

    print(
        f"Average chunk length : {average:.2f}"
    )

    print(
        f"Chunks <= 200 chars  : {very_small}"
    )

    print(
        f"Chunks 201-500 chars  : {small}"
    )

    print(
        f"Chunks 501-1000 chars : {normal}"
    )

    print(
        f"Chunks > 1000 chars   : {oversized}"
    )


# ============================================================
# FILE-TYPE STATISTICS
# ============================================================

def print_file_type_statistics(
    chunks: list[Document],
) -> None:
    """
    Print the number of chunks generated
    from each file type.
    """

    print("\n--- CHUNKS PER FILE TYPE ---")

    file_type_counts = Counter(
        chunk.metadata.get(
            "file_type",
            "unknown",
        )
        for chunk in chunks
    )

    if not file_type_counts:

        print("No file-type information available.")

        return

    for file_type, count in sorted(
        file_type_counts.items()
    ):

        print(
            f"{file_type}: {count}"
        )


# ============================================================
# CATEGORY STATISTICS
# ============================================================

def print_category_statistics(
    chunks: list[Document],
) -> None:
    """
    Print the number of chunks generated
    from each knowledge-base category.
    """

    print("\n--- CHUNKS PER CATEGORY ---")

    category_counts = Counter(
        chunk.metadata.get(
            "category",
            "unknown",
        )
        for chunk in chunks
    )

    if not category_counts:

        print("No category information available.")

        return

    for category, count in sorted(
        category_counts.items()
    ):

        print(
            f"{category}: {count}"
        )


# ============================================================
# MAIN PIPELINE
# ============================================================

def main() -> None:

    print("=" * 60)
    print("ABES KNOWLEDGE BASE INGESTION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Discover files
    # --------------------------------------------------------

    files = discover_files()

    print(
        f"\nFiles discovered: {len(files)}"
    )

    # --------------------------------------------------------
    # 2. Load documents
    # --------------------------------------------------------

    documents = load_knowledge_base()

    print(
        f"Documents loaded: {len(documents)}"
    )

    # --------------------------------------------------------
    # 3. Split documents
    # --------------------------------------------------------

    chunks = split_documents(
        documents
    )

    print(
        f"Chunks created: {len(chunks)}"
    )

    # --------------------------------------------------------
    # 4. Statistics
    # --------------------------------------------------------

    print_chunk_statistics(
        chunks
    )

    print_file_type_statistics(
        chunks
    )

    print_category_statistics(
        chunks
    )

    # --------------------------------------------------------
    # 5. Sample chunk
    # --------------------------------------------------------

    if chunks:

        print("\n--- SAMPLE CHUNK ---")

        print(
            chunks[0].page_content[:1000]
        )

        print("\n--- METADATA ---")

        print(
            chunks[0].metadata
        )

    # --------------------------------------------------------
    # 6. Completion
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("INGESTION COMPLETED")
    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()