#Module to hold functions that perform checks on user input data and results

#determineIfDirectReadings (helper)
#checkReportNumber
#checkStructure
#checkTags
#checkIfAllTags
#checkForRepeats
#runRequiredChecks
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
    numSeries = 0
    lineNum = 0

    for seriesText in seriesTexts:
        seriesNum += 1
        for line in seriesText.splitlines():
            lineNum += 1
            line = line.split()

            if(len(line) == 0):
                continue
            if(line[0][0] == "#" or line[0] == "<Report-Number>" or line[0] == "<Restraint-ID>" or line[0] == "<Unc-Restraint>" or line[0] == "<Random-Error>"):
                continue

            if(line[0] == "@SERIES"):
                numSeries += 1

                #Check if more than 1 series is entered in each text block
                if(numSeries > 1):
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + ": ENTER ONE @SERIES BLOCK PER SERIES\nUSING OPEN FILE FROM THE MENU WILL AUTOMATICALLY SPLIT INPUT TEXT INTO INDIVIDUAL SERIES")
                    highlightError(seriesNum, lineNum)
                    return False

                continue

            #Check that @SERIES marks the start of the series
            if(numSeries == 0):
                sendError("SERIES " + str(seriesNum) + ": THERE MUST BE AN @SERIES ANNOTATION BEFORE <Date> TO MARK THE BEGINNING OF EACH SERIES")
                goToSeries(seriesNum, True)
                return False

        numSeries = 0
        lineNum = 0

    return True

def checkTags(seriesTexts, seriesNum, highlightError, sendError):
    #Checks if currently written tags exist in the known tags dictionary
    acceptedTags = {"@SERIES": False, \
                    "<Report-Number>": False, \
                    "<Restraint-ID>": False, \
                    "<Unc-Restraint>": False, \
                    "<Random-Error>": False, \
                    "<Date>": False, \
                    "<Technician-ID>": False, \
                    "<Check-Standard-ID>": False, \
                    "<Balance-ID>": False, \
                    "<Direct-Readings>": False, \
                    "<Direct-Reading-SF>": False, \
                    "<Design-ID>": False, \
                    "<Design>": False, \
                    "<Pounds>": False, \
                    "<Position>": False, \
                    "<Restraint>": False, \
                    "<Check-Standard>": False, \
                    "<Linear-Combo>": False, \
                    "<Pass-Down>": False, \
                    "<Sigma-t>": False, \
                    "<Sigma-w>": False, \
                    "<sw-Mass>": False, \
                    "<sw-Density>": False, \
                    "<sw-CCE>": False, \
                    "<Balance-Reading>": False, \
                    "<Environmentals>": False, \
                    "<Env-Corrections>": False}

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
            else:
                try:
                    acceptedTags[line.split()[0]]
                except KeyError:
                    if(seriesNum):
                        snText = str(seriesNum)
                    else:
                        snText = str(seriesNumber)

                    errorMessage = "UNKNOWN TAG IN SERIES " + snText + ", LINE " + str(lineNum) + ": " + line.split()[0]
                    highlightError(int(snText), lineNum)
                    sendError(errorMessage)
                    return False
                    
    return True

