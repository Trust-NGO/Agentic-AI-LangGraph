from FastAPI import FastAPI

app = FastAPI()


@get("/get_documents")
async def get_documents(session_id: str):
    chat_history = get_chat_history(session_id)
    for message in chat_history:
        print(f"Message: {message}")
    return {"chat_history": chat_history}


@post("/chat")
async def chat():
    return {"message": "Hello, World!"}
