import sqlite3
from datetime import datetime

def saveSw(name, mass, density, cce):
    today = datetime.today().strftime("%Y-%m-%d")

    conn = sqlite3.connect('mars.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sw_table (
        name TEXT NOT NULL,
        mass REAL NOT NULL,
        density REAL NOT NULL,
        cce REAL NOT NULL,
        date TEXT NOT NULL
        )''')

    c.execute('''INSERT INTO sw_table VALUES (?, ?, ?, ?, ?)''', [name, mass, density, cce, today])
    conn.commit()
    conn.close()

def saveStats(balance, nominal, description, sigw, sigt):
    today = datetime.today().strftime("%Y-%m-%d")

    conn = sqlite3.connect('mars.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stats_table (
        balance TEXT NOT NULL,
        nominal TEXT NOT NULL,
        description TEXT DEFAULT '',
        sigw REAL NOT NULL,
        sigt REAL NOT NULL,
        date TEXT NOT NULL
        )''')

    c.execute('''INSERT INTO stats_table VALUES (?, ?, ?, ?, ?, ?)''', [balance, nominal, description, sigw, sigt, today])
    conn.commit()
    conn.close()