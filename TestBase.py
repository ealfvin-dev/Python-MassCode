class TestBase:
    def __init__(self):
        self.testNum = 1
        self.passed = 0
        self.failed = 0

        self.passedTests = []
        self.failedTests = []
        self.log = []

    def passTest(self, testName):
        self.passed += 1
        self.passedTests.append("TEST " + str(self.testNum) + " - " + testName)
        #self.longOutput += "\n" + testName + ".........PASS"
        self.testNum += 1

    def failTest(self, testName):
        self.failed += 1
        self.failedTests.append("TEST " + str(self.testNum) + " - " + testName)
        #self.longOutput += "\n" + testName + ".........FAIL"
        self.testNum += 1

    def assertEqual(self, var1, var2, test):
        if(var1 == var2):
            self.passTest(test)
        else:
            self.failTest(test)
            self.log.append(test + "\n      Expected: " + str(var1) + "\n      Recieved: " + str(var2) + "\n      Not equal\n")

    def assertClose(self, var1, var2, precision, test):
        if(abs(var1 - var2) <= precision):
            self.passTest(test)
        else:
            self.failTest(test)
            self.log.append(test + "\n      Expected: " + str(var1) + "\n      Recieved: " + str(var2) + "\n      Not within tolerance " + str(precision) + "\n")

    def printSummary(self):
        summary = "\n############## TEST SUITE ##############\n"

        summary += "\n*** LOG\n\n"
        summary += "    " + "\n    ".join(self.log) + "\n"

        summary += "\nTESTS PASSED:\n\n"
        summary += "    " + "\n    ".join(self.passedTests) + "\n"
        summary += "\n\nTESTS FAILED:\n\n"
        summary += "    " + "\n    ".join(self.failedTests) + "\n"

        summary += "\n*** RAN " + str(self.passed + self.failed) + " TESTS\n\n" #+ "/" + str(self.expectedNumTests) + " TESTS ***\n\n"
        summary += str(self.passed) + " PASSED\n"+str(self.failed) + " FAILED\n\n"

        if(self.failed > 0):
            summary += "\nSEE TEST FAILURE LOGS ABOVE"

        print(summary)

    def returnSummary(self):
        summary = "\n############## TEST SUITE ##############\n"

        summary += "\n*** LOG\n\n"
        summary += "    " + "\n    ".join(self.log) + "\n"

        summary += "\nTESTS PASSED:\n\n"
        summary += "    " + "\n    ".join(self.passedTests) + "\n"
        summary += "\n\nTESTS FAILED:\n\n"
        summary += "    " + "\n    ".join(self.failedTests) + "\n"

        summary += "\n*** RAN " + str(self.passed + self.failed) + " TESTS\n\n" #+ "/" + str(self.expectedNumTests) + " TESTS ***\n\n"
        summary += str(self.passed) + " PASSED\n"+str(self.failed) + " FAILED\n\n"

        if(self.failed > 0):
            summary += "\nSEE TEST FAILURE LOGS ABOVE"

        return summary