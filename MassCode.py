"""
Author: Erik Alfvin
Run with Python 3.7, numpy 1.17.2
PyMac Version 1
Version Date: 2019-12-15
Results are for experimental purposes only

This program is designed to reduce data from weighing designs using a least squares
best fit. The program returns best fit mass values and within process standard deviations.

The T-test tests the observed value of the check standard against its accepted value.
The F-test tests the within-process standard deviation agianst the accepted standard deviation.
"""

import sys
import numpy as np
import scipy.stats
from statistics import mean, stdev
from math import sqrt, exp

class MatrixSolution:
    """
    The MatrixSolution class holds all calibration data and data reduction results for a given series.
    The vector self.nextRestraint contains the position of the weights to be passed down to the next series.

    The parser needs to push read data into MatrixSolution class instance variables for each series.
    The variable self.seriesNumber holds the series number 0 = first series

    Functions: calculateAirDensity, calculateDoubleSubs, solution, doStatistics
    """
    def __init__(self):
        self.reportNumber = "000000"
        self.restraintID = "0"
        self.uncRestraint = 0
        self.randomError = 0
        self.referenceTemperature = 20

        self.seriesNumber = 0
        self.designMatrix = None
                      
        self.matrixY = None
        self.matrixBHat = None
        self.calculatedMasses = None

        self.positions = 0
        self.observations = 0

        self.restraintPos = None
        self.checkStandardPos = None
        self.linearCombos = []

        #Holders for data for weights in the series:
        self.weightIds = []
        self.weightNominals = None
        self.weightDensities = []
        self.weightCCEs = []
        self.referenceValues = None

        self.nextRestraint = None

        self.restraintMass = 0
        self.checkStandardMass = 0

        self.swMass = 0
        self.swDensity = 0
        self.swCCE = 0

        self.sigmaW = 0
        self.sigmaT = 0

        self.date = [] #[MM, DD, YYYY]
        self.technicianId = 0
        self.balanceId = 0
        self.checkStandardId = 0

        self.directReadings = 0
        self.directReadingsSF = 0
        self.nominalsInPounds = 0

        self.designId = 0

        self.balanceReadings = []
        self.environmentals = []
        self.envCorrections = [] #[T, P, RH]

        self.gravityGradient = 0
        self.heightDifferences = []

        #Statistics Stuff:
        self.df = 0

    def calculateAirDensity(self, t, p, rh):
        """
        Calculates the air density using the CIPM 2007 air density equation
        Picard et al.: https://iopscience.iop.org/article/10.1088/0026-1394/45/2/004
        """

        tKelvin = t + 273.15
        humidity = rh / 100.0
        pressurePa = p * 133.322368421053

        a = 1.2378847*10**-5
        b = -1.9121316*10**-2
        c = 33.93711047
        d = -6.3431645*10**3

        alpha = 1.00062
        beta = 3.14*10**-8
        gamma = 5.6*10**-7

        r = 8.314472
        ma = 28.96546*10**-3
        mv = 18.01528*10**-3

        aZero = 1.58123*10**-6
        aOne = -2.9331*10**-8
        aTwo = 1.1043*10**-10
        bZero = 5.707*10**-6
        bOne = -2.051*10**-8
        cZero = 1.9898*10**-4
        cOne = -2.376*10**-6
        dZ = 1.83*10**-11
        e = -0.765*10**-8

        vaporPressure = exp(a * tKelvin**2 + b * tKelvin + c + d / tKelvin)
        f = alpha + beta * pressurePa + gamma * t**2
        xv = humidity * f * (vaporPressure / pressurePa)

        z = 1 - (pressurePa / tKelvin) * (aZero + aOne*t + aTwo*t**2 + (bZero + bOne*t)*xv + (cZero + cOne*t)*xv**2) + \
            (pressurePa / tKelvin)**2 * (dZ + e*xv**2)

        airDensity = (pressurePa * ma / (z * r * tKelvin)) * (1 - xv * (1 - mv / ma)) * 10**-3
        return airDensity

        #Approximated air density:
        #es = 1.3146*10**9*exp(-5315.56/(t + 273.15))
        #airDensity = (0.46460 / (t + 273.15)) * (p - 0.0037960 * rh * es) * 10**-3

    def calculateSensitivities(self):
        """Calculate the average sensitivity factors for each load in the weighing design if doing double subs. Function is called in solution function if doing double substitutions.
        Returns a dictionary of load:sensitivity pairs.
        """
        averageSensitivities = {}
        nominalSensitivity = []

        firstDesignLine = self.designMatrix[0:1]

        #Initialize positionMassOne vector to position of first line of design:
        positionMassOne = np.zeros(shape=(1, self.positions))
        for position in range(np.shape(firstDesignLine)[1]):
            if firstDesignLine[0, position] == 1:
                positionMassOne[0, position] = 1

        #Initialize nominal variable to the nominal of the first weighing:
        nominal = float(np.matmul(positionMassOne, np.matrix.transpose(self.weightNominals)))
        nominal = round(nominal, 5)

        for i in range(len(self.balanceReadings)):
            obsOne = self.balanceReadings[i][0]
            obsTwo = self.balanceReadings[i][1]
            obsThree = self.balanceReadings[i][2]
            obsFour = self.balanceReadings[i][3]

            swDensityAdjusted = self.swDensity / (1 + self.swCCE * ((self.environmentals[i][0] - self.envCorrections[0]) - self.referenceTemperature))

            airDensity = self.calculateAirDensity(\
                self.environmentals[i][0] - self.envCorrections[0], self.environmentals[i][1] - self.envCorrections[1], self.environmentals[i][2] - self.envCorrections[2])

            swDrift = ((obsFour - obsOne) - (obsThree - obsTwo)) / 2
            sensitivity = (self.swMass / 1000) * (1 - airDensity / swDensityAdjusted) / ((obsThree - obsTwo) - swDrift)

            designLine = self.designMatrix[i:i+1]
            positionMassOne = np.zeros(shape=(1, self.positions))

            #Set position of massOne for the given line of the design to figure out the nominal we're working at:
            for position in range(np.shape(designLine)[1]):
                if designLine[0, position] == 1:
                    positionMassOne[0, position] = 1

            #Check if current nominal is the same as last nominal, if not, add average sensitivity to sensitivities dictionary:
            if round(float(np.matmul(positionMassOne, np.matrix.transpose(self.weightNominals))), 5) != nominal:
                averageSensitivities[nominal] = mean(nominalSensitivity)
                nominalSensitivity = []
                nominal = round(float(np.matmul(positionMassOne, np.matrix.transpose(self.weightNominals))), 5)
                nominalSensitivity.append(sensitivity)
            else:
                nominalSensitivity.append(sensitivity)

        #Add last stored value to sensitivities dictionary:
        averageSensitivities[nominal] = mean(nominalSensitivity)
        print(averageSensitivities)
        return averageSensitivities

    def calculateDoubleSubs(self, estimateMasses, averageSensitivities):
        """
        Calculates resulting "a" values of double subs. This function is called iteratively, passing the latest calculated values (estimateMasses) in to do line-by-line air buoyancy corrections.
        The first pass through uses the nominal values as a first guess at masses. Sensitivity is passed in and the average sensitivity for each load is used. Automated balances use Direct-Readings-SF 
        as the sensitivity factor. 
        """
        
        for i in range(len(self.balanceReadings)):
            airDensity = self.calculateAirDensity(\
                self.environmentals[i][0] - self.envCorrections[0], self.environmentals[i][1] - self.envCorrections[1], self.environmentals[i][2] - self.envCorrections[2])
            
            #Adjust densities for lab temperature for each observation:
            adjustedDensities = []
            for j in range(self.positions):
                adjustedDensities.append(self.weightDensities[j] / (1 + self.weightCCEs[j] * ((self.environmentals[i][0] - self.envCorrections[0]) - self.referenceTemperature)))
            
            #Estimate Mass1Sum, Mass2Sum and effective densities for ABC using estimateMasses:
            designLine = self.designMatrix[i:i+1] #Get sigle line of design matrix as an array
            positionMassOne = np.zeros(shape=(1, self.positions)) #Will be changed below...
            positionMassTwo = np.zeros(shape=(1, self.positions)) #Will be changed below...

            #Modify positionMass arrays in place to store positions of Mass1 and Mass2 for the observation:
            for position in range(np.shape(designLine)[1]):
                if designLine[0, position] == 1:
                    positionMassOne[0, position] = 1

                if designLine[0, position] == -1:
                    positionMassTwo[0, position] = 1

            #Multiply mass position matrix by transpose of estimated masses to get estimated mass of the line:
            estimatedMassOne = float(np.matmul(positionMassOne, np.matrix.transpose(estimateMasses)))
            estimatedMassTwo = float(np.matmul(positionMassTwo, np.matrix.transpose(estimateMasses)))

            #Calculate effective density of MassOne and MassTwo:
            volumeMassOne = 0
            volumeMassTwo = 0
            for position in range(np.shape(positionMassOne)[1]):
                volumeMassOne += positionMassOne[0, position] * estimateMasses[0, position] / adjustedDensities[position]

            for position in range(np.shape(positionMassTwo)[1]):
                volumeMassTwo += positionMassTwo[0, position] * estimateMasses[0, position] / adjustedDensities[position]

            effectiveDensityMassOne = estimatedMassOne / volumeMassOne
            effectiveDensityMassTwo = estimatedMassTwo / volumeMassTwo

            #Calculate the difference between masses measured in lab air:
            if self.directReadings == 0:
                obsOne = self.balanceReadings[i][0]
                obsTwo = self.balanceReadings[i][1]
                obsThree = self.balanceReadings[i][2]
                obsFour = self.balanceReadings[i][3]

                deltaLab = (((obsTwo - obsOne) + (obsThree - obsFour)) / 2) * averageSensitivities[round(float(np.matmul(positionMassOne, np.matrix.transpose(self.weightNominals))), 5)]

            elif self.directReadings == 1:
                deltaLab = -1 * self.balanceReadings[i][0] * averageSensitivities['balance'] / 1000
            
            else:
                sys.exit("PLEASE ENTER A VALID DIRECT-READINGS ARGUMENT. 1 = DIRECT READINGS ENTERED, 0 = DOUBLE SUBSTITUTION OBSERVATIONS ENTERED")
            
            if self.heightDifferences != []:
                deltaLab = deltaLab - (estimatedMassTwo / 9.807) * ((self.heightDifferences[i]/1000) * -1 * self.gravityGradient)

            #Extrapolate what delta would be in vaccum and add to matrixY
            deltaVaccum = deltaLab + airDensity * ((estimatedMassTwo / effectiveDensityMassTwo) - (estimatedMassOne / effectiveDensityMassOne)) #grams
            self.matrixY[i, 0] = -1 * deltaVaccum

    def solution(self, seriesObjects):
        if len(self.environmentals) != len(self.balanceReadings):
            sys.exit("USE THE SAME NUMBER OF LINES FOR DESIGN-MATRIX, BALANCE-READINGS AND ENVIRONMENTALS IN CONFIGURATION FILE FOR SERIES " + str(self.seriesNumber + 1))

        designTranspose = np.matrix.transpose(self.designMatrix)
        transposeXdesign = np.matmul(designTranspose, self.designMatrix)

        #Build matrix A by stacking restraintPos and restraintPos' on transpose x design matrix:
        matrixAtemp = np.hstack((transposeXdesign, np.matrix.transpose(self.restraintPos)))
        matrixA = np.vstack((matrixAtemp, np.append(self.restraintPos, 0)))

        inverseA = np.linalg.inv(matrixA)

        #Check that the inverse of matrixA got calculated correctly within a tolerance:
        if not np.allclose(np.matmul(matrixA, inverseA), np.identity(transposeXdesign.shape[0] + 1)):
            sys.exit("SOMETHING WENT WRONG WITH THE INVERSE MATRIX CALCULATION :(")

        matrixH = inverseA[np.shape(inverseA)[0] - 1:np.shape(inverseA)[0], 0:np.shape(inverseA)[1] - 1]
        matrixQ = inverseA[0:np.shape(inverseA)[0] - 1, 0:np.shape(inverseA)[1] - 1]

        #Calculate value of restraint R*:
        if self.seriesNumber == 0:
            rStar = (np.matmul(self.restraintPos, np.matrix.transpose(self.referenceValues)) / 1000) + np.matmul(self.restraintPos, np.matrix.transpose(self.weightNominals))
        else:
            if np.count_nonzero(seriesObjects[self.seriesNumber - 1].nextRestraint) == 0:
                sys.exit("NO RESTRAINT PASSED TO SERIES", str(self.seriesNumber))

            #Pull restraint from last series:
            rStar = np.matmul(seriesObjects[self.seriesNumber - 1].nextRestraint, np.matrix.transpose(seriesObjects[self.seriesNumber - 1].calculatedMasses))

        #If direct readings entered (a values), set sesitivity to Direct-Readings-SF, put this in averageSensitivities dictionary and pass to calculateDoubleSubs:

        if self.directReadings == 1:
            averageSensitivities = {'balance':self.directReadingsSF}

            #Iterate 4 times through solution, update calculated masses matrix each time and repeat:
            for i in range(4):
                self.calculateDoubleSubs(self.calculatedMasses, averageSensitivities)
                matrixBHat = np.matmul(np.matmul(matrixQ, designTranspose), self.matrixY) + (np.matrix.transpose(matrixH) * rStar)
                self.calculatedMasses = np.matrix.transpose(matrixBHat)

            print(matrixBHat, "\n")
            
        #If doing double subs:
        else:
            averageSensitivities = self.calculateSensitivities()

            for i in range(4):
                self.calculateDoubleSubs(self.calculatedMasses, averageSensitivities)
                matrixBHat = np.matmul(np.matmul(matrixQ, designTranspose), self.matrixY) + (np.matrix.transpose(matrixH) * rStar)
                self.calculatedMasses = np.matrix.transpose(matrixBHat)

            print(matrixBHat, "\n")

        self.matrixBHat = matrixBHat
        self.doStatistics(matrixQ)

    def doStatistics(self, matrixQ):
        #Calculate YHat = XQX'Y = the predicted values from the best fit (in grams):
        self.df = (self.observations - self.positions) + 1
        matrixYHat = np.matmul(np.matmul(np.matmul(self.designMatrix, matrixQ), np.matrix.transpose(self.designMatrix)), self.matrixY)

        #Calculate the within process standard deviation (in mg):
        sumOfResiduals = 0.0 #grams
        for i in range(np.shape(matrixYHat)[0]):
            sumOfResiduals += (self.matrixY[i, 0] - matrixYHat[i, 0])**2
        
        sw = sqrt(sumOfResiduals / self.df) * 1000 #mg

        alpha = 0.05

        fCritical = scipy.stats.f.ppf(1 - alpha, self.df, 1000)
        f = sw**2 / self.sigmaW**2

        if f < fCritical:
            fPass = True
        else:
            fPass = False

        tCritical = scipy.stats.t.ppf(1 - alpha, 1000)
        t = 0

        print("sw =", str(sw), "mg")
        print("df =", str(self.df))
        print("")

        print("F-critical =", str(fCritical))
        print("F-observed =", str(f))
        print("F-test Passed =", str(fPass))
        print("")

        print("T-critical =", str(tCritical))

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
        for line in configFile:
            lines += 1
            splitLine = line.strip().split(maxsplit=15)

            if(splitLine == [] or splitLine[0] == "\n" or splitLine[0][0] == "#"):
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
                seriesObjects[seriesNumber].date.append(int(splitLine[1]))
                seriesObjects[seriesNumber].date.append(int(splitLine[2]))
                seriesObjects[seriesNumber].date.append(int(splitLine[3]))

                seriesObjects[seriesNumber].reportNumber = header["<Report-Number>"]
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
                    seriesObjects[seriesNumber].calculatedMasses = np.zeros(shape=(1, seriesObjects[seriesNumber].positions))
                    seriesObjects[seriesNumber].matrixY = np.zeros(shape=(seriesObjects[seriesNumber].observations, 1))
                    seriesObjects[seriesNumber].referenceValues = np.zeros(shape=(1, seriesObjects[seriesNumber].positions))

                seriesObjects[seriesNumber].weightNominals[0, positionRow] = float(splitLine[2]) * nominalsInPounds
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
            f.write(str(series.reportNumber))
            f.write("\n")

            for i in range(len(series.weightIds)):
                f.write(series.weightIds[i] + "   " + str(series.matrixBHat[i]) + "\n")

        else:
            for i in range(len(series.weightIds)):
                f.write(series.weightIds[i] + "   " + str(series.matrixBHat[i]) + "\n")

    f.close()

def run(inputFile):
    data = parse(inputFile)
    
    for series in data:
        series.solution(data)

    writeOut(data)

if(__name__ == "__main__"):
    inputFile = sys.argv[1]
    run(inputFile)