import API

def test1CrudSwDb(suite):
    name = "testCrudSwDb"
    mass = "100.01"
    density = "7.95"
    cce = "0.000045"

    try:
        insertId = API.saveSw(name, mass, density, cce)
        suite.passTest("SAVE SW TO DATABASE")
    except:
        suite.failTest("SAVE SW TO DATABASE")
        suite.logFailure(["Error saving sesitivity weight", "to the database"], "SAVE SW TO DATABASE")
        return

    try:
        swsData = API.getSws()
        suite.passTest("GET ALL SW FROM DATABASE")
    except:
        suite.failTest("GET ALL SW FROM DATABASE")
        suite.logFailure(["Error getting all sensitivity weights", "from the database"], "GET ALL SW FROM DATABASE")

    try:
        swData = API.getSw(insertId)
        suite.assertEqual(name, swData[0][0], "ACCURATE STORAGE & RETRIEVAL OF SW FROM DATABASE: NAME")
        suite.assertEqual(mass, swData[0][1], "ACCURATE STORAGE & RETRIEVAL OF SW FROM DATABASE: MASS")
        suite.assertEqual(density, swData[0][2], "ACCURATE STORAGE & RETRIEVAL OF SW FROM DATABASE: DENSITY")
        suite.assertEqual(cce, swData[0][3], "ACCURATE STORAGE & RETRIEVAL OF SW FROM DATABASE: CCE")
    except:
        suite.failTest("GET SELECTED SW FROM DATABASE")
        suite.logFailure(["Error getting selected sensitivity weight", "from the database"], "GET SELECTED SW FROM DATABASE")

    try:
        API.deleteSw(insertId)
        suite.passTest("DELETE SW FROM DATABASE")
    except:
        suite.failTest("DELETE SW FROM DATABASE")
        suite.logFailure(["Error deleting sensitivity weight", "from the database"], "DELETE SW FROM DATABASE")

def test2CrudStatsDb(suite):
    nominal = "1 kg"
    description = "testCrudStatsDb"
    sigw = "0.0062"
    sigt = "0.0081"

    try:
        insertId = API.saveStats(nominal, description, sigw, sigt)
        suite.passTest("SAVE STATISTICS TO DATABASE")
    except:
        suite.failTest("SAVE STATISTICS TO DATABASE")
        suite.logFailure(["Error saving statistics", "to the database"], "SAVE STATISTICS TO DATABASE")
        return

    try:
        statsData = API.getStats()
        suite.passTest("GET ALL STATISTICS FROM DATABASE")
    except:
        suite.failTest("GET ALL STATISTICS FROM DATABASE")
        suite.logFailure(["Error getting all statistics", "from the database"], "GET ALL STATISTICS FROM DATABASE")

    try:
        statData = API.getStat(insertId)
        suite.assertEqual(nominal, statData[0][0], "ACCURATE STORAGE & RETRIEVAL OF STATISTICS FROM DATABASE: NOMINAL")
        suite.assertEqual(sigw, statData[0][1], "ACCURATE STORAGE & RETRIEVAL OF STATISTICS FROM DATABASE: SIGMA-W")
        suite.assertEqual(sigt, statData[0][2], "ACCURATE STORAGE & RETRIEVAL OF STATISTICS FROM DATABASE: SIGMA-T")
    except:
        suite.failTest("GET SELECTED STATISTICS FROM DATABASE")
        suite.logFailure(["Error getting selected statistics", "from the database"], "GET SELECTED STATISTICS FROM DATABASE")

    try:
        API.deleteStat(insertId)
        suite.passTest("DELETE STATISTICS FROM DATABASE")
    except:
        suite.failTest("DELETE STATISTICS FROM DATABASE")
        suite.logFailure(["Error deleting statistics", "from the database"], "DELETE STATISTICS FROM DATABASE")