from pathlib import Path
from collections import Counter

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.document_loader import SUPPORTED_EXTENSIONS, load_file


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
# ALLOWED KNOWLEDGE BASE DIRECTORIES
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
# REQUIRED METADATA
# ============================================================

REQUIRED_METADATA_FIELDS = [
    "document_id",
    "category",
    "document_type",
    "document_name",
    "relative_source",
    "knowledge_status",
    "chunk_id",
]


# ============================================================
# DOCUMENT ID
# ============================================================

def create_document_id(relative_path: Path) -> str:
    """
    Create a stable unique document ID from the relative file path.

    The file extension is preserved so that two different
    physical files with the same filename stem are not
    accidentally treated as the same document.

    Example:

        faculty_navigation/teacher_seating_plan.csv
        ->
        FACULTY_NAVIGATION_TEACHER_SEATING_PLAN_CSV

        faculty_navigation/teacher_seating_plan.md
        ->
        FACULTY_NAVIGATION_TEACHER_SEATING_PLAN_MD
    """

    document_id = str(relative_path)

    document_id = document_id.replace("\\", "_")
    document_id = document_id.replace("/", "_")
    document_id = document_id.replace(" ", "_")
    document_id = document_id.replace("-", "_")
    document_id = document_id.replace(".", "_")

    return document_id.upper()


# ============================================================
# DOCUMENT TYPE
# ============================================================

def get_document_type(category: str) -> str:
    """
    Convert knowledge-base category into a standardized
    document type.
    """

    mapping = {
        "academics": "ACADEMIC_INFORMATION",
        "examinations": "EXAMINATION_INFORMATION",
        "faculty_navigation": "FACULTY_NAVIGATION",
        "fees": "FEES_INFORMATION",
        "policies_notices": "POLICY_OR_NOTICE",
        "student_services": "STUDENT_SERVICES",
        "university": "UNIVERSITY_INFORMATION",
    }

    return mapping.get(
        category,
        "GENERAL_UNIVERSITY_INFORMATION",
    )


# ============================================================
# FILE DISCOVERY
# ============================================================

def discover_files() -> list[Path]:
    """
    Recursively discover all supported files inside the
    ABES knowledge base.

    Only files inside the approved knowledge-base
    categories are included.
    """

    discovered_files = []

    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge base directory not found:\n"
            f"{KNOWLEDGE_BASE_DIR}"
        )

    for category_dir in KNOWLEDGE_BASE_DIR.iterdir():

        if not category_dir.is_dir():
            continue

        if category_dir.name not in ALLOWED_DIRECTORIES:
            continue

        for file_path in category_dir.rglob("*"):

            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            discovered_files.append(file_path)

    return sorted(discovered_files)


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

