from fastapi import APIRouter, UploadFile, File, HTTPException
from app.FastAPI.repository import get_all_documents
from pathlib import Path
from app.config.setting import upload_dir
import shutil
import time
from app.loaders.loader import document_loader
from app.rag.rag_chain import invoke_rag_chain
from app.rag.splitter import split_documents
from app.rag.vector_store import create_vector_store, load_vectore_store
import uuid
from app.FastAPI.repository import (
    insert_document,
    get_documents, 
    delete_document,
    insert_chat_message)
from pydantic import BaseModel
from app.database.rag_app import insert_application_log
from app.rag.retriever import retrieve_documents

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str | None = None
    question: str
    stream: bool = False


class QueryResponse(BaseModel):
    session_id: str 
    answer: str


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get("/get_all_documents")
async def fetch_all_documents():
    documents = get_all_documents()
    if not documents:
        return {"message": "There are no documents uploaded."}
    return {"documents": documents}


@router.get("/get_documents")
async def get_document(document_id: str):
    documents = get_documents(document_id)
    if not documents:
        return {f"documents": f"There is no document with Id {document_id}."}
    return {"documents": documents}


@router.delete("/delete_document")
async def delete_documents(document_id: str):
    documents = get_documents(document_id)
    if not documents:
        return {f"documents": f"There is no document with Id {document_id}."}
    delete_document(document_id)
    return {f"documents": f"Document Id {document_id} Deleted"}


@router.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required"
        )

    session_id = str(uuid.uuid4())

    allowed_extensions = {".pdf",".docx",".txt",".csv"}
    extension = Path(file.filename).suffix.lower()
    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}"
        )
    file_path = Path(upload_dir) / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    documents = document_loader(str(file_path))
    chunks = split_documents(documents)
    chunk_count = len(chunks)
    vector_store = create_vector_store(chunks)

    insert_document(session_id, file.filename, extension, str(upload_dir), chunk_count)
    return {
        "message": "Document uploaded successfully",
        "file_name": file.filename,
        "file_type": extension,
        "file_path": str(file_path),
        "Total_Chunks": chunk_count,
        "Vector_DB": "Stored in Vector DB"
    }


@router.post("/chat", response_model=QueryResponse)
async def chat(QueryInput: ChatRequest):
    """
    Chat endpoint with performance timing.

    WHY TIMING: We need to identify exactly where time is spent.
    This log shows: retrieval, context construction, and LLM generation
    separately so we can see which component is the bottleneck.
    """
    t_start = time.perf_counter()

    session_id = QueryInput.session_id
    if not session_id:
        session_id = str(uuid.uuid4())

    # --- RETRIEVAL ---
    t0 = time.perf_counter()
    # WHY: load_vectore_store() is now cached with lru_cache(maxsize=1),
    # so the FAISS index is deserialized from disk only ONCE per process.
    # Old behavior: the index was loaded from disk on EVERY request,
    # causing 0.3-0.8s of unnecessary I/O + deserialization overhead.
    vector_store = load_vectore_store()
    retrieved_documents = retrieve_documents(
        vector_store,
        QueryInput.question,
        k=8,
    )
    t_retrieve = time.perf_counter() - t0

    if not retrieved_documents:
        return QueryResponse(
            session_id=session_id,
            answer="I couldn't find relevant information in the uploaded documents."
        )

    # --- CONTEXT CONSTRUCTION ---
    t0 = time.perf_counter()
    context = "\n\n".join(
        document.page_content
        for document in retrieved_documents
    )
    t_context = time.perf_counter() - t0

    # --- LLM GENERATION ---
    t0 = time.perf_counter()
    answer = invoke_rag_chain(
        context=context,
        question=QueryInput.question,
        stream=QueryInput.stream,
    )
    t_llm = time.perf_counter() - t0

    t_total = time.perf_counter() - t_start

    # Log performance breakdown to console for bottleneck identification
    print(
        f"[PERF] Total: {t_total:.3f}s | "
        f"Retrieve: {t_retrieve:.3f}s | "
        f"Context: {t_context:.3f}s | "
        f"LLM: {t_llm:.3f}s"
    )

    insert_chat_message(session_id=session_id, role="user", content=QueryInput.question)
    insert_chat_message(session_id=session_id, role="assistant", content=answer)
    insert_application_log(session_id, QueryInput.question, answer, 'Ollama3.2')

    return QueryResponse(
        session_id=session_id,
        answer=answer
    )