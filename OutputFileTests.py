import RunFile
from os import path, remove

def test1WriteOutFile(suite):
    testDesc = "WRITE OUT FILE"
    try:
        data = RunFile.run(path.join("TestFiles", "Test-Writeout-config.txt"), outFilePath="Test-Writeout-out.txt")
        if(path.exists("Test-Writeout-out.txt")):
            suite.passTest(testDesc)
        else:
            suite.failTest(testDesc)
            suite.logFailure(["Could not write out test file"], testDesc)
    except:
        suite.failTest(testDesc)
        suite.logFailure(["Could not write out test file"], testDesc)

    if(path.exists("Test-Writeout-out.txt")):
        remove("Test-Writeout-out.txt")

def test2OutFileData(suite):
    #Test writing stuff into output file
    try:
        data = RunFile.run(path.join("TestFiles", "Test-Writeout-config.txt"), outFilePath="Test-Writeout-out.txt")

        outFileIDs = []
        outFileNominals = []
        outFileDensities = []
        outFileCCEs = []
        outFileTypeAs = []
        outFileTypeBs = []
        outFileMasses = []
        outFileCorrections = []
        outFileRestraintID = ""
        outFileCheckID = ""
        outFileBalanceID = ""
        outFileOperatorID = ""
        outFileDesignID = ""
        outFileTypeACheck = 0.0
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
        calculatedMasses = data[0].calculatedMasses[0]
        calculatedTypeAs = data[0].typeAs
        calculatedTypeBs = data[0].typeBs
        calculatedTypeACheck = round(data[0].typeACheck, 6)

        inputIDs = []
        inputNominals = []
        inputDensities = []
        inputCCEs = []
        inputRestraintID = ""
        inputCheckID = ""
        inputBalanceID = ""
        inputOperatorID = ""
        inputDesignID = ""
        inputSw = 0.0
        inputAcceptedCSCorr = 0.0

        #Pull useful stuff out of output file
        with open("Test-Writeout-out.txt", 'r') as outFile:
            for line in outFile:
                m = line.strip().split()
                if(m == []):
                    continue

                if(m[0] == "W500g" or m[0] == "W300g" or m[0] == "W200g" or m[0] == "W100g" or m[0] == "P100g" or m[0] == "Wsum"):
                    outFileIDs.append(m[0])
                    outFileNominals.append(m[1])
                    outFileDensities.append(float(m[2]))
                    outFileCCEs.append(float(m[3]))
                    outFileTypeAs.append(float(m[4]))
                    outFileTypeBs.append(float(m[5]))
                    outFileMasses.append(float(m[6]))
                    outFileCorrections.append(float(m[7]))
                elif(m[0] == "RESTRAINT_ID"):
                    outFileRestraintID = m[1]
                elif(m[0] == "CHECK_STANDARD_ID"):
                    outFileCheckID = m[1]
                elif(m[0] == "BALANCE_ID"):
                    outFileBalanceID = m[1]
                elif(m[0] == "OPERATOR_ID"):
                    outFileOperatorID = m[1]
                elif(m[0] == "DESIGN_ID"):
                    outFileDesignID = m[1]
                elif(m[0] == "CHECK_STANDARD_TYPE_A_UNC"):
                    outFileTypeACheck = float(m[1])
                elif(m[0] == "ACCEPTED_SW"):
                    outFileswAccepted = float(m[1])
                elif(m[0] == "OBSERVED_SW"):
                    outFilesw = float(m[1])
                elif(m[0] == "CRITICAL_F-VALUE"):
                    outFileFcrit = float(m[1])
                elif(m[0] == "OBSERVED_F-VALUE"):
                    outFileFvalue = float(m[1])
                elif(m[0] == "ACCEPTED_CHECK_STANDARD_CORRECTION"):
                    outFileCheckStdAccepted = float(m[1])
                elif(m[0] == "OBSERVED_CHECK_STANDARD_CORRECTION"):
                    outFileCheckStd = float(m[1])
                elif(m[0] == "CRITICAL_T-VALUE"):
                    outFileTcrit = float(m[1])
                elif(m[0] == "OBSERVED_T-VALUE"):
                    outFileTvalue = float(m[1])

        #Pull useful stuff out of input file
        with open(path.join("TestFiles", "Test-Writeout-config.txt"), 'r') as configFile:
            for line in configFile:
                m = line.strip().split()
                if(m == []):
                    continue

                if(m[0] == "<Restraint-ID>"):
                    inputRestraintID = m[1]
                elif(m[0] == "<Check-ID>"):
                    inputCheckID = m[1]
                elif(m[0] == "<Balance-ID>"):
                    inputBalanceID = m[1]
                elif(m[0] == "<Technician-ID>"):
                    inputOperatorID = m[1]
                elif(m[0] == "<Design-ID>"):
                    inputDesignID = m[1]
                elif(m[0] == "<Sigma-w>"):
                    inputSw = float(m[1])
                elif(m[0] == "<Position>"):
                    inputIDs.append(m[1])
                    inputNominals.append(m[2])
                    inputDensities.append(float(m[3]))
                    inputCCEs.append(float(m[4]))
                    if(m[1] == "P100g"):
                        inputAcceptedCSCorr = float(m[5])

        #Test that metadata was correctly written to output file
        suite.assertEqual(outFileRestraintID, inputRestraintID, "DATA WRITING TO OUTPUT FILE RESTRAINT ID")
        suite.assertEqual(outFileCheckID, inputCheckID, "DATA WRITING TO OUTPUT FILE CHECK STANDARD ID")
        suite.assertEqual(outFileBalanceID, inputBalanceID, "DATA WRITING TO OUTPUT FILE BALANCE ID")
        suite.assertEqual(outFileOperatorID, inputOperatorID, "DATA WRITING TO OUTPUT FILE TECHNICIAN ID")
        suite.assertEqual(outFileDesignID, inputDesignID, "DATA WRITING TO OUTPUT FILE DESIGN ID")

        #Test if weight IDs in output file match input
        for i in range(len(inputIDs)):
            suite.assertEqual(inputIDs[i], outFileIDs[i], "DATA WRITING TO OUTPUT FILE WEIGHT ID CHECK " + str(i + 1))

        #Test if weight nomials in output file match input
        for i in range(len(inputNominals)):
            suite.assertEqual(inputNominals[i], outFileNominals[i], "DATA WRITING TO OUTPUT FILE WEIGHT NOMINAL CHECK " + str(i + 1))

        #Test if densities in output file match input
        for i in range(len(inputDensities)):
            suite.assertEqual(inputDensities[i], outFileDensities[i], "DATA WRITING TO OUTPUT FILE DENSITY CHECK " + str(i + 1))

        #Test if CCEs in output file match input
        for i in range(len(inputCCEs)):
            suite.assertEqual(inputCCEs[i], outFileCCEs[i], "DATA WRITING TO OUTPUT FILE CCE CHECK " + str(i + 1))

        #Test if type As in output file match calculated values
        for i in range(len(calculatedTypeAs[0])):
            suite.assertEqual(outFileTypeAs[i], round(calculatedTypeAs[0][i], 5), "DATA WRITING TO OUTPUT FILE TYPE A CHECK " + str(i + 1))

        #Test if type Bs in output file match calculated values
        for i in range(len(calculatedTypeBs[0])):
            suite.assertEqual(outFileTypeBs[i], round(calculatedTypeBs[0][i], 5), "DATA WRITING TO OUTPUT FILE TYPE B CHECK " + str(i + 1))

        #Test if calculated masses match masses written into the output file and that the rounding is handled correctly. Not testing acuracy of results yet
        for i in range(len(calculatedMasses)):
            suite.assertEqual(outFileMasses[i], round(calculatedMasses[i], 8), "DATA WRITING TO OUTPUT FILE MASS CHECK " + str(i + 1))

        #Test if calculated mass corrections match masses written into the output file and that the rounding is handled correctly
        for i in range(len(outFileCorrections)):
            calculatedCorrection = (calculatedMasses[i] - float(inputNominals[i])) * 1000
            suite.assertEqual(outFileCorrections[i], round(calculatedCorrection, 5), "DATA WRITING TO OUTPUT FILE MASS CORRECTION CHECK " + str(i + 1))

        #Test if statistics were written out correctly
        suite.assertEqual(outFilesw, calculatedSw, "DATA WRITING TO OUTPUT FILE SW OBSERVED")
        suite.assertEqual(outFileswAccepted, inputSw, "DATA WRITING TO OUTPUT FILE SW ACCEPTED")
        suite.assertEqual(outFileTypeACheck, calculatedTypeACheck, "DATA WRITING TO OUTPUT FILE CHECK STANDARD TYPE A UNC")
        suite.assertEqual(outFileFcrit, calculatedFcrit, "DATA WRITING TO OUTPUT FILE F-CRITICAL")
        suite.assertEqual(outFileFvalue, calculatedFvalue, "DATA WRITING TO OUTPUT FILE F-VALUE")
        suite.assertEqual(outFileCheckStd, calculatedCheckStd, "DATA WRITING TO OUTPUT FILE CALCULATED CHECK STANDARD CORRECTION")
        suite.assertEqual(outFileCheckStdAccepted, inputAcceptedCSCorr, "DATA WRITING TO OUTPUT FILE ACCEPTED CHECK STANDARD CORRECTION")
        suite.assertEqual(outFileTcrit, calculatedTcrit, "DATA WRITING TO OUTPUT FILE T-CRITICAL")
        suite.assertEqual(outFileTvalue, calculatedTvalue, "DATA WRITING TO OUTPUT FILE T-VALUE")

    except:
        suite.failTest("OUTPUT FILE DATA")
        suite.logFailure(["Error in run/output report generation"], "OUTPUT FILE DATA")

    if(path.exists("Test-Writeout-out.txt")):
        remove("Test-Writeout-out.txt")