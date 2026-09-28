from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader
)

from app.config.setting import upload_dir


def document_loader(file_name: str) -> list[Document]:

    # ---------------------------------------------------------
    # 1. Validate filename
    # ---------------------------------------------------------

    if not file_name:
        raise FileNotFoundError(
            f"Upload file was not provided. "
            f"Upload directory: {upload_dir}"
        )

    # ---------------------------------------------------------
    # 2. Build path
    # ---------------------------------------------------------

    file_path = Path(file_name)

    # ---------------------------------------------------------
    # 3. Check file
    # ---------------------------------------------------------

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    # ---------------------------------------------------------
    # 4. Extension
    # ---------------------------------------------------------

    extension = file_path.suffix.lower()

    # ---------------------------------------------------------
    # 5. Select loader
    # ---------------------------------------------------------

    if extension == ".pdf":
        loader = PyPDFLoader(str(file_path))

    elif extension == ".docx":
        loader = Docx2txtLoader(str(file_path))

    elif extension == ".txt":
        loader = TextLoader(
            str(file_path),
            encoding="utf-8"
        )

    elif extension == ".csv":
        loader = CSVLoader(str(file_path))

    else:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported: PDF, DOCX, TXT and CSV."
        )

    # ---------------------------------------------------------
    # 6. Load
    # ---------------------------------------------------------

    documents = loader.load()

    return documents