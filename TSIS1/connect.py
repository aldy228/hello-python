from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()
def get_connection():
    return psycopg2.connect(
        host=os.getenv("HOST"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        dbname=os.getenv("DB_NAME"),
        port=os.getenv("PORT")
    )