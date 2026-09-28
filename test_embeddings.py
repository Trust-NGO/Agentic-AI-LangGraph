from langchain_ollama import OllamaEmbeddings

print("Creating embeddings...")

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://127.0.0.1:11434",
)

print("Calling embed_query...")

vector = embeddings.embed_query("hello")

print("SUCCESS")
print("Vector size:", len(vector))
print("First 5:", vector[:5])