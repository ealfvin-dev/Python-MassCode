import sys

def test1PythonVersion(suite):
    testDesc = "PYTHON VERSION"
    try:
        assert sys.version_info >= (3, 5)
        suite.passTest(testDesc)
    except AssertionError:
        suite.failTest(testDesc)
        suite.logFailure(["Requires Python >= 3.5", str(sys.version_info)], testDesc)

def test2Numpy(suite):
    testDesc = "IMPORT NUMPY"
    try:
        import numpy
        suite.passTest(testDesc)
        suite.assertEqual(numpy.__version__, '1.17.2', "NUMPY VERSION")
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Could not import Numpy"], testDesc)

def test3SciPy(suite):
    testDesc = "IMPORT SCIPY"
    try:
        import scipy
        suite.passTest(testDesc)
        suite.assertEqual(scipy.__version__, '1.3.1', "SCIPY VERSION")
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Could not import SciPy"], testDesc)