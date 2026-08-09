import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

# ==========================
# Users Table
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
)
""")

# ==========================
# Predictions Table
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image TEXT,
    disease TEXT,
    confidence TEXT,
    date TEXT
)
""")

# ==========================
# Appointments Table
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    doctor TEXT,
    date TEXT,
    time TEXT,
    problem TEXT
)
""")

# ==========================
# Patient Profile Table
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS patient_profile(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    blood_group TEXT,
    phone TEXT,
    address TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully!")