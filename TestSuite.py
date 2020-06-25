import RunFile
import TestBase
import sys
import os

class TestSuite(TestBase.TestBase):
    def testKivy(self):
        #Test if Kivy can import
        try:
            import kivy

            self.passTest("IMPORT KIVY")
        except:
            self.failTest("IMPORT KIVY")

    def testRunFile(self):
        #Test if config file can be run and output file can be written
        try:
            data = RunFile.run("./Testing/PyMacTest/Test0-AirDensity-config.txt", False)
            self.passTest("RUN TEST FILE")
        except:
            self.failTest("RUN TEST FILE")

    def testWriteOutFile(self):
        #Test if output file can be written
        try:
            data = RunFile.run("./Testing/PyMacTest/Test0-AirDensity-config.txt")
            self.passTest("WRITE OUT FILE")
        except:
            self.failTest("WRITE OUT FILE")

        if(os.path.exists("Test0-AirDensity-out.txt")):
            os.remove("Test0-AirDensity-out.txt")

    def testAirDesities(self):
        #Test if calculated air densities match expected
        try:
            data = RunFile.run("./Testing/PyMacTest/Test0-AirDensity-config.txt", False)
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
            self.failTest("AIR DENSITIES WERE NOT CALCULATED")

    def testOutFileData(self):
        #Test writing stuff into output file
        try:
            data = RunFile.run("./Testing/PyMacTest/Test2-config.txt")

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
            inputSw = round(data[0].sigmaW, 6)
            calculatedFcrit = round(data[0].fCritical, 2)
            calculatedFvalue = round(data[0].fValue, 2)
            calculatedCheckStd = round(data[0].calculatedCheckCorrection, 6)
            calculatedTcrit = round(data[0].tCritical, 2)
            calculatedTvalue = round(data[0].tValue, 2)

            inputDensities = []
            inputAcceptedCSCorr = 0.0

            expectedMasses = data[0].calculatedMasses[0]

            #Pull useful stuff out of output file
            with open("Test2-out.txt", 'r') as outFile:
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
            with open("./Testing/PyMacTest/Test2-config.txt", 'r') as configFile:
                for line in configFile:
                    m = line.strip().split()
                    if(m == [] or m[0] == "\n"):
                        continue
                    if(m[0] == "<Position>"):
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
            self.failTest("ERROR IN RUN/OUTPUT REPORT GENERATION")

        if(os.path.exists("Test2-out.txt")):
            os.remove("Test2-out.txt")

    def testNonInvertible(self):
        pass

    #Test non-invertible matrix throws error
    #Test other data entry errors throw errors (from fe and be?)

    def runAll(self):
        self.testKivy()
        self.testRunFile()
        self.testWriteOutFile()
        self.testAirDesities()
        self.testOutFileData()
        self.printSummary()

    def runFromFE(self):
        self.passTest("IMPORT KIVY")
        self.testRunFile()
        self.testWriteOutFile()
        self.testAirDesities()
        self.testOutFileData()
        return self.returnSummary()

if(__name__ == "__main__"):
    suite = TestSuite()
    suite.runAll()