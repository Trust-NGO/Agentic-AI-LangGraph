import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

temp_upld_path = os.getenv("TEMP_UPLD_PATH")

if not temp_upld_path:
    raise ValueError("TEMP_UPLD_PATH is not configured in .env")
temp_upld_path = Path(temp_upld_path)

upload_dir = os.getenv("UPLOAD_DIR")
if not upload_dir:
    raise ValueError("UPLOAD_DIR is not configured in .env")

upload_dir = Path(upload_dir)

ollama_base_url = os.getenv("OLLAMA_BASE_URL")
embedding_model = os.getenv("EMBEDDING_MODEL")

faiss_dir_value = os.getenv("FAISS_INDEX_DIR")
if not faiss_dir_value:
    raise ValueError("FAISS_INDEX_DIR is not configured in .env")

faiss_dir = Path(faiss_dir_value)

pdf_passwords = [
    password.strip()
    for password in os.getenv("PDF_PASSWORDS", "").split(",")
    if password.strip()
]