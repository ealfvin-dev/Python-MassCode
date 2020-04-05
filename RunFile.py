import sys
import numpy as np
from statistics import mean, stdev
from tabulate import tabulate
from SeriesReduction import MatrixSolution

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
                sys.exit("CONFIGURATION FILE EXCEEDS 5000 LINE LIMIT")

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

            sys.exit("UNKNOWN TAG AT LINE " + str(lines) + " IN CONFIGURATION FILE: " + str(splitLine[0]))

    return seriesObjects

def writeOut(seriesList):
    f = open(seriesList[0].reportNumber + "-out.txt", 'w')

    for series in seriesList:
        if(series.seriesNumber == 0):
            for note in series.notes:
                f.write(note + "\n")

            f.write("\n")

            f.write(str(series.reportNumber) + "\n\n")

        f.write("SERIES " + str(series.seriesNumber + 1) + "\n\n")

        f.write("OPERATOR  " + str(series.technicianId) + "\n")
        f.write("BALANCE ID  " + str(series.balanceId) + "\n")
        f.write("DATE  " + " ".join(series.date) + "\n\n")

        restraint = []
        for i in range(len(series.restraintPos[0])):
            if(series.restraintPos[0][i] == 1):
                restraint.append(series.weightIds[i])

        check = ""
        for i in range(len(series.checkStandardPos[0])):
            if(series.checkStandardPos[0][i] == 1):
                check += series.weightIds[i]

        for i in range(len(series.checkStandardPos[0])):
            if(series.checkStandardPos[0][i] == -1):
                check += "-" + series.weightIds[i]

        f.write("---RESTRAINT  " + "+".join(restraint) + "\n")
        f.write("---CHECK STANDARD  " + check + "\n\n")

        f.write("        T(" + chr(730) + "C) P(mmHg) RH(%)  AIR DENSITY(g/cm) (CORRECTED ENVIRONMENTALS)\n")
        table = []
        for i in range(len(series.environmentals)):
            line = []
            line.append(str(i + 1) + ": ")
            line.append(series.environmentals[i][0] - series.envCorrections[0])
            line.append(series.environmentals[i][1] - series.envCorrections[1])
            line.append(series.environmentals[i][2] - series.envCorrections[2])

            line.append(float(series.airDensities[i]))
            table.append(line)

        transposed = []
        for i in range(3):
            transposed.append([row[i] for row in series.environmentals])

        table.append(["AVE: ", mean(transposed[0]) - series.envCorrections[0], mean(transposed[1]) - series.envCorrections[1], mean(transposed[2]) - series.envCorrections[2], \
            mean(series.airDensities)])

        table.append(["CORR: ", series.envCorrections[0], series.envCorrections[1], series.envCorrections[2]])

        f.write(tabulate(table, tablefmt="plain", floatfmt=("", ".2f", ".2f", ".2f", ".8f")) + "\n\n")

        f.write("BALANCE OBSERVATIONS\n")
        table = []
        for i in range(len(series.balanceReadings)):
            line = []
            line.append(str(i + 1) + ": ")
            line.append(str(series.balanceReadings[i][0]))
            try:
                line.append(str(series.balanceReadings[i][1]))
                line.append(str(series.balanceReadings[i][2]))
                line.append(str(series.balanceReadings[i][3]))
            except IndexError:
                pass

            table.append(line)

        f.write(tabulate(table, tablefmt="plain") + "\n\n")

        f.write("SENSITIVITIES\n")
        table = []
        for i in range(len(series.balanceReadings)):
            line = []
            load = series.loads[i]

            line.append(str(i + 1) + ": ")
            line.append(load)
            line.append(float(series.sensitivities[i]*1000))
            line.append(float(series.aveSensitivities[load]*1000))

            table.append(line)

        f.write(tabulate(table, headers=["", "LOAD\n(g)", "OBS SENSITIVITY\n(mg/DIV)", "AVE SENSITIVITY\n(mg/DIV)"], floatfmt=("", ".5f", ".5f", ".5f"), tablefmt="plain", colalign=("left", "center", "center", "center")) + "\n\n")

        table = []
        for i in range(len(series.weightIds)):
            line = []
            line.append(series.weightIds[i])
            if(int(series.ogNominals[0][i]) == float(series.ogNominals[0][i])):
                line.append(int(series.ogNominals[0][i]))
            else:
                line.append(float(series.ogNominals[0][i]))

            line.append(series.weightDensities[i])
            line.append(series.weightCCEs[i])
            line.append(float(series.matrixBHat[i][0]))
            
            table.append(line)

        f.write(tabulate(table, headers=["WEIGHT ID", "NOMINAL", "DENSITY (g/cm)", "CCE (/" + chr(730) + "C)", "TRUE MASS (g)"], floatfmt=("", "", ".5f", ".7f", ".8f"), colalign=("left", "center", "center", "center", "decimal")) + "\n\n")

    f.close()

def run(inputFile):
    data = parse(inputFile)
    
    for series in data:
        series.solution(data)

    writeOut(data)

if(__name__ == "__main__"):
    inputFile = sys.argv[1]
    run(inputFile)