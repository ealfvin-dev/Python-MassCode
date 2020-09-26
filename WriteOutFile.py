from statistics import mean, stdev
from tabulate import tabulate
import os

def writeOut(seriesList, basePath):
    outFileName = seriesList[0].reportNumber + "-out.txt"
    outFileLocation = os.path.join(basePath, outFileName)
    f = open(outFileLocation, 'w')

    for series in seriesList:
        if(series.seriesNumber == 0):
            writeHeader(series, f)

        f.write("***SERIES " + str(series.seriesNumber + 1) + "***\n\n")

        writeSeriesMetaData(series, f)
        writeSeriesRestraint(series, f)
        writeSeriesCheck(series, f)
        writeSentitivityWeight(series, f)
        writeDesignData(series, f)
        writeEnvironmentals(series, f)
        writeObservations(series, f)
        writeSensitivities(series, f)
        writeFTest(series, f)
        writeTTest(series, f)
        writeMasses(series, f)

    f.close()

def writeHeader(series, f):
    for note in series.notes:
        f.write(note + "\n")

    f.write("\n")

    f.write("REPORT_NUMBER  " + series.reportNumber + "\n")
    f.write("RESTRAINT_ID  " + series.restraintID + "\n\n")

def writeSeriesMetaData(series, f):
    f.write("DATE  " + " ".join(series.date) + "\n\n")
    f.write("OPERATOR_ID  " + str(series.technicianId) + "\n")
    f.write("BALANCE_ID  " + str(series.balanceId) + "\n\n")

def writeSeriesRestraint(series, f):
    restraint = []
    for i in range(len(series.restraintPos[0])):
        if(series.restraintPos[0][i] == 1):
            restraint.append(series.weightIds[i])

    f.write("RESTRAINT  " + "+".join(restraint) + "\n\n")

def writeSeriesCheck(series, f):
    check = ""
    for i in range(len(series.checkStandardPos[0])):
        if(series.checkStandardPos[0][i] == 1):
            check += series.weightIds[i]

    for i in range(len(series.checkStandardPos[0])):
        if(series.checkStandardPos[0][i] == -1):
            check += "-" + series.weightIds[i]

    f.write("CHECK_STANDARD_ID  " + series.checkStandardId + "\n")
    f.write("CHECK_STANDARD  " + check + "\n\n")

def writeSentitivityWeight(series, f):
    f.write("SENSITIVITY_WEIGHT_MASS  " + str(series.swMass) + "\n")
    f.write("SENSITIVITY_WEIGHT_DENSITY  " + str(series.swDensity) + "\n")
    f.write("SENSITIVITY_WEIGHT_CCE  " + str(series.swCCE) + "\n\n")

def writeDesignData(series, f):
    f.write("DESIGN_ID  " + str(series.designId) + "\n")
    f.write("POSITIONS  " + str(series.positions) + "\n")
    f.write("OBSERVATIONS  " + str(series.observations) + "\n\n")

def writeEnvironmentals(series, f):
    f.write("##ENVIRONMENTALS (CORRECTED)##\n")
    f.write("        T(" + chr(730) + "C) P(mmHg) RH(%)  AIR DENSITY(g/cm)\n")
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

def writeObservations(series, f):
    f.write("##BALANCE READINGS##\n")
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

def writeSensitivities(series, f):
    f.write("##METRICS##\n")
    table = []
    for i in range(len(series.balanceReadings)):
        line = []
        load = series.loads[i]
        line.append(str(i + 1) + ": ")

        if(int(load) == float(load)):
            line.append(int(load))
        else:
            line.append(float(load))

        line.append(series.matrixY[i][0] * 1000)
        line.append(series.deltas[i])

        if(series.directReadings == 0):
            line.append(float(series.sensitivities[i]*1000))
        else:
            line.append(float(series.sensitivities[i]))

        try:
            line.append(float(series.aveSensitivities[load]*1000))
        except:
            line.append(float(series.aveSensitivities["balance"]))

        table.append(line)

    f.write(tabulate(table, headers=["", "LOAD\n(g)", "A(I)\n(mg)", "DELTA\n(mg)", "OBS SENSITIVITY\n(mg/DIV)", "AVE SENSITIVITY\n(mg/DIV)"],\
        floatfmt=("", ".5f", ".5f", ".5f", ".5f", ".5f"), tablefmt="plain",\
        colalign=("left", "center", "decimal", "decimal", "decimal", "decimal")) + "\n\n")

def writeFTest(series, f):
    f.write("##STATISTICS##\n")
    if(series.fValue > series.fCritical):
        f.write("################################################################\n")

    f.write("#F-TEST\n")
    f.write("ACCEPTED_SW  " + str(round(series.sigmaW, 6)) + " MG\n")
    f.write("OBSERVED_SW  " + str(round(series.swObs, 6)) + " MG\n")
    f.write("CRITICAL_F-VALUE  " + str(round(series.fCritical, 2)) + "\n")
    f.write("OBSERVED_F-VALUE  " + str(round(series.fValue, 2)) + "\n")

    if(series.fValue <= series.fCritical):
        f.write("--------\n| PASS |\n--------\n\n")
    else:
        f.write("--------\n| FAIL |\n--------\n\n")

    if(series.fValue > series.fCritical):
        f.write("################################################################\n\n")

def writeTTest(series, f):
    if(series.tValue > series.tCritical):
        f.write("################################################################\n")

    f.write("#T-TEST\n")
    f.write("ACCEPTED_CHECK_STANDARD_CORRECTION  " + str(round(series.acceptedCheckCorrection, 6)) + " MG\n")
    f.write("OBSERVED_CHECK_STANDARD_CORRECTION  " + str(round(series.calculatedCheckCorrection, 6)) + " MG\n")
    f.write("ACCEPTED_ST  " + str(round(series.sigmaT, 6)) + " MG\n")
    f.write("CRITICAL_T-VALUE  " + str(round(series.tCritical, 2)) + "\n")
    f.write("OBSERVED_T-VALUE  " + str(round(series.tValue, 2)) + "\n")

    if(abs(series.tValue) <= series.tCritical):
        f.write("--------\n| PASS |\n--------\n\n")
    else:
        f.write("--------\n| FAIL |\n--------\n")

    if(series.tValue > series.tCritical):
        f.write("################################################################\n\n")

def writeMasses(series, f):
    table = []
    if(series.nominalsInGrams == 1):
        units = "g"
    else:
        units = "lb"

    for i in range(len(series.weightIds)):
        line = []
        line.append(series.weightIds[i])
        if(int(series.ogNominals[0][i]) == float(series.ogNominals[0][i])):
            line.append(int(series.ogNominals[0][i]))
        else:
            line.append(float(series.ogNominals[0][i]))

        line.append(series.weightDensities[i])
        line.append(series.weightCCEs[i])
        line.append(float(series.calculatedMasses[0][i]))
        line.append(float(series.calculatedMasses[0][i] - series.weightNominals[0][i]) * 1000)
        
        table.append(line)

    f.write(tabulate(table, headers=["WEIGHT ID", "NOMINAL\n(" + units + ")", "DENSITY\n(g/cm)", "CCE\n(/" + chr(730) + "C)", "TRUE MASS\n(g)", "CORRECTION\n(mg)"],\
        floatfmt=("", "", ".5f", ".7f", ".8f", ".5f"),\
        colalign=("left", "center", "center", "center", "decimal", "decimal")) + "\n\n")