from langchain_core.documents import Document


# Module-level cache for retrievers
# Key: (vector_store_id, k)
# Value: retriever object
_retriever_cache = {}


def retrieve_documents(vector_store, question: str, k: int = 4) -> list[Document]:
    """
    Search the vector database for documents
    relevant to the user's question.

    Parameters
    ----------
    vector_store:
        FAISS vector store containing document embeddings.

    question:
        User's question.

    k:
        Number of relevant chunks to retrieve.

    Returns
    -------
    list[Document]
        Relevant document chunks.
    """

    if vector_store is None:
        raise ValueError("Vector store is not available.")

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    # Use cached retriever to avoid recreating the object on every call.
    # Old behavior: vector_store.as_retriever(...) was called on every request,
    # creating a new retriever wrapper each time (minor overhead, but adds up).
    retriever = _get_retriever(vector_store, k)

    # Search the vector database.
    documents = retriever.invoke(question)

    return documents


def _get_retriever(vector_store, k: int):
    """
    Cache retriever objects using a module-level dict.

    WHY NOT lru_cache:
    - FAISS vector store objects may not be hashable
    - lru_cache requires hashable arguments
    - A simple dict with id(vector_store) as key works perfectly

    Trade-off: Manual cache management, but negligible since we only
    ever have 1-2 vector stores per process.
    """
    cache_key = (id(vector_store), k)

    if cache_key not in _retriever_cache:
        _retriever_cache[cache_key] = vector_store.as_retriever(search_kwargs={"k": k})

    return _retriever_cache[cache_key]