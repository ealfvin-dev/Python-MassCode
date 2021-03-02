#Module to hold functions that perform checks on user input data and results

from numpy import asarray, matmul, matrix

#determineIfDirectReadings (helper)
#checkReportNumber
#checkStructure
#checkTags
#checkIfAllTags
#checkForRepeats
#checkNumObservations
#checkVectors
#checkRestraints
#runSecondaryChecks
#checkResults

def determineIfDirectReadings(inputText):
    #Helper function to determine if direct readings are used
    for line in inputText.splitlines():
        if(line.split() == []):
            continue

        if(line.split()[0] == "<Direct-Readings>"):
            try:
                dr = line.split()[1]
                if(dr == "1"):
                    return True
                else:
                    return False
            except IndexError:
                return False

    return False

def checkReportNumber(inputText, sendError, highlightError):
    #Check that report number does not have spaces
    lineNum = 0

    for line in inputText.splitlines():
        lineNum += 1
        if(line.split() == []):
            continue

        if(line.split()[0] == "<Report-Number>"):
            try:
                line.split()[2]
                sendError("SERIES 1, LINE " + str(lineNum) + ": ENTER A REPORT NUMBER WITHOUT SPACES")
                highlightError(1, lineNum)
                return False
            except IndexError:
                break
    return True

def checkStructure(seriesTexts, sendError, highlightError, goToSeries):
    #Check structure of input file in UI (split into series)
    seriesNum = 0

    for seriesText in seriesTexts:
        seriesNum += 1

        numSeries = 0
        lineNum = 0

        for line in seriesText.splitlines():
            lineNum += 1
            line = line.split()

            if(line == []):
                continue

            if(line[0] == "@SERIES"):
                numSeries += 1

                #Check if more than 1 series is entered in each text block
                if(numSeries > 1):
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": ENTER ONE @SERIES BLOCK PER TAB\nUSE THE SPLIT BUTTON TO SPLIT INPUT INTO INDIVIDUAL SERIES")
                    highlightError(seriesNum, lineNum)
                    return False

        #Check that @SERIES marks the start of the series
        if(numSeries == 0):
            sendError("SERIES " + str(seriesNum) + ": THERE MUST BE AN @SERIES ANNOTATION BEFORE <Date> TO MARK THE BEGINNING OF EACH SERIES")
            goToSeries(seriesNum, True)
            return False

    return True

def checkTags(seriesTexts, seriesNum, highlightError, sendError):
    #Checks if currently written tags exist in the known tags dictionary
    acceptedTags = {"@SERIES": False, \
                    "<Report-Number>": False, \
                    "<Restraint-ID>": False, \
                    "<Unc-Restraint>": False, \
                    #"<Random-Error>": False, \
                    "<Date>": False, \
                    "<Technician-ID>": False, \
                    "<Check-ID>": False, \
                    "<Balance-ID>": False, \
                    "<Direct-Readings>": False, \
                    "<Direct-Reading-SF>": False, \
                    "<Design-ID>": False, \
                    "<Design>": False, \
                    "<Grams>": False, \
                    "<Position>": False, \
                    "<Restraint>": False, \
                    "<Check-Standard>": False, \
                    "<Pass-Down>": False, \
                    "<Sigma-t>": False, \
                    "<Sigma-w>": False, \
                    "<sw-Mass>": False, \
                    "<sw-Density>": False, \
                    "<sw-CCE>": False, \
                    "<Balance-Reading>": False, \
                    "<Environmentals>": False, \
                    "<Env-Corrections>": False, \
                    "<Gravity-Grad>": False, \
                    "<Gravity-Local>": False, \
                    "<Height>": False}

    seriesNumber = 0

    for seriesText in seriesTexts:
        seriesNumber += 1
        lineNum = 0

        for line in seriesText.splitlines():
            lineNum += 1

            if(line.split() == []):
                continue

            if(line.split()[0][0] == "#"):
                continue

            try:
                acceptedTags[line.split()[0]]
            except KeyError:
                if(seriesNum):
                    snText = str(seriesNum)
                else:
                    snText = str(seriesNumber)

                errorMessage = "SERIES " + snText + " LINE " + str(lineNum) + ": UNKNOWN TAG " + line.split()[0]
                highlightError(int(snText), lineNum)
                sendError(errorMessage)
                return False
                    
    return True

