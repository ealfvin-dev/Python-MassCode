import RunFile
import numpy as np
import sys
import os

class TestSuite():
    def __init__(self):
        self.passed = 0
        self.failed = 0

        self.failedTests = []

    def testZero(self):
        testResults = "###RUNNING TEST 0: RUN FILE\n\n"

        try:
            data = RunFile.run("Test0-AirDensity-config.txt", False)
            testResults += "RUN TEST FILE.............PASS\n"
            self.passed +=1
        except:
            testResults += "RUN TEST FILE.............FAIL\n"
            self.failed += 1

        try:
            data = RunFile.run("Test0-AirDensity-config.txt")
            testResults += "WRITE OUT FILE.............PASS\n\n"
            self.passed +=1
        except:
            testResults += "WRITE OUT FILE.............FAIL\n\n"
            self.failed += 1

        if(os.path.exists("Test0-AirDensity-out.txt")):
            os.remove("Test0-AirDensity-out.txt")

        return testResults

    def testOne(self):
        testResults = "###RUNNING TEST 1: AIR DENSITY CALCULATION\n\n"
        data = RunFile.run("Test0-AirDensity-config.txt", False)

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
            else:
                testResults += str(i) + ":  " + str(data[0].airDensities[i]) + "...............FAIL\n"
                self.failed += 1

        return testResults

    def testTwo(self):
        pass