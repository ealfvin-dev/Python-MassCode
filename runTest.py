import RunFile
import numpy as np
import sys
import os

class TestSuite():
    def __init__(self):
        self.passed = 0
        self.failed = 0

        self.passedTests = []
        self.failedTests = []

    def testKivy(self):
        #Tests if Kivy can be imported
        testResults = "###RUNNING IMPORT KIVY\n\n"

        try:
            import kivy
            testResults += "KIVY IMPORT...............PASS"
            self.passed += 1
            self.passedTests.append("KIVY TEST - IMPORT KIVY")
        except:
            testResults += "KIVY IMPORT...............FAIL"
            self.failed += 1
            self.failedTests.append("KIVY TEST - IMPORT KIVY")

        return testResults

    def testZero(self):
        #Tests if config file can be run and output file can be written
        testResults = "###RUNNING TEST 0: RUN FILE\n\n"

        try:
            data = RunFile.run("./Testing/PyMacTest/Test0-AirDensity-config.txt", False)
            testResults += "RUN TEST FILE.............PASS\n"

            self.passed +=1
            self.passedTests.append("TEST 0 - RUN TEST FILE")
        except:
            testResults += "RUN TEST FILE.............FAIL\n"
            self.failed += 1
            self.failedTests.append("TEST 0 - RUN TEST FILE")

        try:
            data = RunFile.run("./Testing/PyMacTest/Test0-AirDensity-config.txt")
            testResults += "WRITE OUT FILE.............PASS\n\n"

            self.passed +=1
            self.passedTests.append("TEST 0 - WRITE OUT FILE")
        except:
            testResults += "WRITE OUT FILE.............FAIL\n\n"
            self.failed += 1
            self.failedTests.append("TEST 0 - WRITE OUT FILE")

        if(os.path.exists("Test0-AirDensity-out.txt")):
            os.remove("Test0-AirDensity-out.txt")

        return testResults

    def testOne(self):
        #Tests if calculated air densities match expected
        testResults = "###RUNNING TEST 1: AIR DENSITY CALCULATION\n\n"

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

            testResults += "EXPECTED AIR DENSITIES: \n" + "\n".join(str(x) for x in expectedDensities) + "\n\n"
            testResults += "CALCULATED AIR DENSITIES\n"

            isCloseRes = np.isclose(data[0].airDensities, expectedDensities, atol=1e-8)

            for i in range(len(isCloseRes)):
                if isCloseRes[i] == True:
                    testResults += str(i) + ":  " + str(data[0].airDensities[i]) + "...............PASS\n"
                    self.passed += 1
                    self.passedTests.append("TEST 1 - AIR DENSITY CALC " + str(i))
                else:
                    testResults += str(i) + ":  " + str(data[0].airDensities[i]) + "...............FAIL\n"
                    self.failed += 1
                    self.failedTests.append("TEST 1 - AIR DENSITY CALC " + str(i))
        except:
            testResults = "AN ERROR OCCURED - AIR DENSITIES WERE NOT CALCULATED.......FAIL\n"
            self.failed += 1
            self.failedTests.append("TEST 1 - AIR DENSITIES WERE NOT CALCULATED\n")

        return testResults

    def testTwo(self):
        #Tests if calculated masses match masses written into the output file and that the rounding is handled correctly. Not testing acuracy of results yet
        testResults = "\n###RUNNING TEST 2: WRITING DATA TO OUTPUT FILE\n\n"

        try:
            data = RunFile.run("./Testing/PyMacTest/Test2-config.txt")

            outFileMasses = []
            expectedMasses = data[0].calculatedMasses[0]
            testResults += "EXPECTED MASSES: \n" + "\n".join(str(x) for x in expectedMasses) + "\n\n"

            with open("Test2-out.txt", 'r') as outFile:
                for line in outFile:
                    m = line.strip().split()
                    if(m == [] or m[0] == "\n"):
                        continue

                    if(m[0] == "W500g" or m[0] == "W300g" or m[0] == "W200g" or m[0] == "W100g" or m[0] == "P100g" or m[0] == "Wsum"):
                        outFileMasses.append(float(m[4]))

            testResults += "OUTPUT FILE MASSES: \n" + "\n".join(str(x) for x in outFileMasses) + "\n\n"

            for i in range(len(expectedMasses)):
                if(outFileMasses[i] == round(expectedMasses[i], 8)):
                    testResults += "TEST 2 - DATA WRITING TO OUTPUT FILE AT " + str(round(data[0].ogNominals[0][i])) + " G..........PASS\n"
                    self.passed += 1
                    self.passedTests.append("TEST 2 - DATA WRITING TO OUTPUT FILE AT " + str(round(data[0].ogNominals[0][i])) + " G")
                else:
                    testResults += "TEST 2 - DATA WRITING TO OUTPUT FILE AT " + str(round(data[0].ogNominals[0][i])) + " G..........FAIL\n"
                    self.failed += 1
                    self.failedTests.append("TEST 2 - DATA WRITING TO OUTPUT FILE AT " + str(round(data[0].ogNominals[0][i])) + " G")
        except:
            testResults = "AN ERROR OCCURED - FILE DID NOT RUN.......FAIL\n"
            self.failed += 1
            self.failedTests.append("TEST 2 - ERROR IN RUN/OUTPUT REPORT GENERATION\n")

        if(os.path.exists("Test2-out.txt")):
            os.remove("Test2-out.txt")

        return testResults

if(__name__ == "__main__"):
    testSuite = TestSuite()

    print(testSuite.testKivy())
    print(testSuite.testZero())
    print(testSuite.testOne())
    print(testSuite.testTwo())

    print("\nTESTS PASSED:\n")
    print("    " + "\n    ".join(testSuite.passedTests))

    print("\n\nTESTS FAILED:\n    ")
    print("    " + "\n    ".join(testSuite.failedTests))

    print("\n***RAN " + str(testSuite.passed + testSuite.failed) + " TESTS***\n")
    print(str(testSuite.passed) + " PASSED\n"+str(testSuite.failed) + " FAILED\n\n")