import RunFile
from os import path

def test01AirDesities(suite):
    #Test if calculated air densities match NIST MassCode
    try:
        data = RunFile.run(path.join("TestFiles", "Test-AirDensity-config.txt"), writeOutFile=False)
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

def test02FourInOne(suite):
    #Test if calculated 4-1 masses at 1 kg match NIST MassCode
    try:
        data = RunFile.run(path.join("TestFiles", "Validation-4-1-config.txt"), writeOutFile=False)
        calculatedMasses = data[0].calculatedMasses[0]

        NIST_MC_MASSES = [1000.01028169, 1000.00279093, 1000.01020846, 999.99989410]
        
        NIST_MC_FVALUE = 0.211
        NIST_MC_TVALUE = 0.59

        for i in range(len(NIST_MC_MASSES)):
            suite.assertClose(NIST_MC_MASSES[i], calculatedMasses[i], 1e-7, "AUTOMATED 4-1 MASS CALCULATION " + str(i + 1))

        suite.assertClose(NIST_MC_FVALUE, data[0].fValue, 0.02, "AUTOMATED 4-1 F-VALUE CALCULATION")
        suite.assertClose(NIST_MC_TVALUE, data[0].tValue, 0.02, "AUTOMATED 4-1 T-VALUE CALCULATION")

    except:
        suite.failTest("VALIDATE 4-1")
        suite.logFailure(["Error running 4-1 input file"], "VALIDATE 4-1")

def test03MetricDissem(suite):
    #Test if full dissemination results from 1 kg - 1 mg (5-1, 532111, 522111) match NIST Masscode
    try:
        data = RunFile.run(path.join("TestFiles", "Validation-1kg-1mg-config.txt"), writeOutFile=False)

        NIST_MC_MASSES = [\
            [1000.00217499, 1000.00211201, 1000.00101741, 1000.00115097, 1000.00110198],\
            [500.00039595, 300.00043622, 200.00026981, 100.00009090, 100.00068933, 100.00004779],\
            [50.00002000, 20.00001440, 20.00000690, 10.00000649, 10.00002187, 9.99998385],\
            [5.00000430, 1.99998793, 1.99999550, 0.99999612, 1.00004420, 1.00000072],\
            [0.49999077, 0.30000739, 0.20000256, 0.09999874, 0.09999579, 0.10000585],\
            [0.05000273, 0.03000459, 0.01999853, 0.01000030, 0.00999905, 0.01000526],\
            [0.00500380, 0.00299881, 0.00200265, 0.00100428, 0.00100096, 0.00103382]]

        NIST_MC_FVALUE = [0.414, 0.640, 0.306, 0.421, 0.839, 0.308, 0.408]
        NIST_MC_TVALUE = [-0.36, 0.18, -1.88, -0.67, 0.65, -0.58, 0.25]

        for seriesNum in range(len(NIST_MC_MASSES)):
            for i in range(len(NIST_MC_MASSES[seriesNum])):
                suite.assertClose(NIST_MC_MASSES[seriesNum][i], data[seriesNum].calculatedMasses[0][i], 1e-7, \
                "1KG - 1MG DISSEMINATION MASS CALC SERIES " + str(seriesNum + 1) + " MASS " + str(i + 1))

            suite.assertClose(NIST_MC_FVALUE[seriesNum], data[seriesNum].fValue, 0.02, "SERIES " + str(seriesNum + 1) + " F-VALUE CALCULATION")
            suite.assertClose(NIST_MC_TVALUE[seriesNum], data[seriesNum].tValue, 0.02, "SERIES " + str(seriesNum + 1) + " T-VALUE CALCULATION")

    except:
        suite.failTest("VALIDATE 1KG - 1MG DISSEMINATION")
        suite.logFailure(["Error running 1kg - 1mg dissemination input file"], "VALIDATE 1KG - 1MG DISSEMINATION")

def test04LargeLb(suite):
    #Test it 3-1 results at 3000 lb match NIST Mass Code
    try:
        data = RunFile.run(path.join("TestFiles", "Validation-3000lb-3-1-config.txt"), writeOutFile=False)
        calculatedMasses = data[0].calculatedMasses[0]

        NIST_MC_MASS_CORRECTIONS = [9.12199977, 28.36503088, -5.87624665]

        NIST_MC_FVALUE = 4.136
        NIST_MC_TVALUE = 0.47

        for i in range(len(NIST_MC_MASS_CORRECTIONS)):
            suite.assertClose(NIST_MC_MASS_CORRECTIONS[i], calculatedMasses[i] - data[0].weightNominals[0][i], 1e-4, "3-1 at 3000 LB MASS CALCULATION " + str(i + 1))

        suite.assertClose(NIST_MC_FVALUE, data[0].fValue, 0.02, "3-1 at 3000 LB F-VALUE CALCULATION")
        suite.assertClose(NIST_MC_TVALUE, data[0].tValue, 0.02, "3-1 at 3000 LB T-VALUE CALCULATION")

    except:
        suite.failTest("VALIDATE 3-1 at 3000 LB")
        suite.logFailure(["Error running 3000 lb 3-1 input file"], "VALIDATE 3-1 at 3000 LB")

