def getDeltas(fileText):
    deltas = []
    seriesDeltas = []

    observations = 0
    headerLine = -9999
    lineNum = 0
    for line in fileText.splitlines():
        if(line.strip == ""):
            continue

        lineNum += 1
        if("OBSERVATIONS" in line):
            observations = int(line.split()[1])

        if("##METRICS##" in line):
            headerLine = lineNum + 2

        if(lineNum > headerLine and lineNum < headerLine + observations):
            seriesDeltas.append(float(line.split()[3]))

        if(lineNum == headerLine + observations):
            seriesDeltas.append(float(line.split()[3]))
            deltas.append(seriesDeltas)
            seriesDeltas = []

    return deltas

def getSws(fileText):
    sws = []

    for line in fileText.splitlines():
        if("ACCEPTED_SW" in line):
            sws.append(float(line.split()[1]))

    return sws

def getSensitivities(fileText):
    sensitivities = []
    seriesSensitivities = []

    observations = 0
    headerLine = -9999
    lineNum = 0
    for line in fileText.splitlines():
        if(line.strip == ""):
            continue

        lineNum += 1
        if("OBSERVATIONS" in line):
            observations = int(line.split()[1])

        if("##METRICS##" in line):
            headerLine = lineNum + 2

        if(lineNum > headerLine and lineNum < headerLine + observations):
            seriesSensitivities.append(float(line.split()[4]))

        if(lineNum == headerLine + observations):
            seriesSensitivities.append(float(line.split()[4]))
            sensitivities.append(seriesSensitivities)
            seriesSensitivities = []

    return sensitivities

def getAirDensities(fileText):
    airDensities = []
    seriesAirDensities = []

    observations = 0
    headerLine = -9999
    lineNum = 0
    for line in fileText.splitlines():
        if(line.strip == ""):
            continue

        lineNum += 1
        if("OBSERVATIONS" in line):
            observations = int(line.split()[1])

        if("##ENVIRONMENTALS" in line):
            headerLine = lineNum + 1

        if(lineNum > headerLine and lineNum < headerLine + observations):
            seriesAirDensities.append(float(line.split()[4]))

        if(lineNum == headerLine + observations):
            seriesAirDensities.append(float(line.split()[4]))
            airDensities.append(seriesAirDensities)
            seriesAirDensities = []

    return airDensities

def getNominals(fileText):
    nominals = []

    targetLine = -9999
    units = "g"
    lineNum = 0
    for line in fileText.splitlines():
        if(line.strip == ""):
            continue

        lineNum += 1
        if("NOMINAL" in line and "CCE" in line and "CORRECTION" in line):
            targetLine = lineNum + 3

        if(lineNum == targetLine - 2):
            if("lb" in line):
                units = "lb"
            else:
                units = "g"
        
        if(lineNum == targetLine):
            nominals.append(line.split()[1] + " " + units)

    return nominals