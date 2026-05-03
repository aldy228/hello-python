"""
phonebook.py — Main application file for the PhoneBook project.
Handles all console interactions, import/export, and database operations
by calling functions and stored procedures defined in the database.
"""

import csv
import json
import os
import sys
from connect import get_connection as connect  # imports our DB connection helper

# BASE_DIR is the folder where this script lives.
# All SQL and CSV files are looked up relative to this folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def file_path(filename):
    """Build an absolute path to a file in the same folder as this script."""
    return os.path.join(BASE_DIR, filename)


def run_sql_file(filename):
    """
    Read a .sql file from disk and execute it against the database.
    Used to load schema.sql, functions.sql, and procedures.sql.
    Uses a transaction: if anything fails, the whole file is rolled back.
    """
    path = file_path(filename)
    conn = connect()
    cur = conn.cursor()
    try:
        with open(path, "r", encoding="utf-8") as file:
            cur.execute(file.read())  # execute the entire SQL file at once
        conn.commit()  # save changes if everything went fine
    except Exception:
        conn.rollback()  # undo everything if there was an error
        raise
    finally:
        cur.close()
        conn.close()


def print_table(rows):
    """
    Print query results to the console in a simple table format.
    Each row is separated by a line of dashes.
    None values are printed as empty strings.
    """
    if not rows:
        print("No results")
        return
    for row in rows:
        print("-" * 90)
        print(" | ".join(str(value) if value is not None else "" for value in row))


def safe_date(value):
    """
    Clean up a date string. Returns None if the string is empty.
    PostgreSQL expects None (NULL) instead of an empty string for DATE fields.
    """
    value = (value or "").strip()
    return value if value else None


def safe_phone_type(value):
    """
    Validate and normalize the phone type.
    Only 'home', 'work', or 'mobile' are allowed (matches the DB CHECK constraint).
    Defaults to 'mobile' if the value is missing or invalid.
    """
    value = (value or "mobile").strip().lower()
    if value not in ("home", "work", "mobile"):
        return "mobile"
    return value


def get_group_id(cur, group_name):
    """
    Look up a group by name and return its ID.
    If the group doesn't exist yet, it is created automatically.
    Uses ON CONFLICT DO NOTHING to safely handle duplicates.
    """
    group_name = (group_name or "Other").strip() or "Other"
    # Insert the group if it doesn't exist yet
    cur.execute("""
        INSERT INTO groups(name)
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING
    """, (group_name,))
    # Now fetch the ID (whether it was just created or already existed)
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    return cur.fetchone()[0]


def save_contact(cur, name, surname, email, birthday, group_name, phone=None, phone_type="mobile", overwrite=True):
    """
    Insert or update a contact in the database.

    - If overwrite=True:  uses INSERT ... ON CONFLICT DO UPDATE (upsert).
      This means if a contact with the same name+surname exists, their data is updated.
    - If overwrite=False: uses INSERT ... ON CONFLICT DO NOTHING.
      Existing contacts are left unchanged.

    After saving the contact, if a phone number is provided, it is also saved
    to the phones table (with upsert to avoid duplicates).

    Returns the contact's ID.
    """
    group_id = get_group_id(cur, group_name)

    if overwrite:
        cur.execute("""
            INSERT INTO contacts(name, surname, email, birthday, group_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (name, surname)
            DO UPDATE SET
                email = EXCLUDED.email,
                birthday = EXCLUDED.birthday,
                group_id = EXCLUDED.group_id
            RETURNING id
        """, (name, surname, email or None, safe_date(birthday), group_id))
    else:
        cur.execute("""
            INSERT INTO contacts(name, surname, email, birthday, group_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (name, surname) DO NOTHING
            RETURNING id
        """, (name, surname, email or None, safe_date(birthday), group_id))

    result = cur.fetchone()
    if result is None:
        # Contact already existed and was not updated (DO NOTHING case),
        # so we manually fetch its ID
        cur.execute("SELECT id FROM contacts WHERE name=%s AND surname=%s", (name, surname))
        result = cur.fetchone()

    contact_id = result[0]

    # Save the phone number if one was provided
    if phone:
        cur.execute("""
            INSERT INTO phones(contact_id, phone, type)
            VALUES (%s, %s, %s)
            ON CONFLICT (contact_id, phone)
            DO UPDATE SET type = EXCLUDED.type
        """, (contact_id, phone, safe_phone_type(phone_type)))

    return contact_id