def test05LbDissem(suite):
    #Test if pound dissemination from 1 lb to 0.001 lb results match NIST Mass Code
    try:
        data = RunFile.run(path.join("TestFiles", "Validation-1lb-0.001lb-config.txt"), writeOutFile=False)

        NIST_MC_MASS_CORRECTIONS = [\
            [0.00034930, 0.00856124, 0.00274900, 0.00634527],\
            [0.00348752, 0.00193592, 0.00092183, 0.00003094, 0.00088465, 0.00055799],\
            [0.00031019, 0.00023586, 0.00001194, 0.00004015, 0.00009632, 0.00026042],\
            [0.00015035, 0.00002761, 0.00008247, 0.00002241, 0.00005837, 0.00007353]]

        NIST_MC_FVALUE = [1.032, 0.266, 1.628, 0.036]
        NIST_MC_TVALUE = [-1.88, 1.30, 0.01, 0.70]

        for seriesNum in range(len(NIST_MC_MASS_CORRECTIONS)):
            for i in range(len(NIST_MC_MASS_CORRECTIONS[seriesNum])):
                suite.assertClose(NIST_MC_MASS_CORRECTIONS[seriesNum][i], data[seriesNum].calculatedMasses[0][i] - data[seriesNum].weightNominals[0][i], 1e-7, \
                "1LB - 0.001LB DISSEMINATION MASS CALC SERIES " + str(seriesNum + 1) + " MASS " + str(i + 1))

            suite.assertClose(NIST_MC_FVALUE[seriesNum], data[seriesNum].fValue, 0.02, "SERIES " + str(seriesNum + 1) + " F-VALUE CALCULATION")
            suite.assertClose(NIST_MC_TVALUE[seriesNum], data[seriesNum].tValue, 0.02, "SERIES " + str(seriesNum + 1) + " T-VALUE CALCULATION")

    except:
        suite.failTest("VALIDATE 1LB - 0.001LB DISSEMINATION")
        suite.logFailure(["Error running 1lb - 0.001lb dissemination input file"], "VALIDATE 1LB - 0.001LB DISSEMINATION")

def test06OnekgSF(suite):
    #Test if calculated 4-1 masses at 1 kg with a sensitivity factor != 1 match NIST MassCode
    try:
        data = RunFile.run(path.join("TestFiles", "Validation-1kg-SF-config.txt"), writeOutFile=False)
        calculatedMasses = data[0].calculatedMasses[0]

        NIST_MC_MASSES = [999.99806382, 1000.00395937, 999.99806408, 1000.00635463]
        
        NIST_MC_FVALUE = 0.299
        NIST_MC_TVALUE = 1.13

        for i in range(len(NIST_MC_MASSES)):
            suite.assertClose(NIST_MC_MASSES[i], calculatedMasses[i], 1e-7, "AUTOMATED 4-1 SF MASS CALCULATION " + str(i + 1))

        suite.assertClose(NIST_MC_FVALUE, data[0].fValue, 0.02, "AUTOMATED 4-1 SF F-VALUE CALCULATION")
        suite.assertClose(NIST_MC_TVALUE, data[0].tValue, 0.02, "AUTOMATED 4-1 SF T-VALUE CALCULATION")

    except:
        suite.failTest("VALIDATE 4-1 WITH SF")
        suite.logFailure(["Error running 4-1 SF input file"], "VALIDATE 4-1 WITH SF")

def test07Ascending52211(suite):
    #Test if ascending 52211 masses match NIST MassCode
    try:
        data = RunFile.run(path.join("TestFiles", "Validation-52211-config.txt"), writeOutFile=False)
        calculatedMasses = data[0].calculatedMasses[0]

        NIST_MC_MASSES = [4999.99155113, 1999.99996593, 2000.00061565, 1000.00158552, 1000.00134116]
        
        NIST_MC_FVALUE = 0.065
        NIST_MC_TVALUE = 1.21

        for i in range(len(NIST_MC_MASSES)):
            suite.assertClose(NIST_MC_MASSES[i], calculatedMasses[i], 1e-7, "ASCENDING 52211 MASS CALCULATION " + str(i + 1))

        suite.assertClose(NIST_MC_FVALUE, data[0].fValue, 0.02, "ASCENDING 52211 F-VALUE CALCULATION")
        suite.assertClose(NIST_MC_TVALUE, data[0].tValue, 0.02, "ASCENDING 52211 T-VALUE CALCULATION")

    except:
        suite.failTest("ASCENDING 52211 MASS CALCULATION")
        suite.logFailure(["Error running ascending 52211 input file"], "ASCENDING 52211 MASS CALCULATION")

