import sys
import numpy as np
from SeriesReduction import MatrixSolution
from WriteOutFile import writeOut
from MARSException import MARSException
assert sys.version_info >= (3, 5)

def parse(fileName):
    header = {}
    seriesObjects = []

    lines = 0
    seriesNumber = -1
    designRow = 0
    positionRow = 0

    nominalsInPounds = 1

    #Determine number of positions and observations in each series
    posObs = []
    with open(fileName, 'r') as configFile:
        for line in configFile:
            lines += 1
            if lines > 5000:
                raise MARSException("CONFIGURATION FILE EXCEEDS 5000 LINE LIMIT")

            splitLine = line.strip().split(maxsplit=15)

            if (len(splitLine) == 0):
                continue

            if splitLine[0] == "@SERIES":
                seriesNumber += 1
                posObs.append([0, 0])

            if splitLine[0] == "<Position>":
                posObs[seriesNumber][0] += 1
            
            if splitLine[0] == "<Design>":
                posObs[seriesNumber][1] += 1

    seriesNumber = -1
    lines = 0

    #Open configuration file, read line by line, make MatrixSolution object for each series,
    #Assign atributes to MatrixSolution object based on the series number
    with open(fileName, 'r') as configFile:
        notes = []

        for line in configFile:
            lines += 1
            splitLine = line.strip().split(maxsplit=15)

            if(splitLine == [] or splitLine[0] == "\n"):
                continue

            if splitLine[0] == "@SERIES":
                seriesNumber += 1
                designRow = 0
                positionRow = 0
                nominalsInPounds = 1

                seriesObjects.append(MatrixSolution())
                seriesObjects[seriesNumber].seriesNumber = seriesNumber

                seriesObjects[seriesNumber].positions = posObs[seriesNumber][0]
                seriesObjects[seriesNumber].observations = posObs[seriesNumber][1]
                continue

            if(splitLine[0][0] == "#"):
                note = " ".join(splitLine)
                notes.append(note)
                continue

            if splitLine[0] == "<Report-Number>":
                header["<Report-Number>"] = splitLine[1]
                continue

            if splitLine[0] == "<Restraint-ID>":
                header["<Restraint-ID>"] = splitLine[1]
                continue

            if splitLine[0] == "<Unc-Restraint>":
                header["<Unc-Restraint>"] = splitLine[1]
                continue

            if splitLine[0] == "<Random-Error>":
                header["<Random-Error>"] = splitLine[1]
                continue

            if splitLine[0] == "<Date>":
                seriesObjects[seriesNumber].date.append(str(splitLine[1]))
                seriesObjects[seriesNumber].date.append(str(splitLine[2]))
                seriesObjects[seriesNumber].date.append(str(splitLine[3]))

                seriesObjects[seriesNumber].reportNumber = header["<Report-Number>"]
                seriesObjects[seriesNumber].notes = notes
                continue

            if splitLine[0] == "<Technician-ID>":
                seriesObjects[seriesNumber].technicianId = splitLine[1]
                continue

            if splitLine[0] == "<Balance-ID>":
                seriesObjects[seriesNumber].balanceId = splitLine[1]
                continue

            if splitLine[0] == "<Check-Standard-ID>":
                seriesObjects[seriesNumber].checkStandardId = splitLine[1]
                continue

            if splitLine[0] == "<Direct-Readings>":
                seriesObjects[seriesNumber].directReadings = int(splitLine[1])
                continue

            if splitLine[0] == "<Direct-Reading-SF>":
                seriesObjects[seriesNumber].directReadingsSF = float(splitLine[1])
                continue

            if splitLine[0] == "<Pounds>":
                seriesObjects[seriesNumber].nominalsInPounds = int(splitLine[1])
                if int(splitLine[1]) == 1:
                    nominalsInPounds = 453.59237
                else:
                    nominalsInPounds = 1
                continue

            if splitLine[0] == "<Design-ID>":
                seriesObjects[seriesNumber].designId = splitLine[1]
                continue

            if splitLine[0] == "<Position>":
                seriesObjects[seriesNumber].weightIds.append(splitLine[1])

                #Make weight nominals array and set calculatedMasses to nominals for first-pass estimates. Initialize matrixY:
                if positionRow == 0:
                    seriesObjects[seriesNumber].weightNominals = np.zeros(shape=(1, seriesObjects[seriesNumber].positions))
                    seriesObjects[seriesNumber].ogNominals = np.zeros(shape=(1, seriesObjects[seriesNumber].positions))

                    seriesObjects[seriesNumber].calculatedMasses = np.zeros(shape=(1, seriesObjects[seriesNumber].positions))
                    seriesObjects[seriesNumber].matrixY = np.zeros(shape=(seriesObjects[seriesNumber].observations, 1))
                    seriesObjects[seriesNumber].referenceValues = np.zeros(shape=(1, seriesObjects[seriesNumber].positions))

                seriesObjects[seriesNumber].weightNominals[0, positionRow] = float(splitLine[2]) * nominalsInPounds
                seriesObjects[seriesNumber].ogNominals[0, positionRow] = float(splitLine[2])

                seriesObjects[seriesNumber].calculatedMasses[0, positionRow] = float(splitLine[2]) * nominalsInPounds

                seriesObjects[seriesNumber].weightDensities.append(float(splitLine[3]))
                seriesObjects[seriesNumber].weightCCEs.append(float(splitLine[4]))

                try:
                    seriesObjects[seriesNumber].referenceValues[0, positionRow] = float(splitLine[5])
                except IndexError:
                    seriesObjects[seriesNumber].referenceValues[0, positionRow] = 0
                positionRow += 1
                continue

            if splitLine[0] == "<Design>":
                if designRow == 0:
                    seriesObjects[seriesNumber].designMatrix = \
                        np.zeros(shape=(seriesObjects[seriesNumber].observations, seriesObjects[seriesNumber].positions))
                for i in range(1, len(splitLine)):
                    seriesObjects[seriesNumber].designMatrix[designRow, i - 1] = int(splitLine[i])
                designRow += 1
                continue

            if splitLine[0] == "<Restraint>":
                seriesObjects[seriesNumber].restraintPos = np.zeros(shape=(1, seriesObjects[seriesNumber].positions))
                for i in range(1, len(splitLine)):
                    seriesObjects[seriesNumber].restraintPos[0, i - 1] = int(splitLine[i])
                continue

            if splitLine[0] == "<Check-Standard>":
                seriesObjects[seriesNumber].checkStandardPos = np.zeros(shape=(1, seriesObjects[seriesNumber].positions))
                for i in range(1, len(splitLine)):
                    seriesObjects[seriesNumber].checkStandardPos[0, i - 1] = int(splitLine[i])
                continue

            if splitLine[0] == "<Linear-Combo>":
                combo = []
                for i in range(1, len(splitLine)):
                    combo.append(int(splitLine[i]))
                seriesObjects[seriesNumber].linearCombos.append(combo)
                continue

            if splitLine[0] == "<Pass-Down>":
                seriesObjects[seriesNumber].nextRestraint = np.zeros(shape=(1, seriesObjects[seriesNumber].positions))
                for i in range(1, len(splitLine)):
                    seriesObjects[seriesNumber].nextRestraint[0, i - 1] = int(splitLine[i])
                continue

            if splitLine[0] == "<Sigma-w>":
                seriesObjects[seriesNumber].sigmaW = float(splitLine[1])
                continue

            if splitLine[0] == "<Sigma-t>":
                seriesObjects[seriesNumber].sigmaT = float(splitLine[1])
                continue

            if splitLine[0] == "<sw-Mass>":
                seriesObjects[seriesNumber].swMass = float(splitLine[1])
                continue

            if splitLine[0] == "<sw-Density>":
                seriesObjects[seriesNumber].swDensity = float(splitLine[1])
                continue

            if splitLine[0] == "<sw-CCE>":
                seriesObjects[seriesNumber].swCCE = float(splitLine[1])
                continue

            if splitLine[0] == "<Balance-Reading>":
                readings = []
                for i in range(1, len(splitLine)):
                    readings.append(float(splitLine[i]))
                seriesObjects[seriesNumber].balanceReadings.append(readings)
                continue

            if splitLine[0] == "<Environmentals>":
                envs = []
                for i in range(1, 4):
                    envs.append(float(splitLine[i]))
                seriesObjects[seriesNumber].environmentals.append(envs)
                continue

            if splitLine[0] == "<Env-Corrections>":
                for i in range(1, 4):
                    seriesObjects[seriesNumber].envCorrections.append(float(splitLine[i]))
                continue

            if splitLine[0] == "<Gravity-Grad>":
                seriesObjects[seriesNumber].gravityGradient = float(splitLine[1])
                continue

            if splitLine[0] == "<COM-Diff>":
                seriesObjects[seriesNumber].heightDifferences.append(float(splitLine[1]))
                continue

            raise MARSException("UNKNOWN TAG AT LINE " + str(lines) + " IN CONFIGURATION FILE: " + str(splitLine[0]))

    return seriesObjects

def run(inputFile, writeOutFile=True):
    data = parse(inputFile)
    
    for series in data:
        series.solution(data)

    if(writeOutFile):
        writeOut(data)

    return data

if(__name__ == "__main__"):
    inputFile = sys.argv[1]
    run(inputFile)