import sqlite3
from datetime import datetime

DB_NAME = "app.db"


def connect():
    return sqlite3.connect(DB_NAME)


# ================= SETUP =================
def setup_db():
    conn = connect()
    cur = conn.cursor()


    # ================= USERS =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # ================= DOCTORS =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        specialty TEXT,
        phone TEXT,
        address TEXT
    )
    """)

    # ================= APPOINTMENTS (FIXED) =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        doctor TEXT,
        date TEXT,
        time TEXT,
        UNIQUE(doctor, date, time)
    )
    """)

    # ================= PHARMACY =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pharmacy(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        drug TEXT,
        quantity INTEGER
    )
    """)

    # ================= ORDERS =================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        drug TEXT,
        qty INTEGER,
        type TEXT,
        address TEXT,
        status TEXT DEFAULT 'Pending',
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

