import sqlite3
from datetime import datetime

def saveSw(mass, density, cce):
    today = datetime.today().strftime("%Y-%m-%d")

    conn = sqlite3.connect('mars.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sw_table (
        mass REAL NOT NULL,
        density REAL NOT NULL,
        cce REAL NOT NULL,
        date TEXT NOT NULL
        )''')

    c.execute('''INSERT INTO sw_table VALUES (?, ?, ?, ?)''', [mass, density, cce, today])
    conn.commit()
    conn.close()