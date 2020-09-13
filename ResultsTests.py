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
    #Test if calculated 4-1 masses at 1 kg match NIST MassCode
    try:
        data = RunFile.run("./Testing/MARSTest/Validation-4-1-config.txt", writeOutFile=False)
        calculatedMasses = data[0].calculatedMasses[0]

        NIST_MC_MASSES = [1000.01028169, 1000.00279094, 1000.01020845, 999.99989410]
        
        NIST_MC_FVALUE = 0.211
        NIST_MC_TVALUE = 0.59

        for i in range(len(NIST_MC_MASSES)):
            suite.assertClose(NIST_MC_MASSES[i], calculatedMasses[i], 1e-7, "AUTOMATED 4-1 MASS CALCULATION " + str(i + 1))

        suite.assertClose(NIST_MC_FVALUE, data[0].fValue, 0.02, "AUTOMATED 4-1 F-VALUE CALCULATION")
        suite.assertClose(NIST_MC_TVALUE, data[0].tValue, 0.02, "AUTOMATED 4-1 T-VALUE CALCULATION")

    except:
        suite.failTest("VALIDATE 4-1")
        suite.logFailure(["Error running 4-1 input file"], "VALIDATE 4-1")

def test3MetricDissem(suite):
    #Test if full dissemination results from 1 kg - 1 mg (5-1, 532111, 522111) match NIST Masscode
    try:
        data = RunFile.run("./Testing/MARSTest/Validation-1kg-1mg-config.txt", writeOutFile=False)

        NIST_MC_MASSES = [\
            [1000.00217500, 1000.00211200, 1000.00101737, 1000.00115094, 1000.00110195],\
            [500.00039592, 300.00043621, 200.00026980, 100.00009090, 100.00068933, 100.00004779],\
            [50.00002000, 20.00001440, 20.00000690, 10.00000649, 10.00002187, 9.99998385],\
            [5.00000430, 1.99998793, 1.99999550, 0.99999612, 1.00004420, 1.00000072],\
            [0.49999077, 0.30000741, 0.20000257, 0.09999874, 0.09999579, 0.10000585],\
            [0.05000273, 0.03000459, 0.01999853, 0.01000030, 0.00999905, 0.01000526],\
            [0.00500380, 0.00299881, 0.00200265, 0.00100428, 0.00100096, 0.00103382]]

        NIST_MC_FVALUE = [0.414, 0.640, 0.306, 0.422, 0.840, 0.308, 0.408]
        NIST_MC_TVALUE = [-0.36, 0.18, -1.89, -0.67, 0.65, -0.58, 0.25]

        for seriesNum in range(len(NIST_MC_MASSES)):
            for i in range(len(NIST_MC_MASSES[seriesNum])):
                suite.assertClose(NIST_MC_MASSES[seriesNum][i], data[seriesNum].calculatedMasses[0][i], 1e-7, \
                "1KG - 1MG DISSEMINATION MASS CALC SERIES " + str(seriesNum + 1) + " MASS " + str(i + 1))

            suite.assertClose(NIST_MC_FVALUE[seriesNum], data[seriesNum].fValue, 0.02, "SERIES " + str(seriesNum + 1) + " F-VALUE CALCULATION")
            suite.assertClose(NIST_MC_TVALUE[seriesNum], data[seriesNum].tValue, 0.02, "SERIES " + str(seriesNum + 1) + " T-VALUE CALCULATION")

    except:
        suite.failTest("VALIDATE 1KG - 1MG DISSEMINATION")
        suite.logFailure(["Error running 1kg - 1mg dissemination input file"], "VALIDATE 1KG - 1MG DISSEMINATION")

def test4LargeLb(suite):
    #Test it 3-1 results at 3000 lb match NIST Mass Code
    try:
        data = RunFile.run("./Testing/MARSTest/Validation-3000lb-3-1-config.txt", writeOutFile=False)
        calculatedMasses = data[0].calculatedMasses[0]

        NIST_MC_MASS_CORRECTIONS = [9.12199724, 28.36503760, -5.87623869]

        NIST_MC_FVALUE = 4.136
        NIST_MC_TVALUE = 0.47

        for i in range(len(NIST_MC_MASS_CORRECTIONS)):
            suite.assertClose(NIST_MC_MASS_CORRECTIONS[i], calculatedMasses[i] - data[0].weightNominals[0][i], 1e-4, "3-1 at 3000 LB MASS CALCULATION " + str(i + 1))

        suite.assertClose(NIST_MC_FVALUE, data[0].fValue, 0.02, "3-1 at 3000 LB F-VALUE CALCULATION")
        suite.assertClose(NIST_MC_TVALUE, data[0].tValue, 0.02, "3-1 at 3000 LB T-VALUE CALCULATION")

    except:
        suite.failTest("VALIDATE 3-1 at 3000 LB")
        suite.logFailure(["Error running 3000 lb 3-1 input file"], "VALIDATE 3-1 at 3000 LB")