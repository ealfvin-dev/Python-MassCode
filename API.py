import sqlite3
from datetime import datetime

def getSws():
    conn = sqlite3.connect('mars.db')
    c = conn.cursor()
    c.execute('''SELECT rowid, name, mass, density, cce, date FROM sw_table ORDER BY massNumerical DESC''')

    data = c.fetchall()

    conn.commit()
    conn.close()
    return data

def getSw(rowId):
    conn = sqlite3.connect('mars.db')
    c = conn.cursor()
    c.execute('''SELECT name, mass, density, cce FROM sw_table WHERE rowid = ?''', [rowId])

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

def getStats():
    conn = sqlite3.connect('mars.db')
    c = conn.cursor()
    c.execute('''SELECT rowid, nominal, description, sigw, sigt, date FROM stats_table ORDER BY numericalOrder DESC''')

    data = c.fetchall()

    conn.commit()
    conn.close()
    return data

def getStat(rowId):
    conn = sqlite3.connect('mars.db')
    c = conn.cursor()
    c.execute('''SELECT nominal, sigw, sigt FROM stats_table WHERE rowid = ?''', [rowId])

    data = c.fetchall()

    conn.commit()
    conn.close()
    return data

def saveStats(nominal, description, sigw, sigt):
    today = datetime.today().strftime("%Y-%m-%d")

    if("lb" in nominal):
        numericalOrder = nominal.strip(' lb')
        numericalOrder = float(numericalOrder) + 1000000000
    elif("kg" in nominal):
        numericalOrder = nominal.strip(' kg')
        numericalOrder = float(numericalOrder) * 1000
    elif("mg" in nominal):
        numericalOrder = nominal.strip(' mg')
        numericalOrder = float(numericalOrder) / 1000
    else:
        numericalOrder = nominal.strip(' g')
        numericalOrder = float(numericalOrder)

    conn = sqlite3.connect('mars.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stats_table (
        nominal TEXT NOT NULL,
        numericalOrder REAL NOT NULL,
        description TEXT DEFAULT '',
        sigw TEXT NOT NULL,
        sigt TEXT NOT NULL,
        date TEXT NOT NULL
        )''')

    c.execute('''INSERT INTO stats_table VALUES (?, ?, ?, ?, ?, ?)''', [nominal, numericalOrder, description, sigw, sigt, today])
    conn.commit()
    conn.close()

def deleteStat(rowId):
    conn = sqlite3.connect('mars.db')
    c = conn.cursor()
    c.execute('''DELETE FROM stats_table WHERE rowid = ?''', [rowId])

    conn.commit()
    conn.close()