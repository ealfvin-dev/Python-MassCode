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
    #Test if a report number with a space is caught in Input checks
    try:
        with open("./Testing/MARSTest/Test-FEBadReportNum-config.txt") as file:
            seriesText = file.read()
        
        suite.assertFalse(InputChecks.checkReportNumber(seriesText, suite.sendErrorMock, suite.highlightErrorMock), "REPORT NUMBER FORMAT DETERMINATION -")
    except:
        suite.failTest("REPORT NUMBER FORMAT DETERMINATION -")
        suite.logFailure(["Error running front end input checks"], "REPORT NUMBER FORMAT DETERMINATION -")

def test4FEBadStructure(suite):
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
    #Test if a missed input is caught in Input checks
    try:
        with open("./Testing/MARSTest/Test-FEBlankInput-config.txt") as file:
            text = file.read()
        
        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), "CHECK FOR MISSED INPUT -")
    except:
        suite.failTest("CHECK FOR MISSED INPUT -")
        suite.logFailure(["Error running front end input checks"], "CHECK FOR MISSED INPUT -")

def test7InputNaN(suite):
    #Test if a NaN input is caught in Input checks
    try:
        with open("./Testing/MARSTest/Test-FEInputNaN-config.txt") as file:
            text = file.read()
        
        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), "CHECK FOR NaN INPUT -")
    except:
        suite.failTest("CHECK FOR NaN INPUT -")
        suite.logFailure(["Error running front end input checks"], "CHECK FOR NaN INPUT -")

def test8CheckEqualsRestraint(suite):
    #Test if input file with check position = restraint position is caught by input checks
    try:
        with open("./Testing/MARSTest/Test-FECheckEqualRes-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkRestraints(seriesTexts, 1, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK STANDARD EQUALS RESTRAINT -")
    except:
        suite.failTest("CHECK STANDARD EQUALS RESTRAINT -")
        suite.logFailure(["Error running front end input checks"], "CHECK STANDARD EQUALS RESTRAINT -")

def test9UnequalRestraintPassed(suite):
    #Test if input file with a passed-down restraint that does not match the nominal of the next restraint is caught by input checks
    try:
        with open("./Testing/MARSTest/Test-BadRestraintPassed-config.txt") as file:
            text = file.read()

        seriesTexts = text.split("@SERIES")
        seriesTexts[1] = "@SERIES\n" + seriesTexts[1]

        seriesTexts[1] = seriesTexts[0] + "\n" + seriesTexts[1]
        seriesTexts.pop(0)

        suite.assertFalse(InputChecks.checkRestraints(seriesTexts, 2, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK FOR UNEQUAL RESTRAINTS -")
    except:
        suite.failTest("CHECK FOR UNEQUAL RESTRAINTS -")
        suite.logFailure(["Error running front end input checks"], "CHECK FOR UNEQUAL RESTRAINTS -")

def test10ErrorInPosition(suite):
    #Test if input file with space in weight_id is caught by input checks
    try:
        with open("./Testing/MARSTest/Test-BadPosition-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkInputValues(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock), "POSITION WEIGHT_ID -")
    except:
        suite.failTest("POSITION WEIGHT_ID -")
        suite.logFailure(["Error running front end input checks"], "POSITION WEIGHT_ID -")

def test11BadDesignVectors(suite):
    #Test if input file with bad design vector lengths is caught by input checks
    try:
        with open("./Testing/MARSTest/Test-FEBadDesignVectorLength-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK FOR BAD DESIGN VECTOR LENGTH -")
    except:
        suite.failTest("CHECK FOR BAD DESIGN VECTOR LENGTH -")
        suite.logFailure(["Error running front end input checks"], "CHECK FOR BAD DESIGN VECTOR LENGTH -")

def test12BadRestraintVectors(suite):
    #Test if input file with bad restraint vector lengths is caught by input checks
    try:
        with open("./Testing/MARSTest/Test-FEBadRestraintVectorLength-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK FOR BAD RESTRAINT VECTOR LENGTH -")
    except:
        suite.failTest("CHECK FOR BAD RESTRAINT VECTOR LENGTH -")
        suite.logFailure(["Error running front end input checks"], "CHECK FOR BAD RESTRAINT VECTOR LENGTH -")

def test13BadCheckVectors(suite):
    #Test if input file with bad restraint vector lengths is caught by input checks
    try:
        with open("./Testing/MARSTest/Test-FEBadCheckVectorLength-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK FOR BAD CHECK VECTOR LENGTH -")
    except:
        suite.failTest("CHECK FOR BAD CHECK VECTOR LENGTH -")
        suite.logFailure(["Error running front end input checks"], "CHECK FOR BAD CHECK VECTOR LENGTH -")

def test14BadPassDownVectors(suite):
    #Test if input file with bad restraint vector lengths is caught by input checks
    try:
        with open("./Testing/MARSTest/Test-FEBadPassDownVectorLength-config.txt") as file:
            text = file.read()

        seriesTexts = [text]

        suite.assertFalse(InputChecks.checkVectors(seriesTexts, suite.sendErrorMock, suite.highlightErrorMock, suite.goToSeriesMock), "CHECK FOR BAD PASS DOWN VECTOR LENGTH -")
    except:
        suite.failTest("CHECK FOR BAD PASS DOWN VECTOR LENGTH -")
        suite.logFailure(["Error running front end input checks"], "CHECK FOR BAD PASS DOWN VECTOR LENGTH -")