import sqlite3
from datetime import datetime

def getSws():
    conn = sqlite3.connect('mars.db')
    c = conn.cursor()
    c.execute('''SELECT rowid, name, mass, density, cce, date FROM sw_table ORDER BY massNumerical''')

    data = c.fetchall()

    conn.commit()
    conn.close()
    return data

def saveSw(name, mass, density, cce):
    today = datetime.today().strftime("%Y-%m-%d")

    conn = sqlite3.connect('mars.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sw_table (
        name TEXT NOT NULL UNIQUE,
        massNumerical REAL NOT NULL,
        mass TEXT NOT NULL,
        density TEXT NOT NULL,
        cce TEXT NOT NULL,
        date TEXT NOT NULL
        )''')

    c.execute('''REPLACE INTO sw_table VALUES (?, ?, ?, ?, ?, ?)''', [name, float(mass), mass, density, cce, today])
    conn.commit()
    conn.close()

def deleteSw(rowId):
    conn = sqlite3.connect('mars.db')
    c = conn.cursor()
    c.execute('''DELETE FROM sw_table WHERE rowid = ?''', [rowId])

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
        sigw TEXT NOT NULL,
        sigt TEXT NOT NULL,
        date TEXT NOT NULL
        )''')

    c.execute('''REPLACE INTO stats_table VALUES (?, ?, ?, ?, ?, ?)''', [balance, nominal, description, sigw, sigt, today])
    conn.commit()
    conn.close()