# ─────────────────────────────────────────────
#  SETUP
# ─────────────────────────────────────────────

def create_schema():
    """
    Drop and recreate all tables, then load functions and procedures.
    WARNING: this deletes all existing data! Used to start fresh.
    Runs three SQL files in order: schema.sql → functions.sql → procedures.sql.
    """
    run_sql_file("schema.sql")
    run_sql_file("functions.sql")
    run_sql_file("procedures.sql")
    print("Clean schema created. Functions and procedures loaded.")


def load_functions_and_procedures():
    """
    Reload just the functions and procedures without touching the data.
    Useful when you've edited functions.sql or procedures.sql and want
    to apply changes without wiping the database.
    """
    run_sql_file("functions.sql")
    run_sql_file("procedures.sql")
    print("Functions and procedures loaded")


# ─────────────────────────────────────────────
#  IMPORT / EXPORT
# ─────────────────────────────────────────────

def insert_from_csv():
    """
    Read contacts from contacts.csv and insert them into the database.
    Expected CSV columns: name, surname, email, birthday, group, phone, phone_type.
    Uses upsert (overwrite=True in save_contact), so re-importing updates existing contacts.
    The whole import is wrapped in a transaction — if one row fails, nothing is saved.
    """
    conn = connect()
    cur = conn.cursor()
    try:
        with open(file_path("contacts.csv"), "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)  # reads header row automatically
            for row in reader:
                save_contact(
                    cur,
                    row["name"].strip(),
                    row["surname"].strip(),
                    row.get("email", "").strip(),
                    row.get("birthday", "").strip(),
                    row.get("group", "Other").strip(),
                    row.get("phone", "").strip(),
                    row.get("phone_type", "mobile").strip()
                )
        conn.commit()
        print("CSV imported")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def export_to_json():
    """
    Export all contacts (with their phones and group) to a JSON file.
    The user can specify the output filename (defaults to contacts.json).
    Each contact includes a 'phones' list with all their phone numbers.
    """
    filename = input("Output JSON file name [contacts.json]: ").strip() or "contacts.json"
    path = filename if os.path.isabs(filename) else file_path(filename)

    conn = connect()
    cur = conn.cursor()

    # Fetch all contacts with their group name via JOIN
    cur.execute("""
        SELECT c.id, c.name, c.surname, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.id
    """)
    contacts = cur.fetchall()

    data = []
    for contact_id, name, surname, email, birthday, group_name in contacts:
        # For each contact, fetch all their phone numbers
        cur.execute("SELECT phone, type FROM phones WHERE contact_id=%s ORDER BY id", (contact_id,))
        phones = cur.fetchall()
        data.append({
            "name": name,
            "surname": surname,
            "email": email,
            "birthday": str(birthday) if birthday else None,
            "group": group_name,
            "phones": [
                {"phone": phone, "type": phone_type}
                for phone, phone_type in phones
            ]
        })

    # Write to file with pretty formatting (indent=4) and Unicode support
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    cur.close()
    conn.close()
    print("Exported to", path)


def import_from_json():
    """
    Import contacts from a JSON file into the database.
    If a contact with the same name+surname already exists, the user is asked
    whether to skip or overwrite that contact.
    All phones for a contact are also imported from the 'phones' list in the JSON.
    """
    filename = input("JSON file name [contacts.json]: ").strip() or "contacts.json"
    path = filename if os.path.isabs(filename) else file_path(filename)

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    conn = connect()
    cur = conn.cursor()
    try:
        for item in data:
            name = item["name"].strip()
            surname = item["surname"].strip()

            # Check if this contact already exists
            cur.execute("SELECT id FROM contacts WHERE name=%s AND surname=%s", (name, surname))
            duplicate = cur.fetchone()

            if duplicate:
                answer = input(f"{name} {surname} exists. skip / overwrite? ").strip().lower()
                if answer == "skip":
                    continue
                if answer != "overwrite":
                    print("Unknown answer. Skipped.")
                    continue
                # Remove old phones before overwriting so we start fresh
                cur.execute("DELETE FROM phones WHERE contact_id=%s", (duplicate[0],))

            contact_id = save_contact(
                cur,
                name,
                surname,
                item.get("email", ""),
                item.get("birthday"),
                item.get("group", "Other"),
                overwrite=True
            )

            # Insert all phones from the JSON
            for phone in item.get("phones", []):
                cur.execute("""
                    INSERT INTO phones(contact_id, phone, type)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (contact_id, phone)
                    DO UPDATE SET type = EXCLUDED.type
                """, (contact_id, phone.get("phone"), safe_phone_type(phone.get("type"))))

        conn.commit()
        print("JSON imported")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  CONSOLE OPERATIONS
# ─────────────────────────────────────────────

def insert_from_console():
    """
    Prompt the user to enter a contact manually and save it to the database.
    All fields are collected one by one from the console.
    """
    name = input("Name: ").strip()
    surname = input("Surname: ").strip()
    email = input("Email: ").strip()
    birthday = input("Birthday YYYY-MM-DD or empty: ").strip()
    group_name = input("Group [Other]: ").strip() or "Other"
    phone = input("Phone: ").strip()
    phone_type = input("Phone type home/work/mobile [mobile]: ").strip() or "mobile"

    conn = connect()
    cur = conn.cursor()
    try:
        save_contact(cur, name, surname, email, birthday, group_name, phone, phone_type)
        conn.commit()
        print("Contact saved")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def filter_by_group():
    """
    Show all contacts that belong to a specific group.
    Uses ILIKE for case-insensitive partial matching,
    so typing 'fri' will match 'Friend'.
    """
    group_name = input("Group name: ").strip()
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.surname, c.email, c.birthday, g.name AS group_name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        WHERE g.name ILIKE %s
        ORDER BY c.name, c.surname
    """, (f"%{group_name}%",))  # %...% means "contains" in SQL LIKE syntax
    print_table(cur.fetchall())
    cur.close()
    conn.close()


def search_by_email():
    """
    Search contacts by a partial email match.
    For example, typing 'gmail' returns everyone with a Gmail address.
    Uses ILIKE for case-insensitive matching.
    """
    text = input("Email search text: ").strip()
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, surname, email, birthday
        FROM contacts
        WHERE email ILIKE %s
        ORDER BY name, surname
    """, (f"%{text}%",))
    print_table(cur.fetchall())
    cur.close()
    conn.close()


