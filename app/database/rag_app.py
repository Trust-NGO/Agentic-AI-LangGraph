import sqlite3
from datetime import datetime

DB_NAME = "rag_app.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return  conn

def create_application_logs():
    conn = get_db_connection()
    conn.execute('''
                    CREATE TABLE IF NOT EXISTS application_logs
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    user_query TEXT,
                    gpt_response TEXT,
                    model TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.close()

def insert_application_log(session_id, user_query, gpt_response, model):
    conn = get_db_connection()
    conn.execute('insert into application_logs(session_id, user_query, gpt_response, model) values (?,?,?,?)',(session_id, user_query, gpt_response,model))
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('select user_query, gpt_response from application_logs where session_id = ? order by created_at',
                   (session_id,))
    message = []
    for row in cursor.fetchall():
        message.extend([
            {'role': "user",'content': row['user_query']},
            {'role': 'assistant', 'content': row['gpt_response']}
        ])
    conn.close()
    return message

#initialize the database
create_application_logs()
