from statistics import mean, stdev
from tabulate import tabulate

def writeOut(seriesList):
    f = open(seriesList[0].reportNumber + "-out.txt", 'w')

    for series in seriesList:
        if(series.seriesNumber == 0):
            for note in series.notes:
                f.write(note + "\n")

            f.write("\n")

            f.write(str(series.reportNumber) + "\n\n")

        f.write("***SERIES " + str(series.seriesNumber + 1) + "***\n\n")

        f.write("OPERATOR  " + str(series.technicianId) + "\n")
        f.write("BALANCE_ID  " + str(series.balanceId) + "\n")
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

        #Air Densities
        f.write("##ENVIRONMENTALS##\n")
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

        #Observations
        f.write("##BALANCE OBSERVATIONS##\n")
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

        #Sensitivities
        f.write("##SENSITIVITIES##\n")
        table = []
        for i in range(len(series.balanceReadings)):
            line = []
            load = series.loads[i]

            line.append(str(i + 1) + ": ")

            if(int(load) == float(load)):
                line.append(int(load))
            else:
                line.append(float(load))

            if(series.directReadings == 0):
                line.append(float(series.sensitivities[i]*1000))
            else:
                line.append(float(series.sensitivities[i]))

            try:
                line.append(float(series.aveSensitivities[load]*1000))
            except:
                line.append(float(series.aveSensitivities["balance"]))

            table.append(line)

        f.write(tabulate(table, headers=["", "LOAD\n(g)", "OBS SENSITIVITY\n(mg/DIV)", "AVE SENSITIVITY\n(mg/DIV)"], floatfmt=("", ".5f", ".5f", ".5f"), tablefmt="plain", colalign=("left", "center", "center", "center")) + "\n\n")

        #Deltas
        f.write("##DELTAS##\n")
        table = []
        for i in range(len(series.balanceReadings)):
            line = []
            load = series.loads[i]

            line.append(str(i + 1) + ": ")

            if(int(load) == float(load)):
                line.append(int(load))
            else:
                line.append(float(load))

            line.append(series.deltas[i])

            table.append(line)

        f.write(tabulate(table, headers=["", "LOAD\n(g)", "DELTA\n(MG)"], floatfmt=("", ".5f", ".5f"), tablefmt="plain", colalign=("left", "center", "decimal")) + "\n\n")

        #Statistics
        #F-test
        f.write("##STATISTICS##\n")
        if(series.fValue > series.fCritical):
            f.write("################################################################\n")

        f.write("#F-TEST\n")
        f.write("ACCEPTED_SW = " + str(round(series.sigmaW, 6)) + " MG\n")
        f.write("OBSERVED_SW = " + str(round(series.swObs, 6)) + " MG\n")
        f.write("CRITICAL_F-VALUE = " + str(round(series.fCritical, 2)) + "\n")
        f.write("OBSERVED_F-VALUE = " + str(round(series.fValue, 2)) + "\n")

        if(series.fValue <= series.fCritical):
            f.write("--------\n| PASS |\n--------\n")
        else:
            f.write("--------\n| FAIL |\n--------\n")

        if(series.fValue > series.fCritical):
            f.write("################################################################\n")

        #T-test
        if(series.tValue > series.tCritical):
            f.write("################################################################\n")

        f.write("#T-TEST\n")
        f.write("ACCEPTED_CHECK_STANDARD_CORRECTION = " + str(series.acceptedCheckCorrection) + " MG\n")
        f.write("OBSERVED_CHECK_STANDARD_CORRECTION = " + str(round(series.calculatedCheckCorrection, 6)) + " MG\n")
        f.write("CRITICAL_T-VALUE = " + str(round(series.tCritical, 2)) + "\n")
        f.write("OBSERVED_T-VALUE = " + str(round(series.tValue, 2)) + "\n")

        if(series.tValue <= series.tCritical):
            f.write("--------\n| PASS |\n--------\n\n")
        else:
            f.write("--------\n| FAIL |\n--------\n")

        if(series.tValue > series.tCritical):
            f.write("################################################################\n\n")

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