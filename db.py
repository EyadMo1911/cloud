# -*- coding: utf-8 -*-
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


# ================= SEED DATA =================
def seed_data():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM doctors")
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    doctors = [
        ("Dr Ahmed Ali", "Bone", "01012345678", "Cairo Medical Center"),
        ("Dr Sara Mohamed", "Bone", "01098765432", "Alex Hospital"),
        ("Dr Omar Hassan", "Stomach", "01122334455", "Gastro Clinic"),
        ("Dr Mona Adel", "Stomach", "01155667788", "Delta Hospital"),
        ("Dr Ali Youssef", "Teeth", "01233445566", "Smile Dental Clinic"),
        ("Dr Noha Samy", "Teeth", "01299887766", "Bright Dental Center"),
    ]

    cur.executemany("""
    INSERT INTO doctors(name, specialty, phone, address)
    VALUES (?,?,?,?)
    """, doctors)

    drugs = [
        ("City Pharmacy", "Panadol Extra", 6),
        ("City Pharmacy", "Brufen 400", 6),
        ("City Pharmacy", "Amoxicillin", 6),
        ("City Pharmacy", "Vitamin C 1000", 6),
        ("City Pharmacy", "Cough Syrup", 6),
        ("City Pharmacy", "Antacid Tablets", 6),
    ]

    cur.executemany("""
    INSERT INTO pharmacy(name, drug, quantity)
    VALUES (?,?,?)
    """, drugs)

    conn.commit()
    conn.close()

# ================= USERS =================
def register_user(u, p):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO users(username, password) VALUES (?,?)", (u, p))
    conn.commit()
    conn.close()


def login_user(u, p):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
    user = cur.fetchone()
    conn.close()
    return user

# ================= DOCTORS =================
def get_doctors_by_specialty(spec):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT name, phone, address FROM doctors WHERE specialty=?", (spec,))
    data = cur.fetchall()
    conn.close()
    return data

# ================= APPOINTMENTS =================
def book_appointment(user_id, doctor, date, time):
    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO appointments(user_id, doctor, date, time)
        VALUES (?,?,?,?)
        """, (user_id, doctor, date, time))

        conn.commit()
        conn.close()
        return True

    except sqlite3.IntegrityError:
        conn.close()
        return False


def get_my_appointments(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
    SELECT doctor, date, time
    FROM appointments
    WHERE user_id=?
    """, (user_id,))
    data = cur.fetchall()
    conn.close()
    return data

# ================= PHARMACY =================
def get_all_drugs():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, name, drug, quantity FROM pharmacy")
    data = cur.fetchall()
    conn.close()
    return data


# ================= ORDER DRUG =================
def order_drug(user_id, drug, qty, type_, address):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT quantity FROM pharmacy WHERE drug=?", (drug,))
    row = cur.fetchone()

    if not row or row[0] < qty:
        conn.close()
        return False

    cur.execute("""
    UPDATE pharmacy
    SET quantity = quantity - ?
    WHERE drug=?
    """, (qty, drug))

    cur.execute("""
    INSERT INTO orders(user_id, drug, qty, type, address, status, created_at)
    VALUES (?,?,?,?,?,?,?)
    """, (user_id, drug, qty, type_, address, "Pending",
          datetime.now().strftime("%Y-%m-%d %H:%M")))

    conn.commit()
    conn.close()
    return True


# ================= MY DRUG ORDERS =================
def get_my_drug_orders(user_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    SELECT drug, qty, type, address, status, created_at
    FROM orders
    WHERE user_id=?
    """, (user_id,))

    data = cur.fetchall()
    conn.close()
    return data

# ================= ADMIN =================
def update_order_status(order_id, status):
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()


def get_all_orders():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders")
    data = cur.fetchall()
    conn.close()
    return data
