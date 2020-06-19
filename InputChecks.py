#Module to hold functions that perform checks on user input data and results

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

def runRequiredChecks(seriesTexts, numberOfSeries, sendError, highlightError):
    #Runs required checks on user input file before running and identifies errors the prevent Runfile.run
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

            if(line[0] == "<Balance-Reading>"):
                numObs += 1
                if(obsStartLine == 0): obsStartLine = lineNum

            if(line[0] == "<Environmentals>"):
                numEnvs += 1
                if(envStartLine == 0): envStartLine = lineNum

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

        #Check number of balace readings, envs
        if(numObs != designObs):
            sendError("SERIES " + str(seriesNum) + " NUMBER OF BALANCE OBSERVATIONS DO NOT MATCH THE DESIGN")
            highlightError(seriesNum, obsStartLine, obsStartLine + numObs - 1)
            return False

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