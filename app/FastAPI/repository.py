from app.database.rag_app import get_db_connection,insert_application_log, get_chat_history

def insert_document(document_id,File_Name,File_Type,File_Path,Chunk_Count):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM documents WHERE document_id = ?", (File_Name,))
    document = cursor.fetchone()
    if document:
        raise ValueError(f"Document '{File_Name}' already exists.")
    
    # Insert the document into the database
    cursor.execute(
        "INSERT INTO documents (File_Name,File_Type,File_Path,Chunk_Count) VALUES (?, ?, ?, ?)",
        (File_Name,File_Type,File_Path,Chunk_Count)
    )

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

def get_all_documents():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve all documents from the database
    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()

    # Close the connection
    cursor.close()
    conn.close()

    return documents

def get_documents(document_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve the document with the specified document_id from the database
    cursor.execute("SELECT * FROM documents WHERE document_id = ?", (document_id,))
    document = cursor.fetchone()

    # Close the connection
    cursor.close()
    conn.close()

    return document

def delete_document(document_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete the document with the specified document_id from the database
    cursor.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

def insert_chat_message(session_id: str, role: str, content: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the chat session into the database
    cursor.execute(
        "INSERT INTO chat_sessions (session_id, role, content) VALUES (?, ?, ?)",
        (session_id,role, content)
    )

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

def get_chat_sessions(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve the chat session with the specified session_id from the database
    cursor.execute("SELECT * FROM chat_sessions WHERE session_id = %s", (session_id,))
    chat_session = cursor.fetchone()

    # Close the connection
    cursor.close()
    conn.close()

    return chat_session

def insert_application_logs(session_id: str, user_query: str, gpt_response: str, model: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the application log into the database
    cursor.execute(
        "INSERT INTO application_logs (session_id, user_query, gpt_response, model) VALUES (%s, %s, %s, %s)",
        (session_id, user_query, gpt_response, model)
    )

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

def get_chat_history(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve the chat history for the specified session_id from the database
    cursor.execute("SELECT user_query, gpt_response FROM application_logs WHERE session_id = %s ORDER BY created_at", (session_id,))
    chat_history = cursor.fetchall()

    # Close the connection
    cursor.close()
    conn.close()

    return chat_history

def document_exists(file_name: str) -> bool:
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM documents
            WHERE File_Name = ?
            LIMIT 1
            """,
            (file_name,),
        )

        return cursor.fetchone() is not None

    finally:
        connection.close()