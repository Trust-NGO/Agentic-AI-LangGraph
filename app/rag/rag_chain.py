import time
from typing import Iterator
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# ---------------------------------------------------------------------------
# LLM configuration
# ---------------------------------------------------------------------------
# OLD: ChatOllama(model="llama3.2", base_url="http://localhost:11434", temperature=0)
#
# WHY CHANGED:
#   Added num_ctx=2048 to limit the context window size.
#   A smaller context window means:
#     - Less memory used during inference
#     - Faster token generation (the model processes fewer tokens at once)
#     - Lower latency for the first token
#
# Trade-off: If a retrieved context is very long (>2048 tokens), some
# information may be truncated. In practice, with k=8 and 1000-char chunks,
# the context is typically well under this limit.
# ---------------------------------------------------------------------------
llm = ChatOllama(
    model="llama3.2",
    base_url="http://localhost:11434",
    temperature=0,
    num_ctx=2048,
)


# ---------------------------------------------------------------------------
# Generic RAG prompt (domain-agnostic)
# ---------------------------------------------------------------------------
# This prompt works for ANY domain - Finacle, Python, policies, reports, etc.
# No domain-specific rules, no assumptions about document types.
# ---------------------------------------------------------------------------
prompt = ChatPromptTemplate.from_template(
    """You are a helpful assistant that answers questions using ONLY the
retrieved document content below.

RETRIEVED DOCUMENT CONTENT:
{context}

USER QUESTION:
{question}

INSTRUCTIONS:
- Answer only from the retrieved document content. Do not use outside knowledge.
- Do not invent facts, numbers, dates, names, code, or procedures.
- If the documents contain relevant information, answer directly and completely.
- If the documents partially answer the question, provide what is supported
  and clearly state what is not available.
- If the documents do not contain meaningful information about the question,
  respond: "I couldn't find the answer in the uploaded documents."
- For learning questions, explain clearly and progressively.
- For syntax/code/command questions, preserve documented syntax accurately.
- For lists, provide all relevant items found in the documents.
- For comparisons, compare only what the documents support.
- For summaries, summarize the relevant retrieved information.
- Do not mention RAG, FAISS, embeddings, retrieval, chunks, context, or
  any internal system details.
- Answer naturally without repeating the question.

ANSWER:"""
)


# ---------------------------------------------------------------------------
# RAG chain
# ---------------------------------------------------------------------------
rag_chain = (
    prompt
    | llm
    | StrOutputParser()
)


def invoke_rag_chain(context: str, question: str, stream: bool = False) -> str | Iterator[str]:
    """
    Invoke the RAG chain with optional streaming.

    Parameters
    ----------
    context : str
        Retrieved document context.
    question : str
        User's question.
    stream : bool
        If True, returns a generator that yields tokens as they're generated.

    Returns
    -------
    str or Iterator[str]
        If stream=False: full answer as string.
        If stream=True: generator yielding string chunks.
    """
    inputs = {"context": context, "question": question}

    if stream:
        return _stream_rag_chain(inputs)
    else:
        return rag_chain.invoke(inputs)


def _stream_rag_chain(inputs: dict) -> Iterator[str]:
    """
    Stream the LLM response token by token.

    WHY: Streaming does NOT make the model itself faster, but it dramatically
    reduces PERCEIVED waiting time. The user sees the first tokens appear
    almost immediately instead of waiting for the full response.

    This is critical for user experience - a 5-second response that streams
    feels much faster than a 5-second response that appears all at once.
    """
    for chunk in rag_chain.stream(inputs):
        yield chunk


def warmup_models():
    """
    Pre-warm the LLM and embedding models to avoid cold-start latency
    on the first user request.

    WHY: The first request to Ollama triggers model loading into GPU/CPU
    memory, which can take 10-30 seconds. This function sends a dummy
    request to load the model before real users hit the system.

    Call this at application startup (e.g., in main.py or api_main.py).
    """
    try:
        print("[WARMUP] Loading LLM model...")
        # Dummy invoke to load llama3.2
        llm.invoke("Hi")
        print("[WARMUP] LLM model loaded")
    except Exception as e:
        print(f"[WARMUP] LLM warmup failed: {e}")