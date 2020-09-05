import sys

def test1PythonVersion(suite):
    #Assert current version of python >= 3.5
    try:
        assert sys.version_info >= (3, 5)
        suite.passTest("PYTHON VERSION")
    except AssertionError:
        suite.failTest("PYTHON VERSION")
        suite.logFailure(["Requires Python >= 3.5", str(sys.version_info)], "PYTHON VERSION")

def test2Numpy(suite):
    #Test if Numpy can import, check version
    try:
        import numpy
        suite.passTest("IMPORT NUMPY")
        suite.assertEqual(numpy.__version__, '1.17.2', "NUMPY VERSION")
    except:
        suite.failTest("IMPORT NUMPY")
        suite.logFailure(["Could not import Numpy"], "IMPORT NUMPY")

def test3SciPy(suite):
    #Test if SciPy can import, check version
    try:
        import scipy
        suite.passTest("IMPORT SCIPY")
        suite.assertEqual(scipy.__version__, '1.3.1', "SCIPY VERSION")
    except:
        suite.failTest("IMPORT SCIPY")
        suite.logFailure(["Could not import SciPy"], "IMPORT SCIPY")