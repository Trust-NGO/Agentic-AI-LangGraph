from app.rag.vector_store import load_vectore_store

vector_store = load_vectore_store()

questions = [
    "Finacle script example",
    "Finacle sample script",
    "Finacle script hook",
    "Finacle script event",
    "Finacle scripting example",
    "how to write scripts in Finacle",
    "sample scripts directory",
    "script syntax",
]

for question in questions:

    print("\n" + "=" * 100)
    print("QUESTION:", question)
    print("=" * 100)

    documents = vector_store.similarity_search(
        question,
        k=5
    )

    for i, doc in enumerate(documents, start=1):

        print(f"\n--- RESULT {i} ---")
        print("Source:", doc.metadata.get("source"))
        print("Page:", doc.metadata.get("page"))

        print("CONTENT:")
        print(doc.page_content[:2000])