def checkIfAllTags(seriesTexts, sendError, goToSeries):
    #Checks if all tags in known tags dictionary exist in each seriesTexts
    seriesNum = 1

    for seriesText in seriesTexts:
        if(determineIfDirectReadings(seriesText)):
            tagSet = {"<Report-Number>": False, \
                        "<Restraint-ID>": False, \
                        "<Unc-Restraint>": False, \
                        #"<Random-Error>": False, \
                        "<Date>": False, \
                        "<Technician-ID>": False, \
                        "<Check-ID>": False, \
                        "<Balance-ID>": False, \
                        "<Direct-Readings>": False, \
                        "<Direct-Reading-SF>": False, \
                        "<Design-ID>": False, \
                        "<Design>": False, \
                        "<Grams>": False, \
                        "<Position>": False, \
                        "<Restraint>": False, \
                        "<Check-Standard>": False, \
                        "<Pass-Down>": False, \
                        "<Sigma-t>": False, \
                        "<Sigma-w>": False, \
                        "<Balance-Reading>": False, \
                        "<Environmentals>": False, \
                        "<Env-Corrections>": False}
        else:
            tagSet = {"<Report-Number>": False, \
                        "<Restraint-ID>": False, \
                        "<Unc-Restraint>": False, \
                        #"<Random-Error>": False, \
                        "<Date>": False, \
                        "<Technician-ID>": False, \
                        "<Check-ID>": False, \
                        "<Balance-ID>": False, \
                        "<Direct-Readings>": False, \
                        "<Design-ID>": False, \
                        "<Design>": False, \
                        "<Grams>": False, \
                        "<Position>": False, \
                        "<Restraint>": False, \
                        "<Check-Standard>": False, \
                        "<Pass-Down>": False, \
                        "<Sigma-t>": False, \
                        "<Sigma-w>": False, \
                        "<sw-Mass>": False, \
                        "<sw-Density>": False, \
                        "<sw-CCE>": False, \
                        "<Balance-Reading>": False, \
                        "<Environmentals>": False, \
                        "<Env-Corrections>": False}

        #Record required tags found in the series
        for line in seriesText.splitlines():
            if(line.split() == []):
                continue

            try:
                tagSet[line.split()[0]]
                tagSet[line.split()[0]] = True
            except KeyError:
                pass

        #Check if all keys in tag set are now true (header tags only in series 1)
        for tag, value in tagSet.items():
            if(value == True):
                continue

            if((tag == "<Report-Number>" or tag == "<Restraint-ID>" or tag == "<Unc-Restraint>") and seriesNum != 1):
                continue

            sendError(tag + " DOES NOT EXIST IN SERIES " + str(seriesNum))
            goToSeries(seriesNum, True)
            return False
                
        seriesNum += 1
    return True

def checkForRepeats(seriesTexts, sendError, highlightError):
    #Check for repeated tags
    seriesNum = 0

    singleTags = {"<Report-Number>": 0,\
        "<Restraint-ID>": 0,\
        "<Unc-Restraint>": 0,\
        #"<Random-Error>": 0,\
        "<Date>": 0,\
        "<Technician-ID>": 0,\
        "<Check-ID>": 0,\
        "<Balance-ID>": 0,\
        "<Direct-Readings>": 0,\
        "<Direct-Reading-SF>": 0,\
        "<Design-ID>": 0,\
        "<Grams>": 0,\
        "<Restraint>": 0,\
        "<Check-Standard>": 0,\
        "<Pass-Down>": 0,\
        "<Sigma-t>": 0,\
        "<Sigma-w>": 0,\
        "<sw-Mass>": 0,\
        "<sw-Density>": 0,\
        "<sw-CCE>": 0,\
        "<Gravity-Local>": 0,\
        "<Gravity-Grad>": 0}

    for seriesText in seriesTexts:
        seriesNum += 1
        lineNum = 0
        
        for line in seriesText.splitlines():
            lineNum += 1
            line = line.split()

            if(line == []):
                continue

            try:
                singleTags[line[0]] += 1
            except KeyError:
                continue

            if(singleTags[line[0]] > 1):
                sendError("SERIES " + str(seriesNum) + ": MULTIPLE " + line[0] + " TAGS FOUND\nMARK THE START OF EACH SERIES WITH THE @SERIES ANNOTATION BEOFRE <Date>")
                highlightError(seriesNum, lineNum)
                return False

        for key, value in singleTags.items():
            singleTags[key] = 0 

    return True

