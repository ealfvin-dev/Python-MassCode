import TestBase
import RunFile
import InputChecks
from MARSException import MARSException
import sys
import os

class TestSuite(TestBase.TestBase):
    #Mocked functions
    def sendErrorMock(self, message):
        pass

    def highlightErrorMock(self, series, startLine, endLine=None):
        pass

    def goToSeriesMock(self, seriesNum, exists):
        pass

    def testPythonVersion(self):
        #Assert current version of python >= 3.5
        try:
            assert sys.version_info >= (3, 5)
            self.passTest("PYTHON VERSION")
        except AssertionError:
            self.failTest("PYTHON VERSION")
            self.logFailure(["Requires Python >= 3.5", str(sys.version_info)], "PYTHON VERSION")

    def testNumpy(self):
        #Test if Numpy can import, check version
        try:
            import numpy
            self.passTest("IMPORT NUMPY")
            self.assertEqual(numpy.__version__, '1.17.2', "NUMPY VERSION")
        except:
            self.failTest("IMPORT NUMPY")
            self.logFailure(["Could not import Numpy"], "IMPORT NUMPY")

    def testSciPy(self):
        #Test if SciPy can import, check version
        try:
            import scipy
            self.passTest("IMPORT SCIPY")
            self.assertEqual(scipy.__version__, '1.3.1', "SCIPY VERSION")
        except:
            self.failTest("IMPORT SCIPY")
            self.logFailure(["Could not import SciPy"], "IMPORT SCIPY")

    def testKivy(self):
        #Test if Kivy can import
        try:
            import kivy
            self.passTest("IMPORT KIVY")
        except:
            self.failTest("IMPORT KIVY")
            self.logFailure(["Could not import Kivy"], "IMPORT KIVY")

    def testRunFile(self):
        #Test if config file can be run
        try:
            data = RunFile.run("./Testing/MARSTest/Test-FEGoodFile-config.txt", False)
            self.passTest("RUN TEST FILE")
        except:
            self.failTest("RUN TEST FILE")
            self.logFailure(["Could not run test file"], "RUN TEST FILE")

    def testNonInvertible(self):
        #Test non-invertible matrix raises MARSException
        try:
            data = RunFile.run("./Testing/MARSTest/Test-NonInvertible-config.txt", False)
            self.failTest("NON-INVERTIBLE MATRIX RAISES MARSEXCEPTION")
            self.logFailure(["Non-invertible matrix did not raise MARSException"], "NON-INVERTIBLE MATRIX RAISES MARSEXCEPTION")
        except MARSException:
            self.passTest("NON-INVERTIBLE MATRIX RAISES MARSEXCEPTION")
        except:
            self.failTest("NON-INVERTIBLE MATRIX RAISES MARSEXCEPTION")
            self.logFailure(["Non-invertible matrix did not raise MARSException"], "NON-INVERTIBLE MATRIX RAISES MARSEXCEPTION")

    def testUnequalBalanceObs(self):
        #Test if balance readings != observations raises MARSException
        try:
            data = RunFile.run("./Testing/MARSTest/Test-UnEqualBalObs-config.txt", False)
            self.failTest("UNEQUAL BALANCE OBSERVATIONS RAISES MARSEXCEPTION")
            self.logFailure(["Unequal balance observations did not raise MARSException"], "UNEQUAL BALANCE OBSERVATIONS RAISES MARSEXCEPTION")
        except MARSException:
            self.passTest("UNEQUAL BALANCE OBSERVATIONS RAISES MARSEXCEPTION")
        except:
            self.failTest("UNEQUAL BALANCE OBSERVATIONS RAISES MARSEXCEPTION")
            self.logFailure(["Unequal balance observations did not raise MARSException"], "UNEQUAL BALANCE OBSERVATIONS RAISES MARSEXCEPTION")

    def testUnequalEnvObs(self):
        #Test if environmental readings != observations raises MARSException
        try:
            data = RunFile.run("./Testing/MARSTest/Test-UnEqualEnvObs-config.txt", False)
            self.failTest("UNEQUAL ENVIRONMENTAL OBSERVATIONS RAISES MARSEXCEPTION")
            self.logFailure(["Unequal environmental observations did not raise MARSException"], "UNEQUAL ENVIRONMENTAL OBSERVATIONS RAISES MARSEXCEPTION")
        except MARSException:
            self.passTest("UNEQUAL ENVIRONMENTAL OBSERVATIONS RAISES MARSEXCEPTION")
        except:
            self.failTest("UNEQUAL ENVIRONMENTAL OBSERVATIONS RAISES MARSEXCEPTION")
            self.logFailure(["Unequal environmental observations did not raise MARSException"], "UNEQUAL ENVIRONMENTAL OBSERVATIONS RAISES MARSEXCEPTION")

    def testNoRestraintPassed(self):
        #Test if no restraint passed to series raises MARSException
        try:
            data = RunFile.run("./Testing/MARSTest/Test-NoRestraintPassed-config.txt", False)
            self.failTest("NO RESTRAINT PASSED RAISES MARSEXCEPTION")
            self.logFailure(["No restraint passed down did not raise MARSException"], "NO RESTRAINT PASSED RAISES MARSEXCEPTION")
        except MARSException:
            self.passTest("NO RESTRAINT PASSED RAISES MARSEXCEPTION")
        except:
            self.failTest("NO RESTRAINT PASSED RAISES MARSEXCEPTION")
            self.logFailure(["No restraint passed down did not raise MARSException"], "NO RESTRAINT PASSED RAISES MARSEXCEPTION")

    def testZeroHeight(self):
        #Test if height of 0 raisesMARSException
        try:
            data = RunFile.run("./Testing/MARSTest/Test-ZeroHeight-config.txt", False)
            self.failTest("HEIGHT OF 0 RAISES MARSEXCEPTION")
            self.logFailure(["Weight height of 0 did not raise MARSException"], "NO RESTRAINT PASSED RAISES MARSEXCEPTION")
        except MARSException:
            self.passTest("HEIGHT OF 0 RAISES MARSEXCEPTION")
        except:
            self.failTest("HEIGHT OF 0 RAISES MARSEXCEPTION")
            self.logFailure(["Weight height of 0 did not raise MARSException"], "HEIGHT OF 0 RAISES MARSEXCEPTION")

    def testFEGoodFile(self):
        #Test if a correctly-made input file passes front end input checks
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
            
            self.assertTrue(InputChecks.determineIfDirectReadings(seriesTexts[0]), "DIRECT READING DETERMINATION +")
            self.assertFalse(InputChecks.determineIfDirectReadings(seriesTexts[1]), "DIRECT READING DETERMINATION -")
            self.assertTrue(InputChecks.checkReportNumber(seriesTexts[0], self.sendErrorMock, self.highlightErrorMock), "REPORT NUMBER FORMAT DETERMINATION +")
            self.assertTrue(InputChecks.checkStructure(seriesTexts, self.sendErrorMock, self.highlightErrorMock, self.goToSeriesMock), "FILE STRUCTURE DETERMINATION +")
            self.assertTrue(InputChecks.checkTags(seriesTexts, False, self.highlightErrorMock, self.sendErrorMock), "CHECK INPUT TAGS +")
            self.assertTrue(InputChecks.checkIfAllTags(seriesTexts, self.sendErrorMock, self.goToSeriesMock), "CHECK IF ALL INPUT TAGS +")
            self.assertTrue(InputChecks.checkForRepeats(seriesTexts, self.sendErrorMock, self.highlightErrorMock), "CHECK FOR REPEATED TAGS +")
            self.assertTrue(InputChecks.runRequiredChecks(seriesTexts, 4, self.sendErrorMock, self.highlightErrorMock, self.goToSeriesMock), "REQUIRED INPUT CHECKS +")
            self.assertTrue(InputChecks.runSecondaryChecks(seriesTexts, "Test-FEGoodFile", self.sendErrorMock, self.highlightErrorMock), "SECONDARY INPUT CHECKS +")
        except:
            self.failTest("GOOD FILE PASSES FE INPUT CHECKS")
            self.logFailure(["Error running front end input checks"], "GOOD FILE PASSES FE INPUT CHECKS")

    def testFEBadReportNum(self):
        #Test if a report number with a space is caught in Input checks
        try:
            with open("./Testing/MARSTest/Test-FEBadReportNum-config.txt") as file:
                seriesText = file.read()
            
            self.assertFalse(InputChecks.checkReportNumber(seriesText, self.sendErrorMock, self.highlightErrorMock), "REPORT NUMBER FORMAT DETERMINATION -")
        except:
            self.failTest("REPORT NUMBER FORMAT DETERMINATION -")
            self.logFailure(["Error running front end input checks"], "REPORT NUMBER FORMAT DETERMINATION -")

    def testFEBadStructure(self):
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
            
            self.assertFalse(InputChecks.checkStructure(seriesTexts, self.sendErrorMock, self.highlightErrorMock, self.goToSeriesMock), "FILE STRUCTURE DETERMINATION -")
        except:
            self.failTest("INPUT STRUCTURE DETERMINATION -")
            self.logFailure(["Error running front end input checks"], "INPUT STRUCTURE DETERMINATION -")

    def testFEBadTags(self):
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
            
            self.assertFalse(InputChecks.checkTags(seriesTexts, False, self.highlightErrorMock, self.sendErrorMock), "CHECK INPUT TAGS -")
            self.assertFalse(InputChecks.checkIfAllTags(seriesTexts, self.sendErrorMock, self.goToSeriesMock), "CHECK IF ALL INPUT TAGS -")
            self.assertFalse(InputChecks.checkForRepeats(seriesTexts, self.sendErrorMock, self.highlightErrorMock), "CHECK FOR REPEATED TAGS -")
        except:
            self.failTest("TAG DETERMINATIONS -")
            self.logFailure(["Error running front end input checks"], "TAG DETERMINATIONS -")

    def testWriteOutFile(self):
        #Test if output file can be written out
        try:
            data = RunFile.run("./Testing/MARSTest/Test-Writeout-config.txt")
            if(os.path.exists("Test-Writeout-out.txt")):
                self.passTest("WRITE OUT FILE")
            else:
                self.failTest("WRITE OUT FILE")
                self.logFailure(["Could not write out test file"], "WRITE OUT FILE")
        except:
            self.failTest("WRITE OUT FILE")
            self.logFailure(["Could not write out test file"], "WRITE OUT FILE")

        if(os.path.exists("Test-Writeout-out.txt")):
            os.remove("Test-Writeout-out.txt")

    def testOutFileData(self):
        #Test writing stuff into output file
        try:
            data = RunFile.run("./Testing/MARSTest/Test-Writeout-config.txt")

            outFileDensities = []
            outFileMasses = []
            outFilesw = 0.0
            outFileswAccepted = 0.0
            outFileFcrit = 0.0
            outFileFvalue = 0.0
            outFileCheckStd = 0.0
            outFileCheckStdAccepted = 0.0
            outFileTcrit = 0.0
            outFileTvalue = 0.0

            calculatedSw = round(data[0].swObs, 6)
            calculatedFcrit = round(data[0].fCritical, 2)
            calculatedFvalue = round(data[0].fValue, 2)
            calculatedCheckStd = round(data[0].calculatedCheckCorrection, 6)
            calculatedTcrit = round(data[0].tCritical, 2)
            calculatedTvalue = round(data[0].tValue, 2)

            inputDensities = []
            inputSw = 0.0
            inputAcceptedCSCorr = 0.0

            expectedMasses = data[0].calculatedMasses[0]

            #Pull useful stuff out of output file
            with open("Test-Writeout-out.txt", 'r') as outFile:
                for line in outFile:
                    m = line.strip().split()
                    if(m == [] or m[0] == "\n"):
                        continue

                    if(m[0] == "W500g" or m[0] == "W300g" or m[0] == "W200g" or m[0] == "W100g" or m[0] == "P100g" or m[0] == "Wsum"):
                        outFileMasses.append(float(m[4]))
                        outFileDensities.append(float(m[2]))
                    elif(m[0] == "ACCEPTED_SW"):
                        outFileswAccepted = float(m[2])
                    elif(m[0] == "OBSERVED_SW"):
                        outFilesw = float(m[2])
                    elif(m[0] == "CRITICAL_F-VALUE"):
                        outFileFcrit = float(m[2])
                    elif(m[0] == "OBSERVED_F-VALUE"):
                        outFileFvalue = float(m[2])
                    elif(m[0] == "ACCEPTED_CHECK_STANDARD_CORRECTION"):
                        outFileCheckStdAccepted = float(m[2])
                    elif(m[0] == "OBSERVED_CHECK_STANDARD_CORRECTION"):
                        outFileCheckStd = float(m[2])
                    elif(m[0] == "CRITICAL_T-VALUE"):
                        outFileTcrit = float(m[2])
                    elif(m[0] == "OBSERVED_T-VALUE"):
                        outFileTvalue = float(m[2])

            #Pull useful stuff out of input file
            with open("./Testing/MARSTest/Test-Writeout-config.txt", 'r') as configFile:
                for line in configFile:
                    m = line.strip().split()
                    if(m == [] or m[0] == "\n"):
                        continue
                    elif(m[0] == "<Sigma-w>"):
                        inputSw = float(m[1])
                    elif(m[0] == "<Position>"):
                        inputDensities.append(float(m[3]))
                        if(m[1] == "P100g"):
                            inputAcceptedCSCorr = float(m[5])

            #Test if calculated masses match masses written into the output file and that the rounding is handled correctly. Not testing acuracy of results yet
            for i in range(len(expectedMasses)):
                self.assertEqual(outFileMasses[i], round(expectedMasses[i], 8), "DATA WRITING TO OUTPUT FILE MASS CHECK " + str(i + 1))

            #Test if densities in output file match input
            for i in range(len(inputDensities)):
                self.assertEqual(inputDensities[i], outFileDensities[i], "DATA WRITING TO OUTPUT FILE DENSITY CHECK " + str(i + 1))

            #Test if statistics were written out correctly
            self.assertEqual(outFilesw, calculatedSw, "DATA WRITING TO OUTPUT FILE SW OBSERVED")
            self.assertEqual(outFileswAccepted, inputSw, "DATA WRITING TO OUTPUT FILE SW ACCEPTED")
            self.assertEqual(outFileFcrit, calculatedFcrit, "DATA WRITING TO OUTPUT FILE F-CRITICAL")
            self.assertEqual(outFileFvalue, calculatedFvalue, "DATA WRITING TO OUTPUT FILE F-VALUE")
            self.assertEqual(outFileCheckStd, calculatedCheckStd, "DATA WRITING TO OUTPUT FILE CALCULATED CHECK STANDARD CORRECTION")
            self.assertEqual(outFileCheckStdAccepted, inputAcceptedCSCorr, "DATA WRITING TO OUTPUT FILE ACCEPTED CHECK STANDARD CORRECTION")
            self.assertEqual(outFileTcrit, calculatedTcrit, "DATA WRITING TO OUTPUT FILE T-CRITICAL")
            self.assertEqual(outFileTvalue, calculatedTvalue, "DATA WRITING TO OUTPUT FILE T-VALUE")

        except:
            self.failTest("OUTPUT FILE DATA")
            self.logFailure(["Error in run/output report generation"], "OUTPUT FILE DATA")

        if(os.path.exists("Test-Writeout-out.txt")):
            os.remove("Test-Writeout-out.txt")

    def testAirDesities(self):
        #Test if calculated air densities match expected
        try:
            data = RunFile.run("./Testing/MARSTest/Test-AirDensity-config.txt", False)
            calculatedDesities = data[0].airDensities

            expectedDensities = [0.0011627477621149957,\
                0.0011319900687371933,\
                0.0012102483268084932,\
                0.001226150777103154,\
                0.001165592451710878,\
                0.001180867465458547,\
                0.0011528885073334091,\
                0.00123707837957592,\
                0.0012113502660840957,\
                0.0011909600963592097,\
                0.0011842805431003785,\
                0.0010969698894584734]

            for i in range(len(expectedDensities)):
                self.assertClose(expectedDensities[i], calculatedDesities[i], 1e-8, "AIR DENSITY CALC " + str(i + 1))

        except:
            self.failTest("CALCULATE AIR DENSITIES")
            self.logFailure(["Air densities were not calculated"], "CALCULATE AIR DENSITIES")

    #Test other data entry errors throw errors (from fe and be?)

    def runAll(self):
        self.testPythonVersion()
        #self.testNumpy()
        #self.testSciPy()
        self.testKivy()
        self.testRunFile()
        self.testNonInvertible()
        self.testUnequalBalanceObs()
        self.testUnequalEnvObs()
        self.testNoRestraintPassed()
        self.testZeroHeight()
        self.testFEGoodFile()
        self.testFEBadReportNum()
        self.testFEBadStructure()
        self.testFEBadTags()
        self.testWriteOutFile()
        self.testOutFileData()
        self.testAirDesities()
        self.printSummary()

    def runFromFE(self):
        self.testPythonVersion()
        #self.testNumpy()
        #self.testSciPy()
        self.passTest("IMPORT KIVY")
        self.testRunFile()
        self.testNonInvertible()
        self.testUnequalBalanceObs()
        self.testUnequalEnvObs()
        self.testNoRestraintPassed()
        self.testZeroHeight()
        self.testFEGoodFile()
        self.testFEBadReportNum()
        self.testFEBadStructure()
        self.testFEBadTags()
        self.testWriteOutFile()
        self.testOutFileData()
        self.testAirDesities()
        return self.returnSummary()

if(__name__ == "__main__"):
    suite = TestSuite()
    suite.runAll()