def sort_contacts():
    """
    Display all contacts sorted by one of three criteria:
    1. Name (alphabetical)
    2. Birthday (chronological, NULLs at the end)
    3. Date added (when the record was created)
    The ORDER BY clause is built dynamically based on the user's choice.
    """
    print("1. Sort by name")
    print("2. Sort by birthday")
    print("3. Sort by date added")
    choice = input("Choose: ").strip()

    order_options = {
        "1": "c.name, c.surname",
        "2": "c.birthday NULLS LAST, c.name",  # NULLS LAST puts contacts with no birthday at the end
        "3": "c.date_added, c.name"
    }
    order_by = order_options.get(choice)
    if not order_by:
        print("Wrong choice")
        return

    conn = connect()
    cur = conn.cursor()
    # f-string is safe here because order_by comes from our own dictionary, not user input
    cur.execute(f"""
        SELECT c.id, c.name, c.surname, c.email, c.birthday, c.date_added, g.name AS group_name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY {order_by}
    """)
    print_table(cur.fetchall())
    cur.close()
    conn.close()


def paginated_navigation():
    """
    Browse contacts page by page using the get_contacts_page() DB function.
    The user chooses how many contacts to show per page, then navigates
    using 'next', 'prev', or 'quit'.
    OFFSET tracks our position in the full result set.
    """
    try:
        limit = int(input("Page size: ").strip())
    except ValueError:
        print("Page size must be a number")
        return

    offset = 0  # start at the beginning
    while True:
        conn = connect()
        cur = conn.cursor()
        # Call the PostgreSQL function get_contacts_page(limit, offset)
        cur.execute("SELECT * FROM public.get_contacts_page(%s, %s)", (limit, offset))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        print("\nPage offset:", offset)
        print_table(rows)

        command = input("next / prev / quit: ").strip().lower()
        if command == "next":
            offset += limit          # move forward by one page
        elif command == "prev":
            offset = max(0, offset - limit)  # move back, but never below 0
        elif command == "quit":
            break
        else:
            print("Unknown command")


