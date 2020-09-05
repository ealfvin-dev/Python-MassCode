import RunFile
from MARSException import MARSException

def test1RunFile(suite):
    #Test if config file can be run
    try:
        data = RunFile.run("./Testing/MARSTest/Test-FEGoodFile-config.txt", writeOutFile=False)
        suite.passTest("RUN TEST FILE")
    except:
        suite.failTest("RUN TEST FILE")
        suite.logFailure(["Could not run test file"], "RUN TEST FILE")

def test2NonInvertible(suite):
    #Test non-invertible matrix raises MARSException
    try:
        data = RunFile.run("./Testing/MARSTest/Test-NonInvertible-config.txt", writeOutFile=False)
        suite.failTest("NON-INVERTIBLE MATRIX RAISES MARSEXCEPTION")
        suite.logFailure(["Non-invertible matrix did not raise MARSException"], "NON-INVERTIBLE MATRIX RAISES MARSEXCEPTION")
    except MARSException:
        suite.passTest("NON-INVERTIBLE MATRIX RAISES MARSEXCEPTION")
    except:
        suite.failTest("NON-INVERTIBLE MATRIX RAISES MARSEXCEPTION")
        suite.logFailure(["Non-invertible matrix did not raise MARSException"], "NON-INVERTIBLE MATRIX RAISES MARSEXCEPTION")

# def testUnequalBalanceObs(suite):
#     #Test if balance readings != observations raises MARSException
#     try:
#         data = RunFile.run("./Testing/MARSTest/Test-UnEqualBalObs-config.txt", writeOutFile=False)
#         suite.failTest("UNEQUAL BALANCE OBSERVATIONS RAISES MARSEXCEPTION")
#         suite.logFailure(["Unequal balance observations did not raise MARSException"], "UNEQUAL BALANCE OBSERVATIONS RAISES MARSEXCEPTION")
#     except MARSException:
#         suite.passTest("UNEQUAL BALANCE OBSERVATIONS RAISES MARSEXCEPTION")
#     except:
#         suite.failTest("UNEQUAL BALANCE OBSERVATIONS RAISES MARSEXCEPTION")
#         suite.logFailure(["Unequal balance observations did not raise MARSException"], "UNEQUAL BALANCE OBSERVATIONS RAISES MARSEXCEPTION")

# def testUnequalEnvObs(suite):
#     #Test if environmental readings != observations raises MARSException
#     try:
#         data = RunFile.run("./Testing/MARSTest/Test-UnEqualEnvObs-config.txt", writeOutFile=False)
#         suite.failTest("UNEQUAL ENVIRONMENTAL OBSERVATIONS RAISES MARSEXCEPTION")
#         suite.logFailure(["Unequal environmental observations did not raise MARSException"], "UNEQUAL ENVIRONMENTAL OBSERVATIONS RAISES MARSEXCEPTION")
#     except MARSException:
#         suite.passTest("UNEQUAL ENVIRONMENTAL OBSERVATIONS RAISES MARSEXCEPTION")
#     except:
#         suite.failTest("UNEQUAL ENVIRONMENTAL OBSERVATIONS RAISES MARSEXCEPTION")
#         suite.logFailure(["Unequal environmental observations did not raise MARSException"], "UNEQUAL ENVIRONMENTAL OBSERVATIONS RAISES MARSEXCEPTION")

# def testNoRestraintPassed(suite):
#     #Test if no restraint passed to series raises MARSException
#     try:
#         data = RunFile.run("./Testing/MARSTest/Test-NoRestraintPassed-config.txt", writeOutFile=False)
#         suite.failTest("NO RESTRAINT PASSED RAISES MARSEXCEPTION")
#         suite.logFailure(["No restraint passed down did not raise MARSException"], "NO RESTRAINT PASSED RAISES MARSEXCEPTION")
#     except MARSException:
#         suite.passTest("NO RESTRAINT PASSED RAISES MARSEXCEPTION")
#     except:
#         suite.failTest("NO RESTRAINT PASSED RAISES MARSEXCEPTION")
#         suite.logFailure(["No restraint passed down did not raise MARSException"], "NO RESTRAINT PASSED RAISES MARSEXCEPTION")

def test3ZeroHeight(suite):
    #Test if height of 0 raisesMARSException
    try:
        data = RunFile.run("./Testing/MARSTest/Test-ZeroHeight-config.txt", writeOutFile=False)
        suite.failTest("HEIGHT OF 0 RAISES MARSEXCEPTION")
        suite.logFailure(["Weight height of 0 did not raise MARSException"], "NO RESTRAINT PASSED RAISES MARSEXCEPTION")
    except MARSException:
        suite.passTest("HEIGHT OF 0 RAISES MARSEXCEPTION")
    except:
        suite.failTest("HEIGHT OF 0 RAISES MARSEXCEPTION")
        suite.logFailure(["Weight height of 0 did not raise MARSException"], "HEIGHT OF 0 RAISES MARSEXCEPTION")