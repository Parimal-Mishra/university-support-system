from pathlib import Path
import csv
import json

from langchain_core.documents import Document


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".xlsx",
    ".pptx",
    ".html",
    ".htm",
}


# ============================================================
# TEXT FILES
# ============================================================

def load_text(file_path: Path) -> list[Document]:
    """Load a plain-text file."""

    text = file_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    return [
        Document(
            page_content=text,
            metadata={
                "source": str(file_path),
                "file_type": "text",
            },
        )
    ]


# ============================================================
# MARKDOWN
# ============================================================

def load_markdown(file_path: Path) -> list[Document]:
    """Load a Markdown file."""

    text = file_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    return [
        Document(
            page_content=text,
            metadata={
                "source": str(file_path),
                "file_type": "markdown",
            },
        )
    ]


# ============================================================
# CSV
# ============================================================

def load_csv(file_path: Path) -> list[Document]:
    """Load each CSV row as a separate document."""

    documents = []

    with file_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row_number, row in enumerate(reader, start=1):

            fields = []

            for key, value in row.items():

                if value is None:
                    continue

                value = str(value).strip()

                if not value:
                    continue

                fields.append(
                    f"{key}: {value}"
                )

            content = "\n".join(fields)

            if not content:
                continue

            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": str(file_path),
                        "file_type": "csv",
                        "row": row_number,
                    },
                )
            )

    return documents


# ============================================================
# JSON
# ============================================================

def load_json(file_path: Path) -> list[Document]:
    """Load JSON content as a document."""

    data = json.loads(
        file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )
    )

    content = json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
    )

    return [
        Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "file_type": "json",
            },
        )
    ]


# ============================================================
# PDF
# ============================================================

def load_pdf(file_path: Path) -> list[Document]:
    """Load a PDF page-by-page."""

    from pypdf import PdfReader

    reader = PdfReader(str(file_path))

    documents = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):

        text = page.extract_text() or ""

        if not text.strip():
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": str(file_path),
                    "file_type": "pdf",
                    "page": page_number,
                },
            )
        )

    return documents


# ============================================================
# DOCX
# ============================================================

def load_docx(file_path: Path) -> list[Document]:
    """Load a DOCX document."""

    from docx import Document as DocxDocument

    document = DocxDocument(str(file_path))

    sections = []

    # Paragraphs
    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            sections.append(text)

    # Tables
    for table in document.tables:

        for row in table.rows:

            values = []

            for cell in row.cells:

                text = cell.text.strip()

                if text:
                    values.append(text)

            if values:
                sections.append(" | ".join(values))

    content = "\n".join(sections)

    return [
        Document(
            page_content=content,
            metadata={
                "source": str(file_path),
                "file_type": "docx",
            },
        )
    ]


# ============================================================
# XLSX
# ============================================================

def load_xlsx(file_path: Path) -> list[Document]:
    """Load an Excel workbook sheet-by-sheet."""

    from openpyxl import load_workbook

    workbook = load_workbook(
        filename=str(file_path),
        read_only=True,
        data_only=True,
    )

    documents = []

    for worksheet in workbook.worksheets:

        rows = list(
            worksheet.iter_rows(
                values_only=True
            )
        )

        if not rows:
            continue

        headers = [
            str(value).strip()
            if value is not None
            else f"column_{index + 1}"
            for index, value in enumerate(rows[0])
        ]

        for row_number, row in enumerate(
            rows[1:],
            start=2,
        ):

            fields = []

            for index, value in enumerate(row):

                if value is None:
                    continue

                value = str(value).strip()

                if not value:
                    continue

                header = (
                    headers[index]
                    if index < len(headers)
                    else f"column_{index + 1}"
                )

                fields.append(
                    f"{header}: {value}"
                )

            if not fields:
                continue

            content = "\n".join(fields)

            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": str(file_path),
                        "file_type": "xlsx",
                        "sheet": worksheet.title,
                        "row": row_number,
                    },
                )
            )

    workbook.close()

    return documents


# ============================================================
# POWERPOINT
# ============================================================

def load_pptx(file_path: Path) -> list[Document]:
    """Load PowerPoint slides."""

    from pptx import Presentation

    presentation = Presentation(str(file_path))

    documents = []

    for slide_number, slide in enumerate(
        presentation.slides,
        start=1,
    ):

        texts = []

        for shape in slide.shapes:

            if not hasattr(shape, "text"):
                continue

            text = shape.text.strip()

            if text:
                texts.append(text)

        content = "\n".join(texts)

        if not content.strip():
            continue

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(file_path),
                    "file_type": "pptx",
                    "slide": slide_number,
                },
            )
        )

    return documents


# ============================================================
# HTML
# ============================================================

def load_html(file_path: Path) -> list[Document]:
    """Load HTML and extract readable text."""

    from bs4 import BeautifulSoup

    html = file_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # Remove elements that do not contain useful
    # knowledge-base content.
    for element in soup(
        ["script", "style", "noscript"]
    ):
        element.decompose()

    text = soup.get_text(
        separator="\n",
        strip=True,
    )

    return [
        Document(
            page_content=text,
            metadata={
                "source": str(file_path),
                "file_type": "html",
            },
        )
    ]


# ============================================================
# UNIVERSAL FILE LOADER
# ============================================================

def load_file(file_path: Path) -> list[Document]:
    """
    Load a supported file according to its extension.
    """

    extension = file_path.suffix.lower()

    loaders = {
        ".pdf": load_pdf,
        ".docx": load_docx,
        ".txt": load_text,
        ".md": load_markdown,
        ".csv": load_csv,
        ".json": load_json,
        ".xlsx": load_xlsx,
        ".pptx": load_pptx,
        ".html": load_html,
        ".htm": load_html,
    }

    loader = loaders.get(extension)

    if loader is None:
        return []

    return loader(file_path)