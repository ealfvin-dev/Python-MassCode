import RunFile
from MARSException import MARSException
from os import path

def test1RunFile(suite):
    testDesc = "RUN TEST FILE"
    try:
        data = RunFile.run(path.join("TestFiles", "Test-FEGoodFile-config.txt"), writeOutFile=False)
        suite.passTest(testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Could not run test file"], testDesc)

def test2NonInvertible(suite):
    testDesc = "NON-INVERTIBLE MATRIX RAISES MARSEXCEPTION"
    try:
        data = RunFile.run(path.join("TestFiles", "Test-NonInvertible-config.txt"), writeOutFile=False)
        suite.failTest(testDesc)
        suite.logFailure(["Non-invertible matrix did not raise MARSException"], testDesc)
    except MARSException:
        suite.passTest(testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Non-invertible matrix did not raise MARSException"], testDesc)

def test3ZeroHeight(suite):
    testDesc = "HEIGHT OF 0 RAISES MARSEXCEPTION"
    try:
        data = RunFile.run(path.join("TestFiles", "Test-ZeroHeight-config.txt"), writeOutFile=False)
        suite.failTest(testDesc)
        suite.logFailure(["Weight height of 0 did not raise MARSException"], "NO RESTRAINT PASSED RAISES MARSEXCEPTION")
    except MARSException:
        suite.passTest(testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Weight height of 0 did not raise MARSException"], testDesc)