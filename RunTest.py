import RunFile
import numpy as np
import sys
import os

class TestSuite():
    def __init__(self):
        self.expectedNumTests = 27
        self.testNum = 1
        self.passed = 0
        self.failed = 0

        self.longOutput = ""

        self.passedTests = []
        self.failedTests = []

    def passTest(self, testName):
        self.passed += 1
        self.passedTests.append("TEST " + str(self.testNum) + " - " + testName)
        self.longOutput += "\n" + testName + ".........PASS"
        self.testNum += 1

    def failTest(self, testName):
        self.failed += 1
        self.failedTests.append("TEST " + str(self.testNum) + " - " + testName)
        self.longOutput += "\n" + testName + ".........FAIL"
        self.testNum += 1

    def printSummary(self):
        summary = "\n############## TESTING SUITE ##############\n"

        summary += self.longOutput + "\n"

        summary += "\nTESTS PASSED:\n\n"
        summary += "    " + "\n    ".join(self.passedTests) + "\n"
        summary += "\n\nTESTS FAILED:\n\n"
        summary += "    " + "\n    ".join(self.failedTests) + "\n"

        summary += "\n*** RAN " + str(self.passed + self.failed) + "/" + str(self.expectedNumTests) + " TESTS ***\n\n"
        summary += str(self.passed) + " PASSED\n"+str(self.failed) + " FAILED\n\n"

        return summary

    def testKivy(self):
        #Test if Kivy can be imported
        self.longOutput += "\n\n###RUNNING IMPORT KIVY...\n\n"
        try:
            import kivy

            self.passTest("IMPORT KIVY")
        except:
            self.failTest("IMPORT KIVY")

    def testZero(self):
        #Test if config file can be run and output file can be written
        self.longOutput += "\n\n###RUNNING TEST: RUN FILE...\n\n"

        try:
            data = RunFile.run("./Testing/PyMacTest/Test0-AirDensity-config.txt", False)

            self.passTest("RUN TEST FILE")
        except:
            self.failTest("RUN TEST FILE")

        try:
            data = RunFile.run("./Testing/PyMacTest/Test0-AirDensity-config.txt")

            self.passTest("WRITE OUT FILE")
        except:
            self.failTest("WRITE OUT FILE")

        if(os.path.exists("Test0-AirDensity-out.txt")):
            os.remove("Test0-AirDensity-out.txt")

    def testOne(self):
        #Test if calculated air densities match expected
        self.longOutput += "\n\n###RUNNING TEST: AIR DENSITY CALCULATION...\n\n"

        try:
            data = RunFile.run("./Testing/PyMacTest/Test0-AirDensity-config.txt", False)

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

            self.longOutput += "EXPECTED AIR DENSITIES: \n" + "\n".join(str(x) for x in expectedDensities) + "\n\n"
            self.longOutput += "CALCULATED AIR DENSITIES: \n" + "\n".join(str(x) for x in data[0].airDensities) + "\n\n"

            isCloseRes = np.isclose(data[0].airDensities, expectedDensities, atol=1e-8)

            for i in range(len(isCloseRes)):
                if isCloseRes[i] == True:
                    self.passTest("AIR DENSITY CALC " + str(i + 1))
                else:
                    self.failTest("AIR DENSITY CALC " + str(i + 1))
        except:
            self.failTest("AIR DENSITIES WERE NOT CALCULATED")

    def testTwo(self):
        #Test if calculated masses match masses written into the output file and that the rounding is handled correctly. Not testing acuracy of results yet
        self.longOutput += "\n\n###RUNNING TEST: WRITING DATA TO OUTPUT FILE...\n\n"

        try:
            data = RunFile.run("./Testing/PyMacTest/Test2-config.txt")

            outFileDensities = []
            outFileMasses = []
            expectedMasses = data[0].calculatedMasses[0]
            self.longOutput += "EXPECTED MASSES: \n" + "\n".join(str(x) for x in expectedMasses) + "\n\n"

            #Pull useful stuff out of output file
            with open("Test2-out.txt", 'r') as outFile:
                for line in outFile:
                    m = line.strip().split()
                    if(m == [] or m[0] == "\n"):
                        continue

                    if(m[0] == "W500g" or m[0] == "W300g" or m[0] == "W200g" or m[0] == "W100g" or m[0] == "P100g" or m[0] == "Wsum"):
                        outFileMasses.append(float(m[4]))
                        outFileDensities.append(float(m[2]))

            self.longOutput += "OUTPUT FILE MASSES: \n" + "\n".join(str(x) for x in outFileMasses) + "\n\n"

            for i in range(len(expectedMasses)):
                if(outFileMasses[i] == round(expectedMasses[i], 8)):
                    self.passTest("DATA WRITING TO OUTPUT FILE MASS CHECK " + str(i + 1))
                else:
                    self.failTest("DATA WRITING TO OUTPUT FILE MASS CHECK " + str(i + 1))

            #Test if densities in output file match input
            inputDensities = []

            with open("./Testing/PyMacTest/Test2-config.txt", 'r') as configFile:
                for line in configFile:
                    m = line.strip().split()
                    if(m == [] or m[0] == "\n"):
                        continue

                    if(m[0] == "<Position>"):
                        inputDensities.append(float(m[3]))

            self.longOutput += "\n\nINPUT FILE DENSITIES: \n" + "\n".join(str(x) for x in inputDensities) + "\n\n"
            self.longOutput += "OUTPUT FILE DENSITIES: \n" + "\n".join(str(x) for x in outFileDensities) + "\n"

            for i in range(len(inputDensities)):
                if(inputDensities[i] == outFileDensities[i]):
                    self.passTest("DATA WRITING TO OUTPUT FILE DENSITY CHECK " + str(i + 1))
                else:
                    self.failTest("DATA WRITING TO OUTPUT FILE DENSITY CHECK " + str(i + 1))
        except:
            self.failTest("ERROR IN RUN/OUTPUT REPORT GENERATION")

        if(os.path.exists("Test2-out.txt")):
            os.remove("Test2-out.txt")

if(__name__ == "__main__"):
    testSuite = TestSuite()

    testSuite.testKivy()
    testSuite.testZero()
    testSuite.testOne()
    testSuite.testTwo()

    print(testSuite.printSummary())