def load_knowledge_base() -> list[Document]:
    """
    Load all supported documents from the knowledge base
    and attach standardized metadata.
    """

    files = discover_files()

    documents = []

    for file_path in files:

        try:
            loaded_documents = load_file(file_path)

        except Exception as exc:

            print(
                f"[ERROR] Failed to load: "
                f"{file_path.name}"
            )

            print(
                f"        {exc}"
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
# TEXT NORMALIZATION
# ============================================================

def normalize_documents(
    documents: list[Document],
) -> list[Document]:
    """
    Normalize document text before chunking.

    Operations:
    - Normalize line endings
    - Remove trailing whitespace
    - Remove excessive blank lines
    - Remove unnecessary leading/trailing whitespace
    - Preserve metadata
    - Skip completely empty documents
    """

    normalized_documents = []

    for document in documents:

        text = document.page_content

        # Normalize line endings.
        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        # Remove trailing whitespace.
        lines = [
            line.rstrip()
            for line in text.split("\n")
        ]

        cleaned_lines = []

        previous_blank = False

        for line in lines:

            if not line.strip():

                if previous_blank:
                    continue

                previous_blank = True

                cleaned_lines.append("")

            else:

                previous_blank = False

                cleaned_lines.append(
                    line.strip()
                )

        text = "\n".join(
            cleaned_lines
        ).strip()

        # Skip empty documents.
        if not text:
            continue

        normalized_documents.append(
            Document(
                page_content=text,
                metadata=dict(
                    document.metadata
                ),
            )
        )

    return normalized_documents


# ============================================================
# CHUNKING
# ============================================================

def split_documents(
    documents: list[Document],
) -> list[Document]:
    """
    Split documents into retrieval-friendly chunks.

    Current configuration:
        chunk_size    = 1000
        chunk_overlap = 150
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
# CHUNK IDs
# ============================================================

def add_chunk_ids(
    chunks: list[Document],
) -> list[Document]:
    """
    Assign stable sequential chunk IDs within each document.

    Example:

        ACADEMICS_ACADEMIC_CALENDAR_C001
        ACADEMICS_ACADEMIC_CALENDAR_C002
        ACADEMICS_ACADEMIC_CALENDAR_C003
    """

    counters = {}

    for chunk in chunks:

        document_id = chunk.metadata.get(
            "document_id",
            "UNKNOWN_DOCUMENT",
        )

        counters.setdefault(
            document_id,
            0,
        )

        counters[document_id] += 1

        chunk_number = counters[
            document_id
        ]

        chunk.metadata["chunk_id"] = (
            f"{document_id}_C{chunk_number:03d}"
        )

    return chunks


# ============================================================
# BASIC CHUNK ID VALIDATION
# ============================================================

def validate_chunk_ids(
    chunks: list[Document],
) -> None:
    """
    Validate that every chunk has a chunk ID
    and that chunk IDs are unique.
    """

    chunk_ids = [
        chunk.metadata.get(
            "chunk_id"
        )
        for chunk in chunks
    ]

    missing_ids = [
        chunk_id
        for chunk_id in chunk_ids
        if not chunk_id
    ]

    unique_ids = set(chunk_ids)

    print(
        "\n--- CHUNK ID VALIDATION ---"
    )

    print(
        f"Total chunk IDs : "
        f"{len(chunk_ids)}"
    )

    print(
        f"Unique chunk IDs: "
        f"{len(unique_ids)}"
    )

    print(
        f"Missing IDs     : "
        f"{len(missing_ids)}"
    )

    if len(chunk_ids) != len(unique_ids):

        print(
            "[WARNING] Duplicate chunk IDs detected."
        )

    elif missing_ids:

        print(
            "[WARNING] Some chunks do not have IDs."
        )

    else:

        print(
            "[OK] All chunk IDs are unique."
        )


# ============================================================
# CHUNK STATISTICS
# ============================================================

def print_chunk_statistics(
    chunks: list[Document],
) -> None:
    """
    Print statistics about generated chunks.
    """

    if not chunks:

        print(
            "\nNo chunks generated."
        )

        return

    lengths = [
        len(chunk.page_content)
        for chunk in chunks
    ]

    minimum = min(lengths)
    maximum = max(lengths)
    average = sum(lengths) / len(lengths)

    below_200 = sum(
        length <= 200
        for length in lengths
    )

    between_201_500 = sum(
        201 <= length <= 500
        for length in lengths
    )

    between_501_1000 = sum(
        501 <= length <= 1000
        for length in lengths
    )

    above_1000 = sum(
        length > 1000
        for length in lengths
    )

    print(
        "\n--- CHUNK STATISTICS ---"
    )

    print(
        f"Minimum chunk length : "
        f"{minimum}"
    )

    print(
        f"Maximum chunk length : "
        f"{maximum}"
    )

    print(
        f"Average chunk length : "
        f"{average:.2f}"
    )

    print(
        f"Chunks <= 200 chars  : "
        f"{below_200}"
    )

    print(
        f"Chunks 201-500 chars : "
        f"{between_201_500}"
    )

    print(
        f"Chunks 501-1000 chars: "
        f"{between_501_1000}"
    )

    print(
        f"Chunks > 1000 chars  : "
        f"{above_1000}"
    )


# ============================================================
# FILE TYPE STATISTICS
# ============================================================

def print_file_type_statistics(
    documents: list[Document],
) -> None:
    """
    Display the number of loaded documents by file type.
    """

    counter = Counter(
        document.metadata.get(
            "file_type",
            "unknown",
        )
        for document in documents
    )

    print(
        "\n--- DOCUMENTS PER FILE TYPE ---"
    )

    for file_type, count in sorted(
        counter.items()
    ):

        print(
            f"{file_type}: {count}"
        )


# ============================================================
# CATEGORY STATISTICS
# ============================================================

def print_category_statistics(
    documents: list[Document],
) -> None:
    """
    Display the number of loaded documents by
    knowledge-base category.
    """

    counter = Counter(
        document.metadata.get(
            "category",
            "unknown",
        )
        for document in documents
    )

    print(
        "\n--- DOCUMENTS PER CATEGORY ---"
    )

    for category, count in sorted(
        counter.items()
    ):

        print(
            f"{category}: {count}"
        )


# ============================================================
# FINAL VALIDATION
# ============================================================

def validate_required_metadata(
    chunks: list[Document],
) -> dict:
    """
    Check that every chunk contains all required metadata.
    """

    missing_metadata = []

    for index, chunk in enumerate(chunks):

        missing_fields = [
            field
            for field in REQUIRED_METADATA_FIELDS
            if not chunk.metadata.get(field)
        ]

        if missing_fields:

            missing_metadata.append(
                {
                    "chunk_index": index,
                    "chunk_id": chunk.metadata.get(
                        "chunk_id",
                        "UNKNOWN",
                    ),
                    "missing_fields": missing_fields,
                }
            )

    return {
        "passed": len(missing_metadata) == 0,
        "errors": missing_metadata,
    }


def validate_empty_chunks(
    chunks: list[Document],
) -> dict:
    """
    Check for empty or whitespace-only chunks.
    """

    empty_chunks = []

    for index, chunk in enumerate(chunks):

        if not chunk.page_content.strip():

            empty_chunks.append(
                {
                    "chunk_index": index,
                    "chunk_id": chunk.metadata.get(
                        "chunk_id",
                        "UNKNOWN",
                    ),
                }
            )

    return {
        "passed": len(empty_chunks) == 0,
        "errors": empty_chunks,
    }


def validate_duplicate_chunk_ids(
    chunks: list[Document],
) -> dict:
    """
    Check that every chunk ID is unique and present.
    """

    chunk_ids = [
        chunk.metadata.get(
            "chunk_id"
        )
        for chunk in chunks
    ]

    counts = Counter(chunk_ids)

    duplicates = {
        chunk_id: count
        for chunk_id, count in counts.items()
        if chunk_id and count > 1
    }

    missing_ids = sum(
        chunk_id is None
        for chunk_id in chunk_ids
    )

    return {
        "passed": (
            len(duplicates) == 0
            and missing_ids == 0
        ),
        "duplicates": duplicates,
        "missing_ids": missing_ids,
    }


def validate_metadata_consistency(
    chunks: list[Document],
) -> dict:
    """
    Check whether chunks belonging to the same document
    have consistent document-level metadata.

    Only genuine document-level fields are checked.
    Row-specific CSV metadata is intentionally ignored.
    """

    document_metadata = {}

    inconsistencies = []

    fields_to_check = [
        "category",
        "document_type",
        "document_name",
        "relative_source",
        "knowledge_status",
    ]

    for chunk in chunks:

        document_id = chunk.metadata.get(
            "document_id"
        )

        if not document_id:
            continue

        current_metadata = {
            field: chunk.metadata.get(
                field
            )
            for field in fields_to_check
        }

        if document_id not in document_metadata:

            document_metadata[
                document_id
            ] = current_metadata

            continue

        previous_metadata = (
            document_metadata[
                document_id
            ]
        )

        differences = {
            field: {
                "first_value": (
                    previous_metadata.get(
                        field
                    )
                ),
                "current_value": (
                    current_metadata.get(
                        field
                    )
                ),
            }
            for field in fields_to_check
            if previous_metadata.get(
                field
            )
            != current_metadata.get(
                field
            )
        }

        if differences:

            inconsistencies.append(
                {
                    "document_id": document_id,
                    "differences": differences,
                }
            )

    return {
        "passed": (
            len(inconsistencies) == 0
        ),
        "errors": inconsistencies,
    }


def print_document_chunk_distribution(
    chunks: list[Document],
) -> None:
    """
    Print the number of chunks generated for
    every document.
    """

    counter = Counter(
        chunk.metadata.get(
            "document_id",
            "UNKNOWN_DOCUMENT",
        )
        for chunk in chunks
    )

    print(
        "\n--- DOCUMENT → CHUNK DISTRIBUTION ---"
    )

    for document_id, count in sorted(
        counter.items()
    ):

        print(
            f"{document_id}: {count}"
        )


def run_final_validation(
    chunks: list[Document],
) -> bool:
    """
    Run all final ingestion validation checks.

    Returns:
        True  -> all checks passed
        False -> one or more checks failed
    """

    print("\n")
    print("=" * 60)
    print("FINAL INGESTION VALIDATION")
    print("=" * 60)

    all_passed = True

    # --------------------------------------------------------
    # 1. REQUIRED METADATA
    # --------------------------------------------------------

    metadata_result = (
        validate_required_metadata(
            chunks
        )
    )

    if metadata_result["passed"]:

        print(
            "[PASS] Required metadata"
        )

    else:

        print(
            "[FAIL] Required metadata"
        )

        for error in (
            metadata_result["errors"]
        ):

            print(
                f"       Chunk: "
                f"{error['chunk_id']}"
            )

            print(
                f"       Missing: "
                f"{', '.join(error['missing_fields'])}"
            )

        all_passed = False

    # --------------------------------------------------------
    # 2. EMPTY CHUNKS
    # --------------------------------------------------------

    empty_result = (
        validate_empty_chunks(
            chunks
        )
    )

    if empty_result["passed"]:

        print(
            "[PASS] No empty chunks"
        )

    else:

        print(
            "[FAIL] Empty chunks detected"
        )

        for error in (
            empty_result["errors"]
        ):

            print(
                f"       {error['chunk_id']}"
            )

        all_passed = False

    # --------------------------------------------------------
    # 3. DUPLICATE CHUNK IDs
    # --------------------------------------------------------

    duplicate_result = (
        validate_duplicate_chunk_ids(
            chunks
        )
    )

    if duplicate_result["passed"]:

        print(
            "[PASS] Chunk IDs are unique"
        )

    else:

        print(
            "[FAIL] Duplicate/missing chunk IDs"
        )

        if duplicate_result["missing_ids"]:

            print(
                f"       Missing IDs: "
                f"{duplicate_result['missing_ids']}"
            )

        for chunk_id, count in (
            duplicate_result[
                "duplicates"
            ].items()
        ):

            print(
                f"       Duplicate: "
                f"{chunk_id} "
                f"({count} times)"
            )

        all_passed = False

    # --------------------------------------------------------
    # 4. METADATA CONSISTENCY
    # --------------------------------------------------------

    consistency_result = (
        validate_metadata_consistency(
            chunks
        )
    )

    if consistency_result["passed"]:

        print(
            "[PASS] Metadata consistency"
        )

    else:

        print(
            "[FAIL] Metadata inconsistencies"
        )

        for error in (
            consistency_result[
                "errors"
            ]
        ):

            print(
                f"       {error['document_id']}"
            )

            print(
                "       Differences:"
            )

            for field, values in (
                error[
                    "differences"
                ].items()
            ):

                print(
                    f"           {field}:"
                )

                print(
                    f"               first   = "
                    f"{values['first_value']}"
                )

                print(
                    f"               current = "
                    f"{values['current_value']}"
                )

        all_passed = False

    # --------------------------------------------------------
    # 5. DOCUMENT / CHUNK COUNTS
    # --------------------------------------------------------

    document_ids = {
        chunk.metadata.get(
            "document_id"
        )
        for chunk in chunks
        if chunk.metadata.get(
            "document_id"
        )
    }

    print(
        f"[INFO] Unique documents: "
        f"{len(document_ids)}"
    )

    print(
        f"[INFO] Total chunks: "
        f"{len(chunks)}"
    )

    # --------------------------------------------------------
    # 6. DOCUMENT → CHUNK DISTRIBUTION
    # --------------------------------------------------------

    print_document_chunk_distribution(
        chunks
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    print(
        "\n" + "-" * 60
    )

    if all_passed:

        print(
            "[SUCCESS] FINAL INGESTION "
            "VALIDATION PASSED"
        )

    else:

        print(
            "[FAILED] FINAL INGESTION "
            "VALIDATION FAILED"
        )

    print(
        "-" * 60
    )

    return all_passed


# ============================================================
# MAIN PIPELINE
# ============================================================

def main() -> None:

    print("=" * 60)
    print("ABES KNOWLEDGE BASE INGESTION")
    print("=" * 60)

    # --------------------------------------------------------
    # STEP 1: DISCOVER FILES
    # --------------------------------------------------------

    files = discover_files()

    print(
        f"\nFiles discovered: "
        f"{len(files)}"
    )

    # --------------------------------------------------------
    # STEP 2: LOAD DOCUMENTS
    # --------------------------------------------------------

    documents = load_knowledge_base()

    print(
        f"Documents loaded: "
        f"{len(documents)}"
    )

    # --------------------------------------------------------
    # STEP 3: NORMALIZE TEXT
    # --------------------------------------------------------

    documents = normalize_documents(
        documents
    )

    print(
        f"Documents after normalization: "
        f"{len(documents)}"
    )

    # --------------------------------------------------------
    # STEP 4: CREATE CHUNKS
    # --------------------------------------------------------

    chunks = split_documents(
        documents
    )

    # --------------------------------------------------------
    # STEP 5: ADD CHUNK IDs
    # --------------------------------------------------------

    chunks = add_chunk_ids(
        chunks
    )

    print(
        f"Chunks created: "
        f"{len(chunks)}"
    )

    # --------------------------------------------------------
    # BASIC CHUNK ID VALIDATION
    # --------------------------------------------------------

    validate_chunk_ids(
        chunks
    )

    # --------------------------------------------------------
    # STEP 6: FINAL VALIDATION
    # --------------------------------------------------------

    validation_passed = (
        run_final_validation(
            chunks
        )
    )

    if not validation_passed:

        print(
            "\nIngestion stopped because "
            "validation failed."
        )

        return

    # --------------------------------------------------------
    # STEP 7: STATISTICS
    # --------------------------------------------------------

    print_chunk_statistics(
        chunks
    )

    print_file_type_statistics(
        documents
    )

    print_category_statistics(
        documents
    )

    # --------------------------------------------------------
    # STEP 8: SAMPLE CHUNK
    # --------------------------------------------------------

    if chunks:

        print(
            "\n--- SAMPLE CHUNK ---"
        )

        print(
            chunks[0].page_content
        )

        print(
            "\n--- SAMPLE METADATA ---"
        )

        print(
            chunks[0].metadata
        )

    # --------------------------------------------------------
    # COMPLETION
    # --------------------------------------------------------

    print(
        "\n" + "=" * 60
    )

    print(
        "INGESTION PIPELINE COMPLETED"
    )

    print(
        "=" * 60
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()