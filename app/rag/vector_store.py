from pathlib import Path
from functools import lru_cache
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from app.config.setting import (
    ollama_base_url,
    embedding_model,
    faiss_dir,
)

embeddings = OllamaEmbeddings(
    model=str(embedding_model),
    base_url=ollama_base_url,
)


def create_vector_store(chunks, batch_size=10):

    if not chunks:
        raise ValueError("No chunks were provided to create the vector store.")

    faiss_path = Path(faiss_dir)
    faiss_path.mkdir(parents=True, exist_ok=True)
    index_file = faiss_path / "index.faiss"

    # ---------------------------------------------------------
    # Create a new FAISS index
    # ---------------------------------------------------------

    if not index_file.exists():

        print("No existing FAISS index found.")
        print(f"Creating FAISS index with {len(chunks)} chunks...")

        vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings,
        )

        vector_store.save_local(str(faiss_path))

        print(f"FAISS saved successfully: {faiss_path}")

        return vector_store

    # ---------------------------------------------------------
    # Load existing FAISS index
    # ---------------------------------------------------------

    print("Existing FAISS index found.")
    print("Loading existing vector store...")

    vector_store = FAISS.load_local(
        str(faiss_path),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    # ---------------------------------------------------------
    # Add chunks in batches
    # ---------------------------------------------------------

    total_chunks = len(chunks)

    print(f"Adding {total_chunks} chunks to existing FAISS...")

    for start in range(0, total_chunks, batch_size):

        end = min(start + batch_size, total_chunks)
        batch = chunks[start:end]
        print(f"Embedding batch: {start + 1}-{end} / {total_chunks}")

        try:

            vector_store.add_documents(batch)
            print(f"Batch completed: {start + 1}-{end}")

        except Exception as e:

            print(f"ERROR embedding batch {start + 1}-{end}: {e}")

            raise

    # ---------------------------------------------------------
    # Save updated FAISS
    # ---------------------------------------------------------

    vector_store.save_local(str(faiss_path))

    print(f"FAISS saved successfully: {faiss_path}")
    print(f"Vector store updated: {vector_store}")

    return vector_store


@lru_cache(maxsize=1)
def load_vectore_store():

    faiss_path = Path(faiss_dir)

    index_file = faiss_path / "index.faiss"

    if not index_file.exists():

        raise FileNotFoundError(
            f"FAISS index not found at: {index_file}. "
            "Please ingest documents first."
        )

    vector_store = FAISS.load_local(
        str(faiss_path),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    print(
        f"FAISS vector store loaded from: {faiss_path}"
    )

    return vector_store


def warmup_embeddings():
    """
    Pre-warm the embedding model to avoid cold-start latency
    on the first retrieval request.

    WHY: The first embedding request to Ollama triggers nomic-embed-text
    model loading, which adds 2-5 seconds to the first retrieval.
    """
    try:
        print("[WARMUP] Loading embedding model...")
        embeddings.embed_query("warmup")
        print("[WARMUP] Embedding model loaded")
    except Exception as e:
        print(f"[WARMUP] Embedding warmup failed: {e}")