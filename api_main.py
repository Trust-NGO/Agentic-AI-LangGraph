from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.FastAPI.documents import router as documents_router
from app.rag.rag_chain import warmup_models
from app.rag.vector_store import warmup_embeddings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: warm up models
    print("[STARTUP] Warming up models...")
    warmup_embeddings()
    warmup_models()
    print("[STARTUP] Warmup complete")
    yield
    # Shutdown: cleanup if needed


# ---------------------------------------------------------
# Create FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="Agentic RAG API",
    description="FastAPI backend for Ollama + FAISS + RAG",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------
# Register API routers
# ---------------------------------------------------------

app.include_router(documents_router)
#app.include_router(sessions_router)
#app.include_router(chat_router)