def checkInputValues(seriesTexts, sendError, highlightError):
    seriesNum = 0

    for seriesText in seriesTexts:
        seriesNum += 1
        lineNum = 0

        for line in seriesText.splitlines():
            lineNum += 1
            line = line.split()

            if(line == []):
                continue

            #Check if report number is entered without spaces
            if(line[0] == "<Report-Number>"):
                try:
                    line[1]
                except IndexError:
                    sendError("SERIES " + str(seriesNum) + ", LINE " + str(lineNum) + ": REPORT NUMBER IS NEEDED")
                    highlightError(seriesNum, lineNum)
                    return False

                try:
                    line[2]
                    sendError("SERIES " + str(seriesNum) + ", LINE " + str(lineNum) + ": ENTER A REPORT NUMBER WITHOUT SPACES")
                    highlightError(seriesNum, lineNum)
                    return False
                except IndexError:
                    continue

            #Check format of date
            if(line[0] == "<Date>"):
                if(len(line) != 4):
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": DATE IS ENTERED IN THE FORM <Date>  MM DD YYYY")
                    highlightError(seriesNum, lineNum)
                    return False
                else:
                    continue

            #Check direct readings value
            if(line[0] == "<Direct-Readings>"):
                try:
                    dr = line[1]
                    if(dr == "1" or dr == "0"):
                        continue
                    else:
                        sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ":\nUNKNOWN DIRECT READING VALUE. (1=DIRECT READINGS, 0=DOUBLE SUBSTITUTIONS)")
                        highlightError(seriesNum, lineNum)
                        return False
                except IndexError:
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ":\nDIRECT READING VALUE NEEDED. (1=DIRECT READINGS, 0=DOUBLE SUBSTITUTIONS)")
                    highlightError(seriesNum, lineNum)
                    return False

            #Check format of environmentals
            if(line[0] == "<Environmentals>"):
                try:
                    line[3]
                except IndexError:
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": ENVIRONMENTALS ARE ENTERED IN THE FORM <Environmentals>  T P RH")
                    highlightError(seriesNum, lineNum)
                    return False

                try:
                    line[4]
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": ENVIRONMENTALS ARE ENTERED IN THE FORM <Environmentals>  T P RH")
                    highlightError(seriesNum, lineNum)
                    return False
                except IndexError:
                    continue

            #Check format of env corrections
            if(line[0] == "<Env-Corrections>"):
                try:
                    line[3]
                except IndexError:
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": ENVIRONMENTAL CORRECTIONS ARE ENTERED IN THE FORM <Env-Corrections>  T P RH")
                    highlightError(seriesNum, lineNum)
                    return False

                try:
                    line[4]
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": ENVIRONMENTAL CORRECTIONS ARE ENTERED IN THE FORM <Env-Corrections>  T P RH")
                    highlightError(seriesNum, lineNum)
                    return False
                except IndexError:
                    continue

            #Check format of positions
            if(line[0] == "<Position>"):
                try:
                    float(line[2])
                    float(line[3])
                    float(line[4])
                    continue
                except (ValueError, IndexError):
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": POSITIONS ARE ENTERED IN THE FORM\n<Position>  WEIGHT_ID  NOMINAL  DENSITY  CCE  (CORRECTION)\nWEIGHT_ID CANNOT CONTAIN SPACES")
                    highlightError(seriesNum, lineNum)
                    return False

            #Check that tags not specially checked above have numeric-type values
            if(\
            #line[0] == "<Restraint-ID>" or\
            line[0] == "<Unc-Restraint>" or\
            #line[0] == "<Random-Error>" or\
            #line[0] == "<Technician-ID>" or\
            #line[0] == "<Check-ID>" or\
            #line[0] == "<Balance-ID>" or\
            line[0] == "<Direct-Reading-SF>" or\
            #line[0] == "<Design-ID>" or\
            line[0] == "<Design>" or\
            line[0] == "<Grams>" or\
            line[0] == "<Restraint>" or\
            line[0] == "<Check-Standard>" or\
            line[0] == "<Pass-Down>" or\
            line[0] == "<Sigma-t>" or\
            line[0] == "<Sigma-w>" or\
            line[0] == "<sw-Mass>" or\
            line[0] == "<sw-Density>" or\
            line[0] == "<sw-CCE>" or\
            line[0] == "<Balance-Reading>" or\
            line[0] == "<Gravity-Grad>" or\
            line[0] == "<Gravity-Local>" or\
            line[0] == "<Height>"):
                try:
                    line[1]
                except IndexError:
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": NO VALUE PROVIDED FOR " + line[0])
                    highlightError(seriesNum, lineNum)
                    return False

                try:
                    float(line[1])
                    continue
                except ValueError:
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": VALUE FOR " + line[0] + " MUST BE A NUMBER")
                    highlightError(seriesNum, lineNum)
                    return False

            #Check that other tag values exist (do not need to be ints)
            if(\
            line[0] == "<Restraint-ID>" or\
            line[0] == "<Technician-ID>" or\
            line[0] == "<Check-ID>" or\
            line[0] == "<Balance-ID>" or\
            line[0] == "<Design-ID>"):
                try:
                    line[1]
                    continue
                except IndexError:
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": NO VALUE PROVIDED FOR " + line[0])
                    highlightError(seriesNum, lineNum)
                    return False

    return True

