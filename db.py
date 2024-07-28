import psycopg2
from datetime import datetime

def get_db_connection():
    hostname = "dpg-cqj2of6ehbks73c4rf30-a.oregon-postgres.render.com"
    port = "5432"
    username = "jobran"
    password = "064Gx1YojVpnmxDJ1IPVUgfFk8ldywaM"
    database = "chatbot_db"
    
    try:
        connection = psycopg2.connect(
            host=hostname,
            port=port,
            user=username,
            password=password,
            dbname=database
        )
        print("Database connection established successfully.")
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def ensure_page_recorded(page_id):
    connection = get_db_connection()
    if not connection:
        return
    cursor = connection.cursor()
    cursor.execute("SELECT page_id FROM pages WHERE page_id = %s", (page_id,))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO pages (page_id, page_name) VALUES (%s, %s)",
            (page_id, f"Page {page_id}")
        )
        connection.commit()
    cursor.close()
    connection.close()

def ensure_chat_recorded(page_id, user_id):
    connection = get_db_connection()
    if not connection:
        return None
    cursor = connection.cursor()
    cursor.execute(
        "SELECT chat_id FROM chats WHERE page_id = %s AND user_id = %s AND end_time IS NULL",
        (page_id, user_id)
    )
    chat = cursor.fetchone()
    if chat is None:
        cursor.execute(
            "INSERT INTO chats (page_id, user_id, start_time) VALUES (%s, %s, %s)",
            (page_id, user_id, datetime.now())
        )
        connection.commit()
        cursor.execute("SELECT currval(pg_get_serial_sequence(chats, chat_id))")
        chat_id = cursor.fetchone()[0]
    else:
        chat_id = chat[0]
    cursor.close()
    connection.close()
    return chat_id

def store_message(chat_id, message_text, sender_type):
    connection = get_db_connection()
    if not connection:
        return
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO messages (chat_id, sender_type, message_text) VALUES (%s, %s, %s)",
        (chat_id, sender_type, message_text)
    )
    connection.commit()
    cursor.close()
    connection.close()

def get_last_messages(chat_id):
    connection = get_db_connection()
    if not connection:
        return []
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM messages WHERE chat_id = %s ORDER BY timestamp DESC LIMIT 15",
        (chat_id,)
    )
    messages = cursor.fetchall()
    cursor.close()
    connection.close()
    return messages
