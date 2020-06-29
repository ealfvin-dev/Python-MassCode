#Module to hold functions that perform checks on user input data and results

def checkStructure(seriesTexts, sendError, highlightError, goToSeries):
    #Check structure of input file in UI (split into series)
    seriesNum = 0
    numSeries = 0
    lineNum = 0

    for seriesText in seriesTexts:
        seriesNum += 1
        for line in seriesText.splitlines():
            lineNum += 1
            line = line.strip().split()

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

def checkTags(seriesArray, seriesNum, orderOfTags, highlightError, sendError):
    #Checks if currently written tags exist in the known tags dictionary
    seriesNumber = 0

    for seriesText in seriesArray:
        seriesNumber += 1
        lineNum = 0

        for line in seriesText.splitlines():
            lineNum += 1

            if(line.split() == []):
                pass
            elif(line.split()[0].strip() == ""):
                pass
            else:
                try:
                    orderOfTags[line.split()[0].strip()]
                except KeyError:
                    if(seriesNum):
                        snText = str(seriesNum)
                    else:
                        snText = str(seriesNumber)

                    errorMessage = "UNKNOWN TAG IN SERIES " + snText + ", LINE " + str(lineNum) + ": " + line.split()[0].strip()
                    highlightError(int(snText), lineNum)
                    sendError(errorMessage)
                    return False
                    
    return True

def checkIfAllTags(seriesTexts, requiredTags, sendError, goToSeries):
    #Checks if all tags in known tags dictionary exist in each seriesTexts
    seriesNum = 1
    for inputText in seriesTexts:
        for tag in requiredTags:
            if((tag == "<Report-Number>" or tag == "<Restraint-ID>" or tag == "<Unc-Restraint>" or tag == "<Random-Error>") and seriesNum != 1):
                continue

            exists = 0
            for line in inputText.splitlines():
                if(line.split() != []):
                    if(line.split()[0] == tag):
                        exists = 1
                        break

            if(exists == 0):
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
            line = line.strip().split()

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
            line = line.strip().split()

            if(len(line) == 0):
                continue
            if(line[0][0] == "#" or line[0] == "<Report-Number>" or line[0] == "<Restraint-ID>" or line[0] == "<Unc-Restraint>" or line[0] == "<Random-Error>"):
                continue

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
                    sendError("SERIES " + str(seriesNum) + " LINE " + str(lineNum) + "\nENVIRONMENTALS MUST BE ENTERED IN THE FORM <Environmentals>  T P RH")
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
            line = line.strip().split()
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