import RunFile
import os

def test1WriteOutFile(suite):
    #Test if output file can be written out
    try:
        data = RunFile.run("./Testing/MARSTest/Test-Writeout-config.txt")
        if(os.path.exists("Test-Writeout-out.txt")):
            suite.passTest("WRITE OUT FILE")
        else:
            suite.failTest("WRITE OUT FILE")
            suite.logFailure(["Could not write out test file"], "WRITE OUT FILE")
    except:
        suite.failTest("WRITE OUT FILE")
        suite.logFailure(["Could not write out test file"], "WRITE OUT FILE")

    if(os.path.exists("Test-Writeout-out.txt")):
        os.remove("Test-Writeout-out.txt")

def test2OutFileData(suite):
    #Test writing stuff into output file
    try:
        data = RunFile.run("./Testing/MARSTest/Test-Writeout-config.txt")

        outFileDensities = []
        outFileMasses = []
        outFilesw = 0.0
        outFileswAccepted = 0.0
        outFileFcrit = 0.0
        outFileFvalue = 0.0
        outFileCheckStd = 0.0
        outFileCheckStdAccepted = 0.0
        outFileTcrit = 0.0
        outFileTvalue = 0.0

        calculatedSw = round(data[0].swObs, 6)
        calculatedFcrit = round(data[0].fCritical, 2)
        calculatedFvalue = round(data[0].fValue, 2)
        calculatedCheckStd = round(data[0].calculatedCheckCorrection, 6)
        calculatedTcrit = round(data[0].tCritical, 2)
        calculatedTvalue = round(data[0].tValue, 2)

        inputDensities = []
        inputSw = 0.0
        inputAcceptedCSCorr = 0.0

        expectedMasses = data[0].calculatedMasses[0]

        #Pull useful stuff out of output file
        with open("Test-Writeout-out.txt", 'r') as outFile:
            for line in outFile:
                m = line.strip().split()
                if(m == [] or m[0] == "\n"):
                    continue

                if(m[0] == "W500g" or m[0] == "W300g" or m[0] == "W200g" or m[0] == "W100g" or m[0] == "P100g" or m[0] == "Wsum"):
                    outFileMasses.append(float(m[4]))
                    outFileDensities.append(float(m[2]))
                elif(m[0] == "ACCEPTED_SW"):
                    outFileswAccepted = float(m[2])
                elif(m[0] == "OBSERVED_SW"):
                    outFilesw = float(m[2])
                elif(m[0] == "CRITICAL_F-VALUE"):
                    outFileFcrit = float(m[2])
                elif(m[0] == "OBSERVED_F-VALUE"):
                    outFileFvalue = float(m[2])
                elif(m[0] == "ACCEPTED_CHECK_STANDARD_CORRECTION"):
                    outFileCheckStdAccepted = float(m[2])
                elif(m[0] == "OBSERVED_CHECK_STANDARD_CORRECTION"):
                    outFileCheckStd = float(m[2])
                elif(m[0] == "CRITICAL_T-VALUE"):
                    outFileTcrit = float(m[2])
                elif(m[0] == "OBSERVED_T-VALUE"):
                    outFileTvalue = float(m[2])

        #Pull useful stuff out of input file
        with open("./Testing/MARSTest/Test-Writeout-config.txt", 'r') as configFile:
            for line in configFile:
                m = line.strip().split()
                if(m == [] or m[0] == "\n"):
                    continue
                elif(m[0] == "<Sigma-w>"):
                    inputSw = float(m[1])
                elif(m[0] == "<Position>"):
                    inputDensities.append(float(m[3]))
                    if(m[1] == "P100g"):
                        inputAcceptedCSCorr = float(m[5])

        #Test if calculated masses match masses written into the output file and that the rounding is handled correctly. Not testing acuracy of results yet
        for i in range(len(expectedMasses)):
            suite.assertEqual(outFileMasses[i], round(expectedMasses[i], 8), "DATA WRITING TO OUTPUT FILE MASS CHECK " + str(i + 1))

        #Test if densities in output file match input
        for i in range(len(inputDensities)):
            suite.assertEqual(inputDensities[i], outFileDensities[i], "DATA WRITING TO OUTPUT FILE DENSITY CHECK " + str(i + 1))

        #Test if statistics were written out correctly
        suite.assertEqual(outFilesw, calculatedSw, "DATA WRITING TO OUTPUT FILE SW OBSERVED")
        suite.assertEqual(outFileswAccepted, inputSw, "DATA WRITING TO OUTPUT FILE SW ACCEPTED")
        suite.assertEqual(outFileFcrit, calculatedFcrit, "DATA WRITING TO OUTPUT FILE F-CRITICAL")
        suite.assertEqual(outFileFvalue, calculatedFvalue, "DATA WRITING TO OUTPUT FILE F-VALUE")
        suite.assertEqual(outFileCheckStd, calculatedCheckStd, "DATA WRITING TO OUTPUT FILE CALCULATED CHECK STANDARD CORRECTION")
        suite.assertEqual(outFileCheckStdAccepted, inputAcceptedCSCorr, "DATA WRITING TO OUTPUT FILE ACCEPTED CHECK STANDARD CORRECTION")
        suite.assertEqual(outFileTcrit, calculatedTcrit, "DATA WRITING TO OUTPUT FILE T-CRITICAL")
        suite.assertEqual(outFileTvalue, calculatedTvalue, "DATA WRITING TO OUTPUT FILE T-VALUE")

    except:
        suite.failTest("OUTPUT FILE DATA")
        suite.logFailure(["Error in run/output report generation"], "OUTPUT FILE DATA")

    if(os.path.exists("Test-Writeout-out.txt")):
        os.remove("Test-Writeout-out.txt")