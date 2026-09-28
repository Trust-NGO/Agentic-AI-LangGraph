from pathlib import Path
from app.config.setting import upload_dir
from app.loaders.loader import document_loader
from app.rag.splitter import split_documents
from app.rag.vector_store import create_vector_store
from app.FastAPI.repository import insert_document, document_exists
import uuid

def ingest_documents():

    print("=" * 70)
    print("STARTING BULK DOCUMENT INGESTION")
    print("=" * 70)

    # 1. Get all files from the ingestion directory
    files = [
        file_path
        for file_path in upload_dir.rglob("*.pdf")
        if file_path.is_file()
    ]

    print(f"Total files found: {len(files)}")

    if not files:
        print("No documents found.")
        return

    # 2. Process files one by one
    for file_path in files:

        print("\n" + "-" * 70)
        print(f"Processing: {file_path.name}")

# ---------------------------------------------
    # Check whether document was already indexed
    # ---------------------------------------------

        if document_exists(file_path.name):
            print(f"SKIPPING: {file_path.name} already uploaded/indexed.")
            continue

        try:

            # ------------------------------------------------
            # Same pipeline as your single-file upload
            # ------------------------------------------------

            # Load document
            documents = document_loader(str(file_path))
            print(f"Loaded documents: {len(documents)}")

            # Split document into chunks
            chunks = split_documents(documents)
            print(f"Generated chunks: {len(chunks)}")
            chunk_count = len(chunks)
            # Create / update FAISS vector store
            vector_store = create_vector_store(chunks)

            print(f"Vector store updated: {vector_store}")
            print(f"Successfully ingested: {file_path.name}")

            session_id = str(uuid.uuid4())
            print(session_id)
            extension = Path(file_path.name).suffix.lower()

            insert_document(session_id,file_path.name,extension,str(upload_dir),chunk_count)

        except Exception as exc:

            print(
                f"ERROR processing {file_path.name}: {exc}"
            )

    print("\n" + "=" * 70)
    print("BULK DOCUMENT INGESTION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    ingest_documents()