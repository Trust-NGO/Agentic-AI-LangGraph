import uuid
from pathlib import Path
import time

import streamlit as st

from app.config.setting import upload_dir

from app.loaders.loader import document_loader
from app.rag.splitter import split_documents

from app.rag.vector_store import (
    create_vector_store,
    load_vectore_store,
)

from app.rag.retriever import retrieve_documents
from app.rag.rag_chain import invoke_rag_chain

from app.database.rag_app import (
    insert_application_log,
    get_chat_history,
)


# ============================================================
# SESSION ID
# ============================================================

if "session_id" not in st.session_state:

    st.session_state.session_id = str(
        uuid.uuid4()
    )


# ============================================================
# STREAMLIT INTERFACE
# ============================================================

def render_interface():

    # ========================================================
    # INITIALIZE SESSION STATE
    # ========================================================

    if "session_id" not in st.session_state:

        st.session_state.session_id = str(
            uuid.uuid4()
        )

    if "chat_history" not in st.session_state:

        st.session_state.chat_history = []

    if "vector_store" not in st.session_state:

        st.session_state.vector_store = None

    # ========================================================
    # LOAD EXISTING KNOWLEDGE BASE
    # ========================================================

    if st.session_state.vector_store is None:

        try:

            st.session_state.vector_store = (
                load_vectore_store()
            )

            print(
                "Existing FAISS knowledge base loaded."
            )

        except FileNotFoundError as e:

            print(
                f"FAISS knowledge base not available: {e}"
            )

        except Exception as e:

            print(
                f"Failed to load FAISS: {e}"
            )

    # ========================================================
    # SIDEBAR
    # ========================================================

    with st.sidebar:

        st.title("Configuration")

        # ====================================================
        # KNOWLEDGE BASE STATUS
        # ====================================================

        st.write("### Knowledge Base")

        if st.session_state.vector_store is not None:

            st.success(
                "Knowledge Base Loaded"
            )

        else:

            st.warning(
                "Knowledge Base is empty"
            )

        # ====================================================
        # UPLOAD DOCUMENT
        # ====================================================

        st.divider()

        st.write(
            "### Add Document"
        )

        st.caption(
            "Uploaded documents are permanently "
            "added to the knowledge base."
        )

        uploaded_file = st.file_uploader(
            "Upload a document",
            type=[
                "pdf",
                "docx",
                "txt",
                "csv",
            ],
        )

        # ====================================================
        # PROCESS UPLOADED DOCUMENT
        # ====================================================

        if uploaded_file is not None:

            upload_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            file_path = (
                upload_dir / uploaded_file.name
            )

            # ------------------------------------------------
            # SAVE FILE
            # ------------------------------------------------

            try:

                with open(
                    file_path,
                    "wb",
                ) as file:

                    file.write(
                        uploaded_file.getbuffer()
                    )

                st.success(
                    f"Document saved: "
                    f"{uploaded_file.name}"
                )

            except Exception as e:

                st.error(
                    f"Failed to save document: {e}"
                )

                return

            # ------------------------------------------------
            # LOAD DOCUMENT
            # ------------------------------------------------

            try:

                documents = document_loader(
                    str(file_path)
                )

                if not documents:

                    st.error(
                        "No content could be extracted "
                        "from this document."
                    )

                    return

                st.write(
                    f"Documents loaded: "
                    f"{len(documents)}"
                )

            except Exception as e:

                st.error(
                    f"Failed to load document: {e}"
                )

                return

            # ------------------------------------------------
            # SPLIT DOCUMENT
            # ------------------------------------------------

            try:

                chunks = split_documents(
                    documents
                )

                if not chunks:

                    st.error(
                        "No text chunks were generated "
                        "from this document."
                    )

                    st.warning(
                        "If this is a scanned/image PDF, "
                        "OCR may be required."
                    )

                    return

                st.write(
                    f"Generated chunks: "
                    f"{len(chunks)}"
                )

            except Exception as e:

                st.error(
                    f"Failed to split document: {e}"
                )

                return

            # ------------------------------------------------
            # ADD TO EXISTING FAISS
            # ------------------------------------------------

            try:

                with st.spinner(
                    "Adding document to knowledge base..."
                ):

                    vector_store = (
                        create_vector_store(
                            chunks
                        )
                    )

                # Update current Streamlit session
                st.session_state.vector_store = (
                    vector_store
                )

                st.success(
                    f"{uploaded_file.name} "
                    "added to the knowledge base."
                )

                st.info(
                    "You can now ask questions about "
                    "this document and all previously "
                    "indexed documents."
                )

            except Exception as e:

                st.error(
                    f"Failed to index document: {e}"
                )

                return

        # ====================================================
        # MODEL INFORMATION
        # ====================================================

        st.divider()

        st.write("### Model")

        st.write(
            "LLM: Llama 3.2"
        )

        st.write(
            "Embeddings: nomic-embed-text"
        )

        # ====================================================
        # CLEAR CHAT
        # ====================================================

        st.divider()

        if st.button("Clear Chat"):

            st.session_state.chat_history = []

            st.rerun()

    # ========================================================
    # MAIN PAGE
    # ========================================================

    st.title(
        "AI Chat Assistant"
    )

    st.caption(
        "RAG + LangGraph + Ollama"
    )

    # ========================================================
    # KNOWLEDGE BASE NOT AVAILABLE
    # ========================================================

    if st.session_state.vector_store is None:

        st.info(
            "No knowledge base is available yet. "
            "Run ingest_doc.py for bulk ingestion "
            "or upload a document from the sidebar."
        )

        return

    # ========================================================
    # LOAD CHAT HISTORY
    # ========================================================

    try:

        chat_history = get_chat_history(
            st.session_state.session_id
        )

    except Exception as e:

        print(
            f"Failed to load chat history: {e}"
        )

        chat_history = []

    # ========================================================
    # DISPLAY PREVIOUS MESSAGES
    # ========================================================

    for message in chat_history:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )

    # ========================================================
    # CHAT INPUT
    # ========================================================

    user_question = st.chat_input(
        "Ask something about your documents..."
    )

    if not user_question:

        return

    # ========================================================
    # DISPLAY USER QUESTION
    # ========================================================

    with st.chat_message("user"):

        st.write(
            user_question
        )

    # ========================================================
    # RETRIEVE DOCUMENTS
    # ========================================================

    t_start = time.perf_counter()

    try:
        t0 = time.perf_counter()
        retrieved_documents = (
            retrieve_documents(
                st.session_state.vector_store,
                user_question,
                k=8,
            )
        )
        t_retrieve = time.perf_counter() - t0

        # ----------------------------------------------------
        # DEBUG INFORMATION
        # ----------------------------------------------------

        print("\n" + "=" * 80)
        print("QUESTION:", user_question,)
        print("=" * 80)

        for i, document in enumerate(
            retrieved_documents,
            start=1,
        ):

            print(f"\n--- Retrieved Document {i} ---")
            print("Source:", document.metadata.get("source"))
            #print("File Name:",document.metadata.get("file_name"),)
            #print("Metadata:",document.metadata,)
            #print("Content:")
            #print(document.page_content[:2000])

        print("=" * 80 + "\n")

    except Exception as e:

        st.error(f"Failed to retrieve documents: {e}")
        return

    # ========================================================
    # NO RETRIEVED DOCUMENTS
    # ========================================================

    if not retrieved_documents:

        assistant_response = (
            "I couldn't find relevant information "
            "in the uploaded documents."
        )

        with st.chat_message(
            "assistant"
        ):

            st.write(
                assistant_response
            )

        return

    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    t0 = time.perf_counter()
    context = "\n\n".join(
        document.page_content
        for document in retrieved_documents
    )
    t_context = time.perf_counter() - t0

    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    try:
        t0 = time.perf_counter()
        assistant_response = invoke_rag_chain(
            context=context,
            question=user_question,
        )
        t_llm = time.perf_counter() - t0

    except Exception as e:

        st.error(
            f"Failed to generate response: {e}"
        )

        return

    # ========================================================
    # DISPLAY ASSISTANT RESPONSE
    # ========================================================

    with st.chat_message(
        "assistant"
    ):

        st.write(
            assistant_response
        )

    t_total = time.perf_counter() - t_start

    # Log performance breakdown
    print(
        f"[PERF] Total: {t_total:.3f}s | "
        f"Retrieve: {t_retrieve:.3f}s | "
        f"Context: {t_context:.3f}s | "
        f"LLM: {t_llm:.3f}s"
    )

    print("Answer Given in streamlit App")
    # ========================================================
    # SAVE CONVERSATION
    # ========================================================

    try:

        insert_application_log(
            st.session_state.session_id,
            user_question,
            assistant_response,
            "Ollama3.2",
        )

    except Exception as e:

        print(
            f"Failed to save conversation "
            f"to database: {e}"
        )