def search_with_function():
    """
    Search contacts using the search_contacts() PostgreSQL function.
    This function searches across name, surname, email, AND all phone numbers.
    Returns distinct results (no duplicates even if a contact has multiple matching phones).
    """
    query = input("Search text: ").strip()
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.search_contacts(%s)", (query,))
    print_table(cur.fetchall())
    cur.close()
    conn.close()


def add_phone_proc():
    """
    Call the add_phone() stored procedure to add a phone number to a contact.
    The procedure looks up the contact by first name and inserts into the phones table.
    Raises an error if the contact is not found.
    """
    name = input("Contact first name: ").strip()
    phone = input("New phone: ").strip()
    phone_type = input("Type home/work/mobile: ").strip()

    conn = connect()
    cur = conn.cursor()
    try:
        # CALL is used to invoke stored procedures in PostgreSQL
        cur.execute("CALL public.add_phone(%s::varchar, %s::varchar, %s::varchar)", (name, phone, phone_type))
        conn.commit()
        print("Phone added")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def move_to_group_proc():
    """
    Call the move_to_group() stored procedure to reassign a contact to a different group.
    The procedure creates the group if it doesn't exist, then updates the contact's group_id.
    """
    name = input("Contact first name: ").strip()
    group_name = input("New group: ").strip()

    conn = connect()
    cur = conn.cursor()
    try:
        cur.execute("CALL public.move_to_group(%s::varchar, %s::varchar)", (name, group_name))
        conn.commit()
        print("Contact moved")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def delete_contact():
    """
    Delete a contact by their full name (name + surname).
    Because of ON DELETE CASCADE on the phones table,
    all their phone numbers are automatically deleted too.
    """
    name = input("Name: ").strip()
    surname = input("Surname: ").strip()

    conn = connect()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM contacts WHERE name=%s AND surname=%s", (name, surname))
        conn.commit()
        print("Contact deleted")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  MENU + MAIN LOOP
# ─────────────────────────────────────────────

def show_menu():
    """Print the main menu options to the console."""
    print("\nPHONEBOOK MENU")
    print("1. Create clean schema + load functions/procedures")
    print("2. Reload functions and procedures")
    print("3. Import from CSV")
    print("4. Add contact from console")
    print("5. Filter by group")
    print("6. Search by email")
    print("7. Sort contacts")
    print("8. Paginated navigation")
    print("9. Export to JSON")
    print("10. Import from JSON")
    print("11. Add phone using procedure")
    print("12. Move contact to group using procedure")
    print("13. Search using search_contacts function")
    print("14. Delete contact")
    print("0. Exit")


def main():
    """
    Main application loop.
    Maps each menu number to its corresponding function.
    Catches and prints errors without crashing the program,
    so the user can try again.
    """
    actions = {
        "1": create_schema,
        "2": load_functions_and_procedures,
        "3": insert_from_csv,
        "4": insert_from_console,
        "5": filter_by_group,
        "6": search_by_email,
        "7": sort_contacts,
        "8": paginated_navigation,
        "9": export_to_json,
        "10": import_from_json,
        "11": add_phone_proc,
        "12": move_to_group_proc,
        "13": search_with_function,
        "14": delete_contact,
    }

    while True:
        show_menu()
        choice = input("Choose: ").strip()

        if choice == "0":
            break  # exit the loop and end the program

        action = actions.get(choice)
        if action is None:
            print("Wrong choice")
            continue

        try:
            action()  # call whichever function matches the user's choice
        except Exception as error:
            print("ERROR:", error)
            print("Tip: first run option 1, then option 3.")


# Only run main() if this file is executed directly (not imported as a module)
if __name__ == "__main__":
    main()