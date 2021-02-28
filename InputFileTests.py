import InputChecks
from os import path

def test01FEGoodFile(suite):
    #Test if a correctly-made input file passes all front end input checks
    try:
        with open(path.join("TestFiles", "Test-FEGoodFile-config.txt")) as file:
            text = file.read()

        seriesTexts = text.split("@SERIES")
        seriesTexts[1] = "@SERIES\n" + seriesTexts[1]
        seriesTexts[2] = "@SERIES\n" + seriesTexts[2]
        seriesTexts[3] = "@SERIES\n" + seriesTexts[3]
        seriesTexts[4] = "@SERIES\n" + seriesTexts[4]

        seriesTexts[1] = seriesTexts[0] + "\n" + seriesTexts[1]
        seriesTexts.pop(0)
        
        suite.assertTrue(InputChecks.determineIfDirectReadings(seriesTexts[0]), "DIRECT READING DETERMINATION MULTIPLE SERIES INPUT +")
        suite.assertFalse(InputChecks.determineIfDirectReadings(seriesTexts[1]), "DIRECT READING DETERMINATION MULTIPLE SERIES INPUT -")
        suite.assertTrue(InputChecks.checkReportNumber(seriesTexts[0], suite.sendErrorMock, suite.highlightErrorMock), "REPORT NUMBER FORMAT DETERMINATION MULTIPLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkStructure(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "FILE STRUCTURE DETERMINATION MULTIPLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkTags(seriesTexts, False, suite.highlightErrorMock, suite.sendErrorMock), "CHECK INPUT TAGS MULTIPLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkIfAllTags(seriesTexts, suite.sendErrorMock, suite.goToSeriesMock), "CHECK IF ALL INPUT TAGS MULTIPLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkForRepeats(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), "CHECK FOR REPEATED TAGS MULTIPLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), "CHECK INPUT VALUES MULTIPLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkNumObservations(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK NUMBER OBS MULTIPLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK VECTORS MULTIPLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkDesignVsWeights(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK DESIGN MULTIPLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkRestraints(seriesTexts, 4, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK RESTRAINTS MULTIPLE SERIES INPUT +")
        suite.assertTrue(InputChecks.runSecondaryChecks(seriesTexts, "Test-FEGoodFile", suite.sendErrorMock, suite.highlightErrorMock), "SECONDARY INPUT CHECKS MULTIPLE SERIES INPUT +")
    except:
        suite.failTest("MULTIPLE SERIES INPUT FILE PASSES FE INPUT CHECKS")
        suite.logFailure(["Error running front end input checks on multiple series input"], "MULTIPLE SERIES INPUT FILE PASSES FE INPUT CHECKS")

def test02FEGoodSingleSeries(suite):
    #Test if a correctly-made input file with a single series passes all front end input checks
    try:
        with open(path.join("TestFiles", "Test-FEGoodFile-SingleSeries-config.txt")) as file:
            text = file.read()

        seriesTexts = [text]
        
        suite.assertTrue(InputChecks.determineIfDirectReadings(seriesTexts[0]), "DIRECT READING DETERMINATION SINGLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkReportNumber(seriesTexts[0], suite.sendErrorMock, suite.highlightErrorMock), "REPORT NUMBER FORMAT DETERMINATION SINGLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkStructure(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "FILE STRUCTURE DETERMINATION SINGLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkTags(seriesTexts, False, suite.highlightErrorMock, suite.sendErrorMock), "CHECK INPUT TAGS SINGLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkIfAllTags(seriesTexts, suite.sendErrorMock, suite.goToSeriesMock), "CHECK IF ALL INPUT TAGS SINGLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkForRepeats(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), "CHECK FOR REPEATED TAGS SINGLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), "CHECK INPUT VALUES SINGLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkNumObservations(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK NUMBER OBS SINGLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK VECTORS SINGLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkDesignVsWeights(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK DESIGN SINGLE SERIES INPUT +")
        suite.assertTrue(InputChecks.checkRestraints(seriesTexts, 1, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK RESTRAINTS SINGLE SERIES INPUT +")
        suite.assertTrue(InputChecks.runSecondaryChecks(seriesTexts, "Test-FEGoodFile-SingleSeries", suite.sendErrorMock, suite.highlightErrorMock), "SECONDARY INPUT CHECKS SINGLE SERIES INPUT +")
    except:
        suite.failTest("SINGLE SERIES INPUT FILE PASSES FE INPUT CHECKS")
        suite.logFailure(["Error running front end input checks on single series input"], "SINGLE SERIES INPUT FILE PASSES FE INPUT CHECKS")

def test03FEBadReportNum(suite):
    testDesc = "REPORT NUMBER FORMAT DETERMINATION -"
    try:
        with open(path.join("TestFiles", "Test-FEBadReportNum-config.txt")) as file:
            seriesText = file.read()
        
        suite.assertFalse(InputChecks.checkReportNumber(seriesText, suite.sendErrorMock, suite.highlightErrorMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test04FEBadStructure(suite):
    testDesc = "INPUT FILE STRUCTURE DETERMINATION -"
    try:
        with open(path.join("TestFiles", "Test-FEGoodFile-config.txt")) as file:
            text = file.read()

        seriesTexts = text.split("@SERIES")
        seriesTexts[1] = "@SERIES\n" + seriesTexts[1]
        seriesTexts[2] = "@SERIES\n" + seriesTexts[2]
        seriesTexts[3] = "@SERIES\n" + seriesTexts[3]
        #seriesTexts[4] = "@SERIES\n" + seriesTexts[4] -> Missing @SERIES in the last series

        seriesTexts[1] = seriesTexts[0] + "\n" + seriesTexts[1]
        seriesTexts.pop(0)
        
        suite.assertFalse(InputChecks.checkStructure(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test05FEBadTags(suite):
    #Test if unrecognized, duplicate, missing tags are found by Input checks
    try:
        with open(path.join("TestFiles", "Test-FEBadTags-config.txt")) as file:
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

def test06MissedInput(suite):
    testDesc = "CHECK FOR MISSED INPUT -"
    try:
        with open(path.join("TestFiles", "Test-FEBlankInput-config.txt")) as file:
            text = file.read()
        
        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test07InputNaN(suite):
    testDesc = "CHECK FOR NaN INPUT -"
    try:
        with open(path.join("TestFiles", "Test-FEInputNaN-config.txt")) as file:
            text = file.read()
        
        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test08CheckEqualsRestraint(suite):
    testDesc = "CHECK STANDARD EQUALS RESTRAINT -"
    try:
        with open(path.join("TestFiles", "Test-FECheckEqualRes-config.txt")) as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkRestraints(seriesTexts, 1, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test09UnequalRestraintPassed(suite):
    testDesc = "CHECK FOR UNEQUAL RESTRAINTS -"
    try:
        with open(path.join("TestFiles", "Test-BadRestraintPassed-config.txt")) as file:
            text = file.read()

        seriesTexts = text.split("@SERIES")
        seriesTexts[1] = "@SERIES\n" + seriesTexts[1]

        seriesTexts[1] = seriesTexts[0] + "\n" + seriesTexts[1]
        seriesTexts.pop(0)

        suite.assertFalse(InputChecks.checkRestraints(seriesTexts, 2, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test10ErrorInPosition(suite):
    testDesc = "POSITION WEIGHT_ID -"
    try:
        with open(path.join("TestFiles", "Test-BadPosition-config.txt")) as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test11BadDesignVectors(suite):
    testDesc = "CHECK FOR BAD DESIGN VECTOR LENGTH -"
    try:
        with open(path.join("TestFiles", "Test-FEBadDesignVectorLength-config.txt")) as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test12BadRestraintVectors(suite):
    testDesc = "CHECK FOR BAD RESTRAINT VECTOR LENGTH -"
    try:
        with open(path.join("TestFiles", "Test-FEBadRestraintVectorLength-config.txt")) as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test13BadCheckVectors(suite):
    testDesc = "CHECK FOR BAD CHECK VECTOR LENGTH -"
    try:
        with open(path.join("TestFiles", "Test-FEBadCheckVectorLength-config.txt")) as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test14BadPassDownVectors(suite):
    testDesc = "CHECK FOR BAD PASS DOWN VECTOR LENGTH -"
    try:
        with open(path.join("TestFiles", "Test-FEBadPassDownVectorLength-config.txt")) as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test15UnequalBalanceObs(suite):
    testDesc = "CHECK FOR UNEQUAL BALANCE OBSERVATIONS -"
    try:
        with open(path.join("TestFiles", "Test-UnEqualBalObs-config.txt")) as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkNumObservations(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test16UnequalEnvObs(suite):
    testDesc = "CHECK FOR UNEQUAL ENV OBSERVATIONS -"
    try:
        with open(path.join("TestFiles", "Test-UnEqualEnvObs-config.txt")) as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkNumObservations(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test17BadDesignLine(suite):
    testDesc = "CHECK FOR INCOMPATIBLE DESIGN LINE -"
    try:
        with open(path.join("TestFiles", "Test-FEBadDesignLine-config.txt")) as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkDesignVsWeights(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)