def checkIfAllTags(seriesTexts, sendError, goToSeries):
    #Checks if all tags in known tags dictionary exist in each seriesTexts
    seriesNum = 1
    for inputText in seriesTexts:
        if(determineIfDirectReadings(inputText)):
            tagSet = {"<Report-Number>": False, \
                        "<Restraint-ID>": False, \
                        "<Unc-Restraint>": False, \
                        "<Random-Error>": False, \
                        "<Date>": False, \
                        "<Technician-ID>": False, \
                        "<Check-Standard-ID>": False, \
                        "<Balance-ID>": False, \
                        "<Direct-Readings>": False, \
                        "<Direct-Reading-SF>": False, \
                        "<Design-ID>": False, \
                        "<Design>": False, \
                        "<Pounds>": False, \
                        "<Position>": False, \
                        "<Restraint>": False, \
                        "<Check-Standard>": False, \
                        "<Linear-Combo>": False, \
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
                        "<Random-Error>": False, \
                        "<Date>": False, \
                        "<Technician-ID>": False, \
                        "<Check-Standard-ID>": False, \
                        "<Balance-ID>": False, \
                        "<Direct-Readings>": False, \
                        "<Direct-Reading-SF>": False, \
                        "<Design-ID>": False, \
                        "<Design>": False, \
                        "<Pounds>": False, \
                        "<Position>": False, \
                        "<Restraint>": False, \
                        "<Check-Standard>": False, \
                        "<Linear-Combo>": False, \
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
        for line in inputText.splitlines():
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

            if((tag == "<Report-Number>" or tag == "<Restraint-ID>" or tag == "<Unc-Restraint>" or tag == "<Random-Error>") and seriesNum != 1):
                continue

            sendError(tag + " DOES NOT EXIST IN SERIES " + str(seriesNum))
            goToSeries(seriesNum, True)
            return False
                
        seriesNum += 1
    return True

def checkForRepeats(seriesTexts, sendError, highlightError):
    #Check for repeated tags
    seriesNum = 0
    lineNum = 0

    singleTags = {"<Report-Number>": 0,\
        "<Restraint-ID>": 0,\
        "<Unc-Restraint>": 0,\
        "<Random-Error>": 0,\
        "<Date>": 0,\
        "<Technician-ID>": 0,\
        "<Check-Standard-ID>": 0,\
        "<Balance-ID>": 0,\
        "<Direct-Readings>": 0,\
        "<Direct-Reading-SF>": 0,\
        "<Design-ID>": 0,\
        "<Pounds>": 0,\
        "<Restraint>": 0,\
        "<Check-Standard>": 0,\
        "<Linear-Combo>": 0,\
        "<Pass-Down>": 0,\
        "<Sigma-t>": 0,\
        "<Sigma-w>": 0,\
        "<sw-Mass>": 0,\
        "<sw-Density>": 0,\
        "<sw-CCE>": 0}

    for seriesText in seriesTexts:
        seriesNum += 1
        lineNum = 0
        for line in seriesText.splitlines():
            lineNum += 1
            line = line.split()

            if(len(line) == 0):
                continue

            try:
                singleTags[line[0]] += 1
            except KeyError:
                continue

            if(singleTags[line[0]] > 1):
                sendError("SERIES " + str(seriesNum) + ": MULTIPLE " + line[0] + " TAGS FOUND\nMARK THE START OF EACH SERIES WITH THE @SERIES ANNOTATION BEOFRE <Date>")
                highlightError(seriesNum, lineNum)
                return False

        lineNum = 0
        for key, value in singleTags.items():
            singleTags[key] = 0 

    return True

def runRequiredChecks(seriesTexts, numberOfSeries, sendError, highlightError, goToSeries):
    #Runs required checks on user input file before running and identifies errors that prevent Runfile.run
    seriesNum = 0
    lineNum = 0

    designObs = 0
    numObs = 0
    numEnvs = 0

    obsStartLine = 0
    envStartLine = 0

    for seriesText in seriesTexts:
        seriesNum += 1
        for line in seriesText.splitlines():
            lineNum += 1
            line = line.split()

            if(len(line) == 0):
                continue

            #Check if report number is entered without spaces
            if(line[0] == "<Report-Number>"):
                try:
                    error = line[2]
                    sendError("SERIES " + str(seriesNum) + ", LINE " + str(lineNum) + ": ENTER A REPORT NUMBER WITHOUT SPACES")
                    highlightError(seriesNum, lineNum)
                    return False
                except IndexError:
                    continue

            if(line[0][0] == "#" or line[0] == "<Restraint-ID>" or line[0] == "<Unc-Restraint>" or line[0] == "<Random-Error>"):
                continue

            #Check format of date
            if(line[0] == "<Date>"):
                if(len(line) != 4):
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + "\nDATE IS ENTERED IN THE FORM <Date>  MM DD YYYY")
                    highlightError(seriesNum, lineNum)
                    return False

            #Check direct readings value
            if(line[0] == "<Direct-Readings>"):
                try:
                    dr = line[1]
                    if(dr == "1"):
                        continue
                    elif(dr == "0"):
                        continue
                    else:
                        sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + "\nUNKNOWN DIRECT READING VALUE. (1=DIRECT READINGS, 0=DOUBLE SUBSTITUTIONS)")
                        highlightError(seriesNum, lineNum)
                        return False
                except IndexError:
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + "\nDIRECT READING VALUE NEEDED. (1=DIRECT READINGS, 0=DOUBLE SUBSTITUTIONS)")
                    highlightError(seriesNum, lineNum)
                    return False

            #Make sure all connected series have results passed down
            if(line[0] == "<Pass-Down>" and seriesNum < numberOfSeries):
                total = 0
                for position in line[1:]:
                    total += int(position)
                
                if(total == 0):
                    sendError("NO RESTRAINT PASSED TO SERIES " + str(seriesNum + 1))
                    highlightError(seriesNum, lineNum)
                    return False

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

            #Check if environmentals provided correctly
            if(line[0] == "<Environmentals>"):
                try:
                    temp = float(line[1])
                    pressure = float(line[2])
                    humidity = float(line[3])
                except:
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + "\nENVIRONMENTALS ARE ENTERED IN THE FORM <Environmentals>  T P RH")
                    highlightError(seriesNum, lineNum)
                    return False
                continue

            #Check that pass down nominal matches next restraint

        #Check number of balace readings
        if(numObs != designObs):
            sendError("SERIES " + str(seriesNum) + " NUMBER OF BALANCE OBSERVATIONS DO NOT MATCH THE DESIGN")
            highlightError(seriesNum, obsStartLine, obsStartLine + numObs - 1)
            return False

        #Check number of balace environmentals
        if(numEnvs != designObs):
            sendError("SERIES " + str(seriesNum) + " NUMBER OF ENVIRONMENTAL OBSERVATIONS DO NOT MATCH THE DESIGN")
            highlightError(seriesNum, envStartLine, envStartLine + numEnvs - 1)
            return False

        lineNum = 0
        designObs = 0
        numObs = 0
        numEnvs = 0
        obsStartLine = 0
        envStartLine = 0

    return True

def runSecondaryChecks(seriesTexts, reportNum, sendError, highlightError):
    #Runs unrequired checks on user input file before running and identifies errors. Does not prevent Runfile.run
    seriesNum = 0
    lineNum = 1

    for seriesText in seriesTexts:
        seriesNum += 1
        for line in seriesText.splitlines():
            line = line.split()
            if(len(line) == 0):
                lineNum += 1
                continue

            #Check if environmentals are out of specs
            if(line[0] == "<Environmentals>"):
                temp = float(line[1])
                pressure = float(line[2])
                humidity = float(line[3])

                if(temp < 18 or temp > 23 or humidity < 40 or humidity > 60):
                    sendError("FILE WAS RUN AND SAVED AS " + str(reportNum) + "-out.txt\n" + "HOWEVER, ENVIRONMENTALS IN SERIES " + str(seriesNum) + " LINE " + str(lineNum) + " ARE OUTSIDE SOP 28 LIMITS\n\nENVIRONMENTALS ARE ENTERED IN THE FORM <Environmentals>  T P RH")
                    highlightError(seriesNum, lineNum)
                    return False
            
            lineNum += 1
        lineNum = 1
    return True

def checkResults(results):
    seriesNum = 0
    for series in results:
        seriesNum += 1