import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "1234"),
    "dbname": os.getenv("DB_NAME", "your_db"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "client_encoding": "UTF8"
}