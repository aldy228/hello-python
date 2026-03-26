# ============================================================================
# DATABASE CONNECTION MODULE
# ============================================================================
# This file handles the connection to PostgreSQL database.
# It's imported by phonebook.py to get database access.
# ============================================================================

# Import psycopg2 - the PostgreSQL adapter for Python
# This library allows Python to communicate with PostgreSQL databases
import psycopg2


def get_connection():
    """
    Creates and returns a connection to the PostgreSQL database.
    
    This function is called by other modules (like phonebook.py)
    whenever they need to interact with the database.
    
    Returns:
        conn: A psycopg2 connection object to the database
    
    Database Credentials:
        - dbname: Name of your PostgreSQL database
        - user: Database username (default is 'postgres')
        - password: Your database password (CHANGE THIS in production!)
        - host: Server location ('localhost' = your computer)
        - port: PostgreSQL default port is 5432
    """
    # Establish connection to PostgreSQL database
    # psycopg2.connect() creates a new database connection
    conn = psycopg2.connect(
        dbname="phonebook_db",    # Name of the database to connect to
        user="postgres",          # Database username (default superuser)
        password="12345678",      # My password - keep this secure!
        host="localhost",         #'localhost' means database is on this computer
        port="5432"               # Default PostgreSQL port (5432)
    )
    
    # Return the connection object
    # The calling function will use this to create cursors and execute queries
    return conn


# ============================================================================
# HOW IT WORKS:
# ============================================================================
# 1. phonebook.py imports this file:  from connect import get_connection
# 2. When it needs database access, it calls:  conn = get_connection()
# 3. It gets a connection object that it can use to run SQL queries
# 4. After using the connection, it must call conn.close() to free resources
#
# WHY SEPARATE FILE?
# - Keeps database credentials in one place (easier to update)
# - Can be reused by multiple Python files
# - Cleaner code organization (separation of concerns)
# ============================================================================