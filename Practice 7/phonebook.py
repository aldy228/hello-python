# Import the database connection function from connect.py
from connect import get_connection
# Import csv module to read CSV files
import csv
# ============================================================================
# -------------------------- DATABASE FUNCTIONS ------------------------------
# ============================================================================

def create_table():
    """
    Creates the contacts table in the database if it doesn't exist yet.
    This should be called once when the program starts.
    """
    # Get a connection to the PostgreSQL database
    conn = get_connection()
    # Create a cursor object - this is used to execute SQL queries
    cur = conn.cursor()

    # Execute SQL command to create table
    # CREATE TABLE IF NOT EXISTS - won't error if table already exists
    # id SERIAL PRIMARY KEY - auto-incrementing unique ID for each contact
    # VARCHAR(100) - text field that can hold up to 100 characters
    # VARCHAR(20) - text field for phone numbers (up to 20 characters)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            phone VARCHAR(20)
        )
    """)

    # Save/commit the changes to the database (required for CREATE, INSERT, UPDATE, DELETE)
    conn.commit()
    # Close the connection to free up resources
    conn.close()


def insert_contact(name, phone):
    """
    Adds a new contact to the database.
    
    Parameters:
        name (str): The contact's name
        phone (str): The contact's phone number
    """
    # Get database connection
    conn = get_connection()
    # Create cursor to execute queries
    cur = conn.cursor()

    # INSERT command adds a new row to the contacts table
    # %s are placeholders - prevents SQL injection attacks
    # (name, phone) - the actual values that replace the %s placeholders
    cur.execute(
        "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    # Save the changes to database
    conn.commit()
    # Close connection
    conn.close()


def show_contacts():
    """
    Displays all contacts stored in the database.
    Prints a message if no contacts exist.
    """
    # Get database connection
    conn = get_connection()
    # Create cursor
    cur = conn.cursor()

    # SELECT * means "get all columns" from the contacts table
    cur.execute("SELECT * FROM contacts")
    # fetchall() retrieves all rows from the query result
    rows = cur.fetchall()

    # Check if the result is empty (no contacts in database)
    if not rows:
        print("No contacts found.")
    else:
        # Loop through each row and print it
        # Each row is a tuple: (id, name, phone)
        for row in rows:
            print(row)

    # Close connection (no commit needed - we didn't change anything)
    conn.close()


def update_contact(name, new_phone):
    """
    Updates the phone number for an existing contact.
    
    Parameters:
        name (str): The contact's name (used to find the record)
        new_phone (str): The new phone number to save
    """
    # Get database connection
    conn = get_connection()
    # Create cursor
    cur = conn.cursor()

    # UPDATE command modifies existing records
    # SET phone = %s - the new value for the phone column
    # WHERE name = %s - only update the row where name matches
    # IMPORTANT: Without WHERE clause, ALL records would be updated!
    cur.execute(
        "UPDATE contacts SET phone = %s WHERE name = %s",
        (new_phone, name)
    )

    # Save changes
    conn.commit()
    # Close connection
    conn.close()


def delete_contact(name):
    """
    Deletes a contact from the database by name.
    
    Parameters:
        name (str): The contact's name to delete
    """
    # Get database connection
    conn = get_connection()
    # Create cursor
    cur = conn.cursor()

    # DELETE command removes records from the table
    # WHERE name = %s - only delete the row where name matches
    # (name,) - note the comma! This makes it a tuple with one element
    cur.execute(
        "DELETE FROM contacts WHERE name = %s",
        (name,)
    )

    # Save changes
    conn.commit()
    # Close connection
    conn.close()


def import_from_csv(filename):
    """
    Imports contacts from a CSV file into the database.
    Skips duplicate contacts (same name AND phone).
    
    Parameters:
        filename (str): Path to the CSV file
    """
    # Get database connection
    conn = get_connection()
    # Create cursor
    cur = conn.cursor()

    # Open the CSV file with UTF-8 encoding (supports special characters)
    # 'with' statement automatically closes the file when done
    with open(filename, encoding='utf-8') as f:
        # csv.reader parses the CSV file into rows
        reader = csv.reader(f)
        # Loop through each row in the CSV file
        for row in reader:
            # Check if row has at least 2 columns (name and phone)
            if len(row) >= 2:
                # Extract name and phone from the row
                name, phone = row[0], row[1]
                
                # Check if this exact contact already exists in database
                # This prevents duplicate entries when importing multiple times
                cur.execute(
                    "SELECT id FROM contacts WHERE name = %s AND phone = %s", 
                    (name, phone)
                )
                
                # fetchone() returns None if no matching record found
                if cur.fetchone() is None:
                    # Contact doesn't exist - insert it
                    cur.execute(
                        "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
                        (name, phone)
                    )
                    print(f"Added: {name}")
                else:
                    # Contact already exists - skip it
                    print(f"Skip (already exists): {name}")

    # Save all the inserts to database (done once after all rows processed)
    conn.commit()
    # Close connection
    conn.close()


def reset_database():
    """
    Deletes ALL contacts and resets the ID counter to 1.
    Use this to start fresh with a clean database.
    WARNING: This cannot be undone!
    """
    # Get database connection
    conn = get_connection()
    # Create cursor
    cur = conn.cursor()
    
    # DELETE without WHERE clause removes ALL records from the table
    cur.execute("DELETE FROM contacts")
    
    # SERIAL columns use a sequence to generate IDs
    # This command resets the sequence so next ID starts at 1
    # Without this, IDs would continue from where they left off (e.g., 8, 9, 10...)
    cur.execute("ALTER SEQUENCE contacts_id_seq RESTART WITH 1")
    
    # Save changes
    conn.commit()
    # Close connection
    conn.close()
    # Confirm to user
    print("✓ Database reset successfully!")

def search_contacts():
    """
    Search for contacts by name or phone prefix.
    """
    print("\n========== SEARCH CONTACTS ==========")
    print("1. Search by name")
    print("2. Search by phone prefix (starts with)")
    print("0. Back to menu")
    print("=====================================")
    
    search_choice = input("Choose filter type: ")
    
    conn = get_connection()
    cur = conn.cursor()
    
    results = None
    
    # ========== OPTION 1: SEARCH BY NAME ==========
    if search_choice == "1":
        search_term = input("Enter name (or part of it): ")
        
        # ILIKE = case-insensitive match (John, john, JOHN all work)
        # %search_term% = matches anywhere in the name
        cur.execute("SELECT * FROM contacts WHERE name ILIKE %s", (f"%{search_term}%",))
        results = cur.fetchall()
        print(f"\n🔍 Searching for name containing: '{search_term}'")
    
    # ========== OPTION 2: SEARCH BY PHONE PREFIX ==========
    elif search_choice == "2":
        prefix = input("Enter phone prefix (starts with): ")
        
        # prefix% = matches phones that START with this number
        cur.execute("SELECT * FROM contacts WHERE phone LIKE %s", (f"{prefix}%",))
        results = cur.fetchall()
        print(f"\n🔍 Searching for phone starting with: '{prefix}'")
    
    # ========== OPTION 0: BACK TO MENU ==========
    elif search_choice == "0":
        conn.close()
        return
    
    # ========== INVALID CHOICE ==========
    else:
        print("❌ Invalid choice!")
        conn.close()
        return
    
    # ========== DISPLAY RESULTS ==========
    print("\n" + "=" * 50)
    
    if not results:
        print("❌ No contacts found matching your criteria.")
    else:
        print(f"✅ Found {len(results)} contact(s):")
        print("=" * 50)
        print(f"{'ID':<5} | {'Name':<20} | {'Phone':<15}")
        print("=" * 50)
        for row in results:
            # row[0]=id, row[1]=name, row[2]=phone
            print(f"{row[0]:<5} | {row[1]:<20} | {row[2]:<15}")
        print("=" * 50)
    
    conn.close()

# ============================================================================
# -------------------------- USER INTERFACE (MENU) ---------------------------
# ============================================================================

def menu():
    create_table()

    while True:
        print("\n========== PHONEBOOK MENU ==========")
        print("1. Add contact")
        print("2. Show all contacts")
        print("3. Update contact")
        print("4. Delete contact")
        print("5. Import CSV")
        print("6. Search contacts")     
        print("7. Reset database")
        print("0. Exit")
        print("====================================")

        choice = input("Choose: ")

        if choice == "1":
            name = input("Name: ")
            phone = input("Phone: ")
            insert_contact(name, phone)
            print("✓ Contact added successfully!")

        elif choice == "2":
            show_contacts()

        elif choice == "3":
            name = input("Name: ")
            phone = input("New phone: ")
            update_contact(name, phone)
            print("✓ Contact updated successfully!")

        elif choice == "4":
            name = input("Name: ")
            delete_contact(name)
            print("✓ Contact deleted successfully!")

        elif choice == "5":
            import_from_csv("Practice 7/contacts.csv")
            print("✓ Import completed!")

        elif choice == "6":             
            search_contacts()

        elif choice == "7":
            confirm = input("⚠️  Are you sure? This will delete ALL contacts! (yes/no): ")
            if confirm.lower() == "yes":
                reset_database()
            else:
                print("Reset cancelled.")

        elif choice == "0":
            print("Goodbye! 👋")
            break

        else:
            print("❌ Invalid choice. Please enter 0-7.")


# ============================================================================
# -------------------------- PROGRAM ENTRY POINT -----------------------------
# ============================================================================

# This code only runs if you execute this file directly (not when imported)
# This is a Python best practice for reusable modules
if __name__ == "__main__":
    # Start the menu loop
    menu()