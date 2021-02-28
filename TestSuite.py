import TestBase
import RunFile
import InputChecks
from MARSException import MARSException
import API

import SystemTests
import RuntimeTests
import InputFileTests
import OutputFileTests
import DbTests
import ResultsTests

class TestSuite(TestBase.TestBase):
    #Mocked functions
    def sendErrorMock(self, message):
        pass

    def highlightErrorMock(self, series, startLine, endLine=None):
        pass

    def goToSeriesMock(self, seriesNum, exists):
        pass

    def runAll(self):
        systemTestAttr = dir(SystemTests)
        runtimeTestAttr = dir(RuntimeTests)
        inputFileTestAttr = dir(InputFileTests)
        outputFileTestAttr = dir(OutputFileTests)
        dbTestAttr = dir(DbTests)
        resultsTestAttr = dir(ResultsTests)

        for i in systemTestAttr:
            attr = getattr(SystemTests, i)
            if(i.startswith("test") and callable(attr)):
                attr(self)

        for i in runtimeTestAttr:
            attr = getattr(RuntimeTests, i)
            if(i.startswith("test") and callable(attr)):
                attr(self)

        for i in inputFileTestAttr:
            attr = getattr(InputFileTests, i)
            if(i.startswith("test") and callable(attr)):
                attr(self)

        for i in outputFileTestAttr:
            attr = getattr(OutputFileTests, i)
            if(i.startswith("test") and callable(attr)):
                attr(self)

        for i in dbTestAttr:
            attr = getattr(DbTests, i)
            if(i.startswith("test") and callable(attr)):
                attr(self)

        for i in resultsTestAttr:
            attr = getattr(ResultsTests, i)
            if(i.startswith("test") and callable(attr)):
                attr(self)

        return self.returnSummary()

if(__name__ == "__main__"):
    suite = TestSuite()
    results = suite.runAll()
    print(results)

    try:
        import kivy
        print("IMPORT KIVY: SUCCESS")
    except:
        print("IMPORT KIVY: FAIL")