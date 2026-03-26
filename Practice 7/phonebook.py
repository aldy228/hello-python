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


# ============================================================================
# -------------------------- USER INTERFACE (MENU) ---------------------------
# ============================================================================

def menu():
    """
    Main program loop - displays menu and handles user choices.
    Runs until user chooses to exit (option 0).
    """
    # Create the database table on startup (if it doesn't exist)
    create_table()

    # Infinite loop - keeps showing menu until user exits
    while True:
        # Display menu options
        print("\n========== PHONEBOOK MENU ==========")
        print("1. Add contact")
        print("2. Show contacts")
        print("3. Update contact")
        print("4. Delete contact")
        print("5. Import CSV")
        print("6. Reset database")
        print("0. Exit")
        print("====================================")

        # Get user's choice as a string
        choice = input("Choose: ")

        # Handle each menu option
        if choice == "1":
            # ADD CONTACT
            name = input("Name: ")
            phone = input("Phone: ")
            insert_contact(name, phone)
            print("✓ Contact added successfully!")

        elif choice == "2":
            # SHOW ALL CONTACTS
            show_contacts()

        elif choice == "3":
            # UPDATE CONTACT
            name = input("Name: ")
            phone = input("New phone: ")
            update_contact(name, phone)
            print("✓ Contact updated successfully!")

        elif choice == "4":
            # DELETE CONTACT
            name = input("Name: ")
            delete_contact(name)
            print("✓ Contact deleted successfully!")

        elif choice == "5":
            # IMPORT FROM CSV FILE
            # Path is relative to where you run the program from
            import_from_csv("Practice 7/contacts.csv")
            print("✓ Import completed!")

        elif choice == "6":
            # RESET DATABASE - DANGEROUS OPERATION!
            # Ask for confirmation before proceeding
            confirm = input("⚠️  Are you sure? This will delete ALL contacts! (yes/no): ")
            if confirm.lower() == "yes":
                reset_database()
            else:
                print("Reset cancelled.")

        elif choice == "0":
            # EXIT PROGRAM
            print("Goodbye! 👋")
            break  # Exit the while loop

        else:
            # Invalid input - not 0-6
            print("❌ Invalid choice. Please enter 0-6.")


# ============================================================================
# -------------------------- PROGRAM ENTRY POINT -----------------------------
# ============================================================================

# This code only runs if you execute this file directly (not when imported)
# This is a Python best practice for reusable modules
if __name__ == "__main__":
    # Start the menu loop
    menu()