def test08LineByLineABC(suite):
    #Test if ascending 52211 masses match NIST MassCode
    try:
        data = RunFile.run(path.join("TestFiles", "Validation-LBL-ABC-config.txt"), writeOutFile=False)
        calculatedMasses = data[0].calculatedMasses[0]

        EXPECTED_MASSES = [999.98995274, 999.99835319, 999.99002598, 999.99989410]

        for i in range(len(EXPECTED_MASSES)):
            suite.assertClose(EXPECTED_MASSES[i], calculatedMasses[i], 1e-7, "LINE-BY-LINE AIR BUOYANCY CORRECTIONS " + str(i + 1))

    except:
        suite.failTest("LINE-BY-LINE AIR BUOYANCY CORRECTIONS")
        suite.logFailure(["Error running line-by-line ABC input file"], "LINE-BY-LINE AIR BUOYANCY CORRECTIONS")

def test09TypeAUncertainties(suite):
    #Test if type A uncertainties are calculated correctly. Tested at 1 kg, 50 g, 500 mg
    try:
        data = RunFile.run(path.join("TestFiles", "Validation-1kg-1mg-config.txt"), writeOutFile=False)

        NIST_MC_TYPE_AS_1kg = [0.01109, 0.01109, 0.01921, 0.01921, 0.01921]
        NIST_MC_TYPE_AS_50g = [0.00485, 0.00233, 0.00233, 0.00180, 0.00192, 0.00192]
        NIST_MC_TYPE_AS_500mg = [0.00028, 0.00021, 0.00018, 0.00019, 0.00019, 0.00019]

        typeACalculated1kg = data[0].typeAs
        typeACalculated50g = data[2].typeAs
        typeACalculated500mg = data[4].typeAs

        for i in range(len(NIST_MC_TYPE_AS_1kg)):
            suite.assertClose(NIST_MC_TYPE_AS_1kg[i], typeACalculated1kg[0][i], 2e-5, "1 kg TYPE A UNCERTAINTY CALCULATION " + str(i + 1))

        for i in range(len(NIST_MC_TYPE_AS_50g)):
            suite.assertClose(NIST_MC_TYPE_AS_50g[i], typeACalculated50g[0][i], 2e-5, "50 g TYPE A UNCERTAINTY CALCULATION " + str(i + 1))

        for i in range(len(NIST_MC_TYPE_AS_500mg)):
            suite.assertClose(NIST_MC_TYPE_AS_500mg[i], typeACalculated500mg[0][i], 2e-5, "500 mg TYPE A UNCERTAINTY CALCULATION " + str(i + 1))

    except:
        suite.failTest("TYPE A UNCERTAINTY CALCULATIONS")
        suite.logFailure(["Error running validate type A uncertainties input file"], "TYPE A UNCERTAINTY CALCULATIONS")

def test10TypeBUncertainties(suite):
    #Test if type B uncertainties are calculated correctly. Tested at 1 kg, 50 g, 500 mg
    try:
        data = RunFile.run(path.join("TestFiles", "Validation-1kg-1mg-config.txt"), writeOutFile=False)

        NIST_MC_TYPE_BS_1kg = [0.03050, 0.03050, 0.03050, 0.03050, 0.03050]
        NIST_MC_TYPE_BS_50g = [0.00153, 0.00061, 0.00061, 0.00031, 0.00031, 0.00031]
        NIST_MC_TYPE_BS_500mg = [0.00002, 0.00001, 0.00001, 0.00000, 0.00000, 0.00000]

        typeBCalculated1kg = data[0].typeBs
        typeBCalculated50g = data[2].typeBs
        typeBCalculated500mg = data[4].typeBs

        for i in range(len(NIST_MC_TYPE_BS_1kg)):
            suite.assertClose(NIST_MC_TYPE_BS_1kg[i], typeBCalculated1kg[0][i], 2e-5, "1 kg TYPE B UNCERTAINTY CALCULATION " + str(i + 1))

        for i in range(len(NIST_MC_TYPE_BS_50g)):
            suite.assertClose(NIST_MC_TYPE_BS_50g[i], typeBCalculated50g[0][i], 2e-5, "50 g TYPE B UNCERTAINTY CALCULATION " + str(i + 1))

        for i in range(len(NIST_MC_TYPE_BS_500mg)):
            suite.assertClose(NIST_MC_TYPE_BS_500mg[i], typeBCalculated500mg[0][i], 2e-5, "500 mg TYPE B UNCERTAINTY CALCULATION " + str(i + 1))

    except:
        suite.failTest("TYPE B UNCERTAINTY CALCULATIONS")
        suite.logFailure(["Error running validate type B uncertainties input file"], "TYPE B UNCERTAINTY CALCULATIONS")