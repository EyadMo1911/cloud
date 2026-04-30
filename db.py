import sqlite3
from datetime import datetime

DB_NAME = "app.db"


def connect():
    return sqlite3.connect(DB_NAME)


# ================= SETUP =================
def setup_db():
    conn = connect()
    cur = conn.cursor()
