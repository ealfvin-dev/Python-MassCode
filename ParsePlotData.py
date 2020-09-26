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

        if("LOAD" in line and "DELTA" in line):
            headerLine = lineNum + 1

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
    pass

def getAirDensities(fileText):
    pass
