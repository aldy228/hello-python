import os
import psycopg2  
from dotenv import load_dotenv

# Automatically finds .env in the current directory or parent dirs
load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("HOST", "localhost"),
        user=os.getenv("USER", "postgres"),
        password=os.getenv("PASSWORD"),
        dbname=os.getenv("DB_NAME"),
        port=int(os.getenv("PORT", 5432))  # psycopg2 requires port as an int
    )