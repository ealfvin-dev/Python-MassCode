import sys
from numpy import float64, zeros

from SeriesReduction import MatrixSolution
from WriteOutFile import writeOut
from MARSException import MARSException
#assert sys.version_info >= (3, 5)

def parse(fileName):
    notes = []
    header = {"reportNumber": "", "restraintID": "", "uncRestraint": 0}
    seriesObjects = []

    lines = 0
    seriesNumber = -1

    #Determine number of positions and observations in each series, get header information
    posObs = []
    with open(fileName, 'r') as configFile:
        for line in configFile:
            lines += 1
            if lines > 5000:
                raise MARSException("CONFIGURATION FILE EXCEEDS 5000 LINE LIMIT")

            splitLine = line.split()

            if (splitLine == []):
                continue

            if splitLine[0] == "@SERIES":
                seriesNumber += 1
                posObs.append([0, 0])
                continue

            if splitLine[0] == "<Position>":
                posObs[seriesNumber][0] += 1
                continue
            
            if splitLine[0] == "<Design>":
                posObs[seriesNumber][1] += 1
                continue

            if splitLine[0] == "<Report-Number>" and header["reportNumber"] == "":
                header["reportNumber"] = splitLine[1]
                continue

            if splitLine[0] == "<Restraint-ID>" and header["restraintID"] == "":
                header["restraintID"] = splitLine[1]
                continue

            if splitLine[0] == "<Unc-Restraint>" and header["uncRestraint"] == 0:
                header["uncRestraint"] = float(splitLine[1])
                continue

            # if splitLine[0] == "<Random-Error>":
            #     seriesObjects[seriesNumber].randomError = splitLine[1]
            #     continue

    seriesNumber = -1
    lines = 0

    #Open configuration file, read line by line, make MatrixSolution object for each series,
    #Assign atributes to MatrixSolution object based on the series number
    with open(fileName, 'r') as configFile:
        for line in configFile:
            lines += 1
            splitLine = line.split()

            if splitLine == []:
                continue

            if splitLine[0] == "<Report-Number>" or splitLine[0] == "<Restraint-ID>" or splitLine[0] == "<Unc-Restraint>":
                continue

            if splitLine[0] == "@SERIES":
                seriesNumber += 1
                designRow = 0
                positionRow = 0
                heightRow = 0
                toGrams = 1

                seriesObjects.append(MatrixSolution())

                seriesObjects[seriesNumber].notes = notes
                seriesObjects[seriesNumber].seriesNumber = seriesNumber
                seriesObjects[seriesNumber].positions = posObs[seriesNumber][0]
                seriesObjects[seriesNumber].observations = posObs[seriesNumber][1]
                seriesObjects[seriesNumber].reportNumber = header["reportNumber"]
                seriesObjects[seriesNumber].restraintID = header["restraintID"]
                seriesObjects[seriesNumber].uncRestraint = header["uncRestraint"]

                continue

            if splitLine[0][0] == "#":
                note = " ".join(splitLine)
                notes.append(note)
                continue

            if splitLine[0] == "<Date>":
                seriesObjects[seriesNumber].date.append(str(splitLine[1]))
                seriesObjects[seriesNumber].date.append(str(splitLine[2]))
                seriesObjects[seriesNumber].date.append(str(splitLine[3]))
                continue

            if splitLine[0] == "<Technician-ID>":
                seriesObjects[seriesNumber].technicianId = splitLine[1]
                continue

            if splitLine[0] == "<Balance-ID>":
                seriesObjects[seriesNumber].balanceId = splitLine[1]
                continue

            if splitLine[0] == "<Check-ID>":
                seriesObjects[seriesNumber].checkStandardId = splitLine[1]
                continue

            if splitLine[0] == "<Direct-Readings>":
                seriesObjects[seriesNumber].directReadings = int(splitLine[1])
                continue

            if splitLine[0] == "<Direct-Reading-SF>":
                seriesObjects[seriesNumber].directReadingsSF = float64(splitLine[1])
                continue

            if splitLine[0] == "<Grams>":
                seriesObjects[seriesNumber].nominalsInGrams = int(splitLine[1])
                if int(splitLine[1]) == 0:
                    toGrams = 453.59237
                else:
                    toGrams = 1
                continue

            if splitLine[0] == "<Design-ID>":
                seriesObjects[seriesNumber].designId = splitLine[1]
                continue

            if splitLine[0] == "<Position>":
                seriesObjects[seriesNumber].weightIds.append(splitLine[1])

                #Make weight nominals array and set calculatedMasses to nominals for first-pass estimates. Initialize matrixY:
                if positionRow == 0:
                    seriesObjects[seriesNumber].weightNominals = zeros(shape=(1, seriesObjects[seriesNumber].positions), dtype=float64)
                    seriesObjects[seriesNumber].ogNominals = zeros(shape=(1, seriesObjects[seriesNumber].positions), dtype=float64)

                    seriesObjects[seriesNumber].calculatedMasses = zeros(shape=(1, seriesObjects[seriesNumber].positions), dtype=float64)
                    seriesObjects[seriesNumber].matrixY = zeros(shape=(seriesObjects[seriesNumber].observations, 1), dtype=float64)
                    seriesObjects[seriesNumber].referenceValues = zeros(shape=(1, seriesObjects[seriesNumber].positions), dtype=float64)

                seriesObjects[seriesNumber].weightNominals[0, positionRow] = float64(splitLine[2]) * toGrams
                seriesObjects[seriesNumber].ogNominals[0, positionRow] = float64(splitLine[2])

                seriesObjects[seriesNumber].calculatedMasses[0, positionRow] = float64(splitLine[2]) * toGrams

                seriesObjects[seriesNumber].weightDensities.append(float64(splitLine[3]))
                seriesObjects[seriesNumber].weightCCEs.append(float64(splitLine[4]))

                try:
                    seriesObjects[seriesNumber].referenceValues[0, positionRow] = float64(splitLine[5])
                except IndexError:
                    seriesObjects[seriesNumber].referenceValues[0, positionRow] = 0
                positionRow += 1
                continue

            if splitLine[0] == "<Design>":
                if designRow == 0:
                    seriesObjects[seriesNumber].designMatrix = \
                        zeros(shape=(seriesObjects[seriesNumber].observations, seriesObjects[seriesNumber].positions), dtype=int)
                for i in range(1, len(splitLine)):
                    seriesObjects[seriesNumber].designMatrix[designRow, i - 1] = int(splitLine[i])
                designRow += 1
                continue

            if splitLine[0] == "<Restraint>":
                seriesObjects[seriesNumber].restraintPos = zeros(shape=(1, seriesObjects[seriesNumber].positions), dtype=int)
                for i in range(1, len(splitLine)):
                    seriesObjects[seriesNumber].restraintPos[0, i - 1] = int(splitLine[i])
                continue

            if splitLine[0] == "<Check-Standard>":
                seriesObjects[seriesNumber].checkStandardPos = zeros(shape=(1, seriesObjects[seriesNumber].positions), dtype=int)
                for i in range(1, len(splitLine)):
                    seriesObjects[seriesNumber].checkStandardPos[0, i - 1] = int(splitLine[i])
                continue

            # if splitLine[0] == "<Linear-Combo>":
            #     combo = []
            #     for i in range(1, len(splitLine)):
            #         combo.append(int(splitLine[i]))
            #     seriesObjects[seriesNumber].linearCombos.append(combo)
            #     continue

            if splitLine[0] == "<Pass-Down>":
                seriesObjects[seriesNumber].nextRestraint = zeros(shape=(1, seriesObjects[seriesNumber].positions), dtype=int)
                for i in range(1, len(splitLine)):
                    seriesObjects[seriesNumber].nextRestraint[0, i - 1] = int(splitLine[i])
                continue

            if splitLine[0] == "<Sigma-w>":
                seriesObjects[seriesNumber].sigmaW = float64(splitLine[1])
                continue

            if splitLine[0] == "<Sigma-t>":
                seriesObjects[seriesNumber].sigmaT = float64(splitLine[1])
                continue

            if splitLine[0] == "<sw-Mass>":
                seriesObjects[seriesNumber].swMass = float64(splitLine[1])
                continue

            if splitLine[0] == "<sw-Density>":
                seriesObjects[seriesNumber].swDensity = float64(splitLine[1])
                continue

            if splitLine[0] == "<sw-CCE>":
                seriesObjects[seriesNumber].swCCE = float64(splitLine[1])
                continue

            if splitLine[0] == "<Balance-Reading>":
                readings = []
                for i in range(1, len(splitLine)):
                    readings.append(float64(splitLine[i]))
                seriesObjects[seriesNumber].balanceReadings.append(readings)
                continue

            if splitLine[0] == "<Environmentals>":
                envs = []
                for i in range(1, 4):
                    envs.append(splitLine[i])
                seriesObjects[seriesNumber].environmentals.append(envs)
                continue

            if splitLine[0] == "<Env-Corrections>":
                for i in range(1, 4):
                    seriesObjects[seriesNumber].envCorrections.append(splitLine[i])
                continue

            if splitLine[0] == "<Gravity-Grad>":
                seriesObjects[seriesNumber].gravityGradient = float64(splitLine[1])
                continue

            if splitLine[0] == "<Gravity-Local>":
                seriesObjects[seriesNumber].localGravity = float64(splitLine[1])
                continue

            if splitLine[0] == "<Height>":
                if(seriesObjects[seriesNumber].weightHeights.size == 0):
                    #Initialize np matrix
                    seriesObjects[seriesNumber].weightHeights = zeros(shape=(1, seriesObjects[seriesNumber].positions), dtype=float64)

                seriesObjects[seriesNumber].weightHeights[0, heightRow] = float64(splitLine[1]) / 100
                heightRow += 1
                continue

            raise MARSException("UNKNOWN TAG AT LINE " + str(lines) + " IN CONFIGURATION FILE: " + str(splitLine[0]))

    return seriesObjects

def run(inputFile, outFilePath="./Working-Files/test-config.txt", writeOutFile=True):
    data = parse(inputFile)
    
    for series in data:
        series.solution(data)

    if(writeOutFile):
        writeOut(data, outFilePath)

    return data

if(__name__ == "__main__"):
    inputFile = sys.argv[1]
    run(inputFile, writeOutFile=True)