def checkVectors(seriesTexts, sendError, highlightError, goToSeries):
    seriesNum = 0

    for seriesText in seriesTexts:
        numPositions = 0
        lineNum = 0
        seriesNum += 1

        #Iterate twice through to grab numPositions and check vector lengths
        for line in seriesText.splitlines():
            line = line.split()

            if(line == []):
                continue

            if(line[0] == "<Position>"):
                numPositions += 1

        for line in seriesText.splitlines():
            lineNum += 1
            line = line.split()

            if(line == []):
                continue

            if(line[0] == "<Design>"):
                if(len(line[1:]) != numPositions):
                    sendError("VECTOR LENGTH DOES NOT MATCH NUMBER OF POSITIONS")
                    highlightError(seriesNum, lineNum)
                    return False

            if(line[0] == "<Restraint>"):
                if(len(line[1:]) != numPositions):
                    sendError("VECTOR LENGTH DOES NOT MATCH NUMBER OF POSITIONS")
                    highlightError(seriesNum, lineNum)
                    return False

            if(line[0] == "<Check-Standard>"):
                if(len(line[1:]) != numPositions):
                    sendError("VECTOR LENGTH DOES NOT MATCH NUMBER OF POSITIONS")
                    highlightError(seriesNum, lineNum)
                    return False

            if(line[0] == "<Pass-Down>"):
                if(len(line[1:]) != numPositions):
                    sendError("VECTOR LENGTH DOES NOT MATCH NUMBER OF POSITIONS")
                    highlightError(seriesNum, lineNum)
                    return False

    return True

def checkDesignVsWeights(seriesTexts, sendError, highlightError, goToSeries):
    seriesNum = 0

    for seriesText in seriesTexts:
        lineNum = 0
        nominals = []
        seriesNum += 1

        #Iterate first time to grab position nominals
        for line in seriesText.splitlines():
            line = line.split()

            if(line == []):
                continue

            if(line[0] == "<Position>"):
                nominals.append(float(line[2]))

        for line in seriesText.splitlines():
            lineNum += 1
            line = line.split()

            if(line == []):
                continue

            if(line[0] == "<Design>"):
                nominalsArr = asarray(nominals)
                designLine = line[1:]

                mass1Pos = [0] * len(designLine)
                mass2Pos = [0] * len(designLine)

                for p in range(len(designLine)):
                    if(designLine[p] == "1"):
                        mass1Pos[p] = 1
                    if(designLine[p] == "-1"):
                        mass2Pos[p] = 1

                mass1Arr = asarray(mass1Pos)
                mass2Arr = asarray(mass2Pos)

                mass1 = matmul(mass1Arr, matrix.transpose(nominalsArr))
                mass2 = matmul(mass2Arr, matrix.transpose(nominalsArr))

                if(abs(mass1 - mass2) > 1e-6):
                    sendError("SERIES " + str(seriesNum) + ": DESIGN LINE IS NOT COMPATIBLE WITH WEIGHT NOMINALS")
                    highlightError(seriesNum, lineNum)
                    return False

    return True

