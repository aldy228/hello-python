from connect import get_connection
import csv

# ---------- FUNCTIONS ----------

def create_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            phone VARCHAR(20)
        )
    """)

    conn.commit()
    conn.close()


def insert_contact(name, phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    conn.close()


def show_contacts():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM contacts")
    rows = cur.fetchall()

    if not rows:
        print("No contacts found.")
    else:
        for row in rows:
            print(row)

    conn.close()


def update_contact(name, new_phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE contacts SET phone = %s WHERE name = %s",
        (new_phone, name)
    )

    conn.commit()
    conn.close()


def delete_contact(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM contacts WHERE name = %s",
        (name,)
    )

    conn.commit()
    conn.close()


def import_from_csv(filename):
    conn = get_connection()
    cur = conn.cursor()

    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                name, phone = row[0], row[1]
                
                # Check if contact already exists
                cur.execute("SELECT id FROM contacts WHERE name = %s AND phone = %s", (name, phone))
                if cur.fetchone() is None:
                    # Only insert if not found
                    cur.execute(
                        "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
                        (name, phone)
                    )
                    print(f"Added: {name}")
                else:
                    print(f"Skip (already exists): {name}")

    conn.commit()
    conn.close()

def reset_database():
    """Delete all contacts and reset ID counter"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Delete all records
    cur.execute("DELETE FROM contacts")
    
    # Reset the ID counter to 1
    cur.execute("ALTER SEQUENCE contacts_id_seq RESTART WITH 1")
    
    conn.commit()
    conn.close()
    print("Database reset!")

# ---------- MENU ----------

def menu():
    create_table()

    while True:
        print("\n1. Add contact")
        print("2. Show contacts")
        print("3. Update contact")
        print("4. Delete contact")
        print("5. Import CSV")
        print("6. Reset database")  # NEW OPTION
        print("0. Exit")

        choice = input("Choose: ")

        if choice == "1":
            name = input("Name: ")
            phone = input("Phone: ")
            insert_contact(name, phone)

        elif choice == "2":
            show_contacts()

        elif choice == "3":
            name = input("Name: ")
            phone = input("New phone: ")
            update_contact(name, phone)

        elif choice == "4":
            name = input("Name: ")
            delete_contact(name)

        elif choice == "5":
            import_from_csv("Practice 7/contacts.csv") 

        elif choice == "6":  # NEW RESET FUNCTIONALITY
            confirm = input("Are you sure? This will delete ALL contacts! (yes/no): ")
            if confirm.lower() == "yes":
                reset_database()
            else:
                print("Reset cancelled.")

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid choice")


# ---------- ENTRY POINT ----------

if __name__ == "__main__":
    menu()