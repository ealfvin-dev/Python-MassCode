import RunFile

def test1AirDesities(suite):
    #Test if calculated air densities match NIST MassCode
    try:
        data = RunFile.run("./Testing/MARSTest/Test-AirDensity-config.txt", writeOutFile=False)
        calculatedDesities = data[0].airDensities

        NIST_MC_DENSITIES = [\
            0.0011627,\
            0.0011320,\
            0.0012102,\
            0.0012262,\
            0.0011656,\
            0.0011809,\
            0.0011529,\
            0.0012371,\
            0.0012114,\
            0.0011910,\
            0.0011843,\
            0.0010970]

        for i in range(len(NIST_MC_DENSITIES)):
            suite.assertClose(NIST_MC_DENSITIES[i], calculatedDesities[i], 2e-7, "AIR DENSITY CALCULATION " + str(i + 1))

    except:
        suite.failTest("CALCULATE AIR DENSITIES")
        suite.logFailure(["Air densities were not calculated"], "CALCULATE AIR DENSITIES")

def test2FourInOne(suite):
    #Test if calculated 4-1 masses at 10 kg match NIST MassCode
    ##try:
        data = RunFile.run("./Testing/MARSTest/Validation-4-1-config.txt", writeOutFile=False)
        calculatedMasses = data[0].calculatedMasses[0]

        NIST_MC_MASSES = [\
            1000.01028169,\
            1000.00279093,\
            1000.01020846,\
            999.99989410]
        
        NIST_MC_FVALUE = 0.211
        NIST_MC_TVALUE = 0.59

        for i in range(len(NIST_MC_MASSES)):
            suite.assertClose(NIST_MC_MASSES[i], calculatedMasses[i], 2e-8, "4-1 MASS CALCULATION " + str(i + 1))

        suite.assertClose(NIST_MC_FVALUE, data[0].fValue, 0.02, "4-1 F-VALUE CALCULATION")
        suite.assertClose(NIST_MC_TVALUE, data[0].tValue, 0.02, "4-1 T-VALUE CALCULATION")

    # except:
    #     suite.failTest("VALIDATE 4-1")
    #     suite.logFailure(["Error running 4-1 Input File"], "VALIDATE 4-1")