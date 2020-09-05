import InputChecks

def test1FEGoodFile(suite):
    #Test if a correctly-made input file passes all front end input checks
    try:
        with open("./Testing/MARSTest/Test-FEGoodFile-config.txt") as file:
            text = file.read()

        seriesTexts = text.split("@SERIES")
        seriesTexts[1] = "@SERIES\n" + seriesTexts[1]
        seriesTexts[2] = "@SERIES\n" + seriesTexts[2]
        seriesTexts[3] = "@SERIES\n" + seriesTexts[3]
        seriesTexts[4] = "@SERIES\n" + seriesTexts[4]

        seriesTexts[1] = seriesTexts[0] + "\n" + seriesTexts[1]
        seriesTexts.pop(0)
        
        suite.assertTrue(InputChecks.determineIfDirectReadings(seriesTexts[0]), "DIRECT READING DETERMINATION +")
        suite.assertFalse(InputChecks.determineIfDirectReadings(seriesTexts[1]), "DIRECT READING DETERMINATION -")
        suite.assertTrue(InputChecks.checkReportNumber(seriesTexts[0], suite.sendErrorMock, suite.highlightErrorMock), "REPORT NUMBER FORMAT DETERMINATION +")
        suite.assertTrue(InputChecks.checkStructure(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "FILE STRUCTURE DETERMINATION +")
        suite.assertTrue(InputChecks.checkTags(seriesTexts, False, suite.highlightErrorMock, suite.sendErrorMock), "CHECK INPUT TAGS +")
        suite.assertTrue(InputChecks.checkIfAllTags(seriesTexts, suite.sendErrorMock, suite.goToSeriesMock), "CHECK IF ALL INPUT TAGS +")
        suite.assertTrue(InputChecks.checkForRepeats(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), "CHECK FOR REPEATED TAGS +")
        suite.assertTrue(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), "CHECK INPUT VALUES +")
        suite.assertTrue(InputChecks.runRequiredChecks(seriesTexts, 4, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "REQUIRED INPUT CHECKS +")
        suite.assertTrue(InputChecks.runSecondaryChecks(seriesTexts, "Test-FEGoodFile", suite.sendErrorMock, suite.highlightErrorMock), "SECONDARY INPUT CHECKS +")
    except:
        suite.failTest("GOOD FILE PASSES FE INPUT CHECKS")
        suite.logFailure(["Error running front end input checks"], "GOOD FILE PASSES FE INPUT CHECKS")

def test2FEBadReportNum(suite):
    #Test if a report number with a space is caught in Input checks
    try:
        with open("./Testing/MARSTest/Test-FEBadReportNum-config.txt") as file:
            seriesText = file.read()
        
        suite.assertFalse(InputChecks.checkReportNumber(seriesText, suite.sendErrorMock, suite.highlightErrorMock), "REPORT NUMBER FORMAT DETERMINATION -")
    except:
        suite.failTest("REPORT NUMBER FORMAT DETERMINATION -")
        suite.logFailure(["Error running front end input checks"], "REPORT NUMBER FORMAT DETERMINATION -")

def test3FEBadStructure(suite):
    #Test if an input file missing a @SERIES is caught in Input checks
    try:
        with open("./Testing/MARSTest/Test-FEGoodFile-config.txt") as file:
            text = file.read()

        seriesTexts = text.split("@SERIES")
        seriesTexts[1] = "@SERIES\n" + seriesTexts[1]
        seriesTexts[2] = "@SERIES\n" + seriesTexts[2]
        seriesTexts[3] = "@SERIES\n" + seriesTexts[3]
        #seriesTexts[4] = "@SERIES\n" + seriesTexts[4] -> Missing @SERIES in the last series

        seriesTexts[1] = seriesTexts[0] + "\n" + seriesTexts[1]
        seriesTexts.pop(0)
        
        suite.assertFalse(InputChecks.checkStructure(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "FILE STRUCTURE DETERMINATION -")
    except:
        suite.failTest("INPUT STRUCTURE DETERMINATION -")
        suite.logFailure(["Error running front end input checks"], "INPUT STRUCTURE DETERMINATION -")

def test4FEBadTags(suite):
    #Test if unrecognized, duplicate, missing tags are found by Input checks
    try:
        with open("./Testing/MARSTest/Test-FEBadTags-config.txt") as file:
            text = file.read()

        seriesTexts = text.split("@SERIES")
        seriesTexts[1] = "@SERIES\n" + seriesTexts[1]
        seriesTexts[2] = "@SERIES\n" + seriesTexts[2]
        seriesTexts[3] = "@SERIES\n" + seriesTexts[3]
        seriesTexts[4] = "@SERIES\n" + seriesTexts[4]

        seriesTexts[1] = seriesTexts[0] + "\n" + seriesTexts[1]
        seriesTexts.pop(0)
        
        suite.assertFalse(InputChecks.checkTags(seriesTexts, False, suite.highlightErrorMock, suite.sendErrorMock), "CHECK INPUT TAGS -")
        suite.assertFalse(InputChecks.checkIfAllTags(seriesTexts, suite.sendErrorMock, suite.goToSeriesMock), "CHECK IF ALL INPUT TAGS -")
        suite.assertFalse(InputChecks.checkForRepeats(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), "CHECK FOR REPEATED TAGS -")
    except:
        suite.failTest("TAG DETERMINATIONS -")
        suite.logFailure(["Error running front end input checks"], "TAG DETERMINATIONS -")

def test5MissedInput(suite):
    #Test if a missed input is caught in Input checks
    try:
        with open("./Testing/MARSTest/Test-FEBlankInput-config.txt") as file:
            text = file.read()
        
        seriesTexts = text.split("@SERIES")
        seriesTexts[1] = "@SERIES\n" + seriesTexts[1]

        seriesTexts[1] = seriesTexts[0] + "\n" + seriesTexts[1]
        seriesTexts.pop(0)

        suite.assertFalse(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), "CHECK FOR MISSED INPUT -")
    except:
        suite.failTest("CHECK FOR MISSED INPUT -")
        suite.logFailure(["Error running front end input checks"], "CHECK FOR MISSED INPUT -")

def test6InputNaN(suite):
    #Test if a NaN input is caught in Input checks
    try:
        with open("./Testing/MARSTest/Test-FEInputNaN-config.txt") as file:
            text = file.read()
        
        seriesTexts = text.split("@SERIES")
        seriesTexts[1] = "@SERIES\n" + seriesTexts[1]

        seriesTexts[1] = seriesTexts[0] + "\n" + seriesTexts[1]
        seriesTexts.pop(0)

        suite.assertFalse(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), "CHECK FOR NaN INPUT -")
    except:
        suite.failTest("CHECK FOR NaN INPUT -")
        suite.logFailure(["Error running front end input checks"], "CHECK FOR NaN INPUT -")