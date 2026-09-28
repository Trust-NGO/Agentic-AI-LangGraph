import streamlit as st
from app.interface.interface import render_interface
from app.rag.rag_chain import warmup_models
from app.rag.vector_store import warmup_embeddings


def main():
    """
    Main Streamlit application.
    """
    # Pre-warm models on startup to avoid cold-start latency on first request
    print("[STARTUP] Warming up models...")
    warmup_embeddings()
    warmup_models()
    print("[STARTUP] Warmup complete")

    st.set_page_config(
        page_title="RAG CHAT",
        page_icon="🤖",
        layout="wide",
    )

    render_interface()


if __name__ == "__main__":
    main()