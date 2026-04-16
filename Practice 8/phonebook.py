# 👇 MUST be at the very top, before ANY other imports
import os
os.environ['PYTHONUTF8'] = '1'
os.environ['PGCLIENTENCODING'] = 'UTF8'

import psycopg2
import re
# (remove `from dotenv import load_dotenv` and `load_dotenv()` completely)

def get_connection():
    return psycopg2.connect(
        host="localhost",
        user="postgres",
        password="1234",
        dbname="your_db",   # 👈 Ensure this matches your actual DB name
        port=5432,
        client_encoding='UTF8'  # Forces libpq to use UTF-8
    )

def init_procedures():
    print("⏭️ SQL init skipped (menu works now)")

def search_contacts():
    keyword = input("🔍 Search: ")
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM phonebook WHERE firstname ILIKE %s OR secondname ILIKE %s OR phonenumber ILIKE %s",
            ('%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%')
        )
        rows = cur.fetchall()
    conn.close()
    print("\n📋 Results:" if rows else "No contacts found.")
    for row in rows: print(row)

def insert_contact():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("CALL upsert_contact(%s, %s, %s)", (input("Name: "), input("Surname: "), input("Phone: ")))
    conn.commit()
    conn.close()
    print("✅ Contact inserted/updated")

def bulk_insert():
    n = int(input("📦 How many? "))
    contacts = [(input("Name: "), input("Surname: "), input("Phone: ")) for _ in range(n)]
    conn = get_connection()
    with conn.cursor() as cur:
        cur.executemany("INSERT INTO phonebook(firstname, secondname, phonenumber) VALUES (%s, %s, %s)", contacts)
    conn.commit()
    conn.close()
    print(f"✅ {n} contacts added.")

def delete_contact():
    val = input("🗑️ Name/Surname/Phone: ")
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM phonebook WHERE firstname = %s OR secondname = %s OR phonenumber = %s", (val, val, val))
    conn.commit()
    conn.close()
    print("✅ Deleted (if existed).")

def show_paginated():
    lim, off = int(input("Limit: ")), int(input("Offset: "))
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM get_contacts_paginated(%s,%s)", (lim, off))
        rows = cur.fetchall()
    conn.close()
    print("\n📋 Results:" if rows else "No contacts found.")
    for row in rows: print(row)

def menu():
    init_procedures()  # Safe now
    while True:
        print("\n1.🔍 Search\n2.➕ Insert/Update\n3.📦 Bulk Insert\n4.🗑️ Delete\n5.📄 Paginated\n6.🚪 Exit")
        c = input("Choose: ").strip()
        if c=="1": search_contacts()
        elif c=="2": insert_contact()
        elif c=="3": bulk_insert()
        elif c=="4": delete_contact()
        elif c=="5": show_paginated()
        elif c=="6": break

if __name__ == "__main__":
    menu()