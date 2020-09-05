import RunFile

def test1AirDesities(suite):
    #Test if calculated air densities match expected
    try:
        data = RunFile.run("./Testing/MARSTest/Test-AirDensity-config.txt", writeOutFile=False)
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
            suite.assertClose(expectedDensities[i], calculatedDesities[i], 1e-7, "AIR DENSITY CALC " + str(i + 1))

    except:
        suite.failTest("CALCULATE AIR DENSITIES")
        suite.logFailure(["Air densities were not calculated"], "CALCULATE AIR DENSITIES")