def checkRestraints(seriesTexts, numberOfSeries, sendError, highlightError, goToSeries):
    seriesNum = 0
    previousPassDownNominal = 0
    
    for seriesText in seriesTexts:
        seriesNum += 1

        lineNum = 0
        checkPos = []
        restraintPos = []
        passDownPos = []
        nominals = []
        restraintLine = 0

        for line in seriesText.splitlines():
            lineNum += 1
            line = line.split()

            if(line == []):
                continue

            if(line[0] == "<Position>"):
                nominals.append(float(line[2]))

            #Make sure all connected series have results passed down
            if(line[0] == "<Pass-Down>" and seriesNum < numberOfSeries):
                for p in range(len(line[1:])):
                    try:
                        passDownPos.append(int(line[1:][p]))
                    except ValueError:
                        sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": INCORRECT DATA ENTRY")
                        highlightError(seriesNum, lineNum)
                        return False

                if(sum(passDownPos) == 0):
                    sendError("NO RESTRAINT PASSED TO SERIES " + str(seriesNum + 1))
                    highlightError(seriesNum, lineNum)
                    return False
                else:
                    continue

            #Check restraint and check positions
            if(line[0] == "<Check-Standard>"):
                for p in line[1:]:
                    try:
                        checkPos.append(int(p))
                    except ValueError:
                        sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": INCORRECT DATA ENTRY")
                        highlightError(seriesNum, lineNum)
                        return False

                if(checkPos == restraintPos):
                    sendError("SERIES " + str(seriesNum) + ": CHECK STANDARD AND RESTRAINT ARE IN THE SAME POSITION")
                    highlightError(seriesNum, lineNum)
                    return False

            if(line[0] == "<Restraint>"):
                restraintLine = lineNum
                for p in line[1:]:
                    try:
                        restraintPos.append(int(p))
                    except ValueError:
                        sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": INCORRECT DATA ENTRY")
                        highlightError(seriesNum, lineNum)
                        return False

                if(checkPos == restraintPos):
                    sendError("SERIES " + str(seriesNum) + ": CHECK STANDARD AND RESTRAINT ARE IN THE SAME POSITION")
                    highlightError(seriesNum, lineNum)
                    return False

        #Check restraint nominal vs restraint passed down
        nominalsArr = asarray(nominals)
        restraintPosArr = asarray(restraintPos)

        if(seriesNum > 1):
            d = matmul(restraintPosArr, matrix.transpose(nominalsArr)) - previousPassDownNominal
            
            if(abs(d) > 1e-6):
                sendError("SERIES " + str(seriesNum) + ": RESTRAINT NOMINAL DOES NOT MATCH RESTRAINT PASSED DOWN FROM SERIES " + str(seriesNum - 1))
                highlightError(seriesNum, restraintLine)
                return False

        if(seriesNum < numberOfSeries):
            passDownPosArr = asarray(passDownPos)
            previousPassDownNominal = matmul(passDownPosArr, matrix.transpose(nominalsArr))

    return True

def checkNumObservations(seriesTexts, sendError, highlightError, goToSeries):
    #Runs other required consistency checks on user input
    seriesNum = 0

    for seriesText in seriesTexts:
        seriesNum += 1

        lineNum = 0
        designObs = 0
        numObs = 0
        numEnvs = 0
        obsStartLine = 0
        envStartLine = 0

        for line in seriesText.splitlines():
            lineNum += 1
            line = line.split()

            if(line == []):
                continue

            #Count number of observations, balace readings, env lines provided
            if(line[0] == "<Design>"):
                designObs += 1
                continue

            if(line[0] == "<Balance-Reading>"):
                numObs += 1
                if(obsStartLine == 0): obsStartLine = lineNum
                continue

            if(line[0] == "<Environmentals>"):
                numEnvs += 1
                if(envStartLine == 0): envStartLine = lineNum
                continue

        #Check number of balace readings
        if(numObs != designObs):
            sendError("SERIES " + str(seriesNum) + ": NUMBER OF BALANCE OBSERVATIONS DO NOT MATCH THE DESIGN")
            highlightError(seriesNum, obsStartLine, obsStartLine + numObs - 1)
            return False

        #Check number of balace environmentals
        if(numEnvs != designObs):
            sendError("SERIES " + str(seriesNum) + ": NUMBER OF ENVIRONMENTAL OBSERVATIONS DO NOT MATCH THE DESIGN")
            highlightError(seriesNum, envStartLine, envStartLine + numEnvs - 1)
            return False

    return True

def runSecondaryChecks(seriesTexts, reportNum, sendError, highlightError, debugMode=False):
    #Runs unrequired checks on user input file before running and identifies errors. Does not prevent Runfile.run
    seriesNum = 0

    runMessage = "FILE WAS RUN AND SAVED AS " + str(reportNum) + "-out.txt\n" + "HOWEVER, "
    if(debugMode):
        runMessage = ""

    for seriesText in seriesTexts:
        seriesNum += 1
        lineNum = 0

        for line in seriesText.splitlines():
            lineNum += 1
            line = line.split()

            if(line == []):
                continue

            #Check if environmentals are out of specs
            if(line[0] == "<Environmentals>"):
                temp = float(line[1])
                pressure = float(line[2])
                humidity = float(line[3])

                if(temp < 18 or temp > 23 or humidity < 40 or humidity > 60):
                    sendError(runMessage + "ENVIRONMENTALS IN SERIES " + str(seriesNum) + " LINE " + str(lineNum) + " ARE OUTSIDE SOP 28 LIMITS\n\nENVIRONMENTALS ARE ENTERED IN THE FORM <Environmentals>  T P RH")
                    highlightError(seriesNum, lineNum)
                    return False
            
    return True

def checkResults(results):
    return True