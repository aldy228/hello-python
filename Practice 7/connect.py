import psycopg2

def get_connection():
    conn = psycopg2.connect(
        dbname = "phonebook_db",
        user = "postgres",
        password = "12345678",
        host = "localhost",
        port = "5432"
    )
    return conn
