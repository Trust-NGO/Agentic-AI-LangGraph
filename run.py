from app.loaders.loader import document_loader
from app.rag.splitter import split_documents
print("Hello")


documents = document_loader("Subhas_Chandra_Bose.docx")
print(f"Document printing: ",documents)
print(split_documents(documents))

