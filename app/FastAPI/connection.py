from app.database.rag_app import get_db_connection

#--- Table Creation for documents table
def create_documents_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the documents table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            document_id INTEGER PRIMARY KEY,
            File_Name TEXT NOT NULL UNIQUE,
            File_Type TEXT NOT NULL,
            File_Path TEXT NOT NULL,
            Chunk_Count INTEGER NOT NULL
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()


# Create chat_sessions table 

def create_chat_sessions_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the chat_sessions table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()
create_documents_table()
create_chat_sessions_table()
print("Document table Created")