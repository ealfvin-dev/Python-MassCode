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
        suite.assertTrue(InputChecks.checkRestraints(seriesTexts, 4, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK RESTRAINTS MULTIPLE SERIES INPUT +")
        suite.assertTrue(InputChecks.runSecondaryChecks(seriesTexts, "Test-FEGoodFile", suite.sendErrorMock, suite.highlightErrorMock), "SECONDARY INPUT CHECKS MULTIPLE SERIES INPUT +")
    except:
        suite.failTest("MULTIPLE SERIES INPUT FILE PASSES FE INPUT CHECKS")
        suite.logFailure(["Error running front end input checks on multiple series input"], "MULTIPLE SERIES INPUT FILE PASSES FE INPUT CHECKS")

def test2FEGoodSingleSeries(suite):
    #Test if a correctly-made input file with a single series passes all front end input checks
    try:
        with open("./Testing/MARSTest/Test-FEGoodFile-SingleSeries-config.txt") as file:
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
        suite.assertTrue(InputChecks.checkRestraints(seriesTexts, 1, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK RESTRAINTS SINGLE SERIES INPUT +")
        suite.assertTrue(InputChecks.runSecondaryChecks(seriesTexts, "Test-FEGoodFile-SingleSeries", suite.sendErrorMock, suite.highlightErrorMock), "SECONDARY INPUT CHECKS SINGLE SERIES INPUT +")
    except:
        suite.failTest("SINGLE SERIES INPUT FILE PASSES FE INPUT CHECKS")
        suite.logFailure(["Error running front end input checks on single series input"], "SINGLE SERIES INPUT FILE PASSES FE INPUT CHECKS")

def test3FEBadReportNum(suite):
    testDesc = "REPORT NUMBER FORMAT DETERMINATION -"
    try:
        with open("./Testing/MARSTest/Test-FEBadReportNum-config.txt") as file:
            seriesText = file.read()
        
        suite.assertFalse(InputChecks.checkReportNumber(seriesText, suite.sendErrorMock, suite.highlightErrorMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test4FEBadStructure(suite):
    testDesc = "INPUT FILE STRUCTURE DETERMINATION -"
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
        
        suite.assertFalse(InputChecks.checkStructure(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test5FEBadTags(suite):
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

def test6MissedInput(suite):
    testDesc = "CHECK FOR MISSED INPUT -"
    try:
        with open("./Testing/MARSTest/Test-FEBlankInput-config.txt") as file:
            text = file.read()
        
        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test7InputNaN(suite):
    testDesc = "CHECK FOR NaN INPUT -"
    try:
        with open("./Testing/MARSTest/Test-FEInputNaN-config.txt") as file:
            text = file.read()
        
        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test8CheckEqualsRestraint(suite):
    testDesc = "CHECK STANDARD EQUALS RESTRAINT -"
    try:
        with open("./Testing/MARSTest/Test-FECheckEqualRes-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkRestraints(seriesTexts, 1, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test9UnequalRestraintPassed(suite):
    testDesc = "CHECK FOR UNEQUAL RESTRAINTS -"
    try:
        with open("./Testing/MARSTest/Test-BadRestraintPassed-config.txt") as file:
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
        with open("./Testing/MARSTest/Test-BadPosition-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test11BadDesignVectors(suite):
    testDesc = "CHECK FOR BAD DESIGN VECTOR LENGTH -"
    try:
        with open("./Testing/MARSTest/Test-FEBadDesignVectorLength-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test12BadRestraintVectors(suite):
    testDesc = "CHECK FOR BAD RESTRAINT VECTOR LENGTH -"
    try:
        with open("./Testing/MARSTest/Test-FEBadRestraintVectorLength-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test13BadCheckVectors(suite):
    testDesc = "CHECK FOR BAD CHECK VECTOR LENGTH -"
    try:
        with open("./Testing/MARSTest/Test-FEBadCheckVectorLength-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test14BadPassDownVectors(suite):
    testDesc = "CHECK FOR BAD PASS DOWN VECTOR LENGTH -"
    try:
        with open("./Testing/MARSTest/Test-FEBadPassDownVectorLength-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test15UnequalBalanceObs(suite):
    testDesc = "CHECK FOR UNEQUAL BALANCE OBSERVATIONS -"
    try:
        with open("./Testing/MARSTest/Test-UnEqualBalObs-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkNumObservations(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)

def test16UnequalEnvObs(suite):
    testDesc = "CHECK FOR UNEQUAL ENV OBSERVATIONS -"
    try:
        with open("./Testing/MARSTest/Test-UnEqualEnvObs-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkNumObservations(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Error running front end input checks"], testDesc)