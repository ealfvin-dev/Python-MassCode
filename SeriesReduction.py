# Author: Erik Alfvin
# Run with Python 3.7, numpy 1.17.2, sciPy 1.3.1
# MARS Version 1
# Version Date: 2020-07-24
# Results are for experimental purposes only

# This program is designed to reduce data from weighing designs using a least squares
# best fit. The program returns best fit mass values and within process standard deviations.

# The T-test tests the observed value of the check standard against its accepted value.
# The F-test tests the within-process standard deviation agianst the accepted standard deviation.

from numpy import identity, hstack, vstack, append, linalg, allclose, zeros, float64, copy, matmul, matrix, shape, count_nonzero, multiply, sum
from scipy.stats import f, t
from statistics import mean, stdev
from math import sqrt

from MARSException import MARSException
from CIPM import calculateAirDensity

class MatrixSolution:
    # The MatrixSolution class holds all calibration data and data reduction results for a given series.
    # The vector self.nextRestraint contains the position of the weights to be passed down to the next series.

    # The parser needs to push read data into MatrixSolution class instance variables for each series.
    # The variable self.seriesNumber holds the series number 0 = first series

    # Functions: calculateDoubleSubs, solution, doStatistics

    def __init__(self):
        self.reportNumber = "000000"
        self.notes = []

        self.restraintID = "0"
        self.uncRestraint = 0
        #self.randomError = 0
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
        #self.linearCombos = []
        self.acceptedCheckCorrection = 0
        self.calculatedCheckCorrection = 0

        #Holders for data for weights in the series:
        self.weightIds = []
        self.weightNominals = None
        self.ogNominals = None
        self.weightDensities = []
        self.weightCCEs = []
        self.referenceValues = None

        self.nextRestraint = None

        self.swMass = "NA"
        self.swDensity = "NA"
        self.swCCE = "NA"

        self.sigmaW = 0
        self.sigmaT = 0

        self.date = [] #[MM, DD, YYYY]
        self.technicianId = 0
        self.balanceId = 0
        self.checkStandardId = 0

        self.directReadings = 0
        self.directReadingsSF = 0
        self.nominalsInGrams = 0

        self.designId = 0

        self.balanceReadings = []
        self.environmentals = []
        self.envCorrections = [] #[T, P, RH]
        self.airDensities = []

        self.sensitivities = []
        self.loads = []
        self.aveSensitivities = None

        self.localGravity = 9.8
        self.gravityGradient = 0.0 #1/s2
        self.weightHeights = zeros(shape=0) #m

        #Statistics Stuff:
        self.df = 0
        self.swObs = 0
        self.fCritical = 0
        self.fValue = 0
        self.tCritical = 0
        self.tValue = 0
        self.deltas = [] #mg

    def calculateSensitivities(self):
        #Calculate the average sensitivity factors for each load in the weighing design if doing double subs. Function is called in solution function if doing double substitutions.
        #Returns a dictionary of load:sensitivity pairs.
        
        averageSensitivities = {}
        nominalSensitivity = []

        #Initialize load to nominal of the first weighing:
        load = self.loads[0]

        for i in range(len(self.balanceReadings)):
            obsOne = self.balanceReadings[i][0]
            obsTwo = self.balanceReadings[i][1]
            obsThree = self.balanceReadings[i][2]
            obsFour = self.balanceReadings[i][3]

            swDensityAdjusted = self.swDensity / (1 + self.swCCE * ((float64(self.environmentals[i][0]) - float64(self.envCorrections[0])) - self.referenceTemperature))

            airDensity = calculateAirDensity(\
                self.environmentals[i][0], self.envCorrections[0], self.environmentals[i][1], self.envCorrections[1], self.environmentals[i][2], self.envCorrections[2])

            swDrift = ((obsFour - obsOne) - (obsThree - obsTwo)) / 2

            sensitivity = (self.swMass / 1000) * (1 - airDensity / swDensityAdjusted) / ((obsThree - obsTwo) - swDrift)
            self.sensitivities.append(sensitivity)

            #Check if current load is the same as last. If not, add average sensitivity to sensitivities dictionary:
            if(self.loads[i] != load):
                averageSensitivities[load] = mean(nominalSensitivity)

                nominalSensitivity = []
                load = self.loads[i]

                nominalSensitivity.append(sensitivity)
            else:
                nominalSensitivity.append(sensitivity)

        #Add last stored value to sensitivities dictionary:
        averageSensitivities[load] = mean(nominalSensitivity)

        self.aveSensitivities = averageSensitivities

        return averageSensitivities

    def calculateLoads(self):
        #Builds a list of working loads for each observation line in the design
        for line in self.designMatrix:
            positionMassOne = copy(line)
            for i in range(len(line)):
                if(line[i] == 1):
                    positionMassOne[i] = 1
                else:
                    positionMassOne[i] = 0

            nominal = float64(matmul(positionMassOne, matrix.transpose(self.weightNominals)))
            nominal = round(nominal, 5)

            self.loads.append(nominal)

    def calculateDoubleSubs(self):
        # Calculates resulting "a" values of double subs. This function is called iteratively, passing the latest calculated values (self.calculatedMasses) in to do line-by-line air buoyancy corrections.
        # The first pass through uses the nominal values as a first guess at masses. Sensitivity is passed in and the average sensitivity for each load is used. Automated balances use Direct-Readings-SF 
        # as the sensitivity factor.

        for i in range(len(self.balanceReadings)):
            airDensity = calculateAirDensity(\
                self.environmentals[i][0], self.envCorrections[0], self.environmentals[i][1], self.envCorrections[1], self.environmentals[i][2], self.envCorrections[2])
            
            self.airDensities.append(airDensity)

            #Estimate Mass1Sum, Mass2Sum for ABC using self.calculatedMasses:
            designLine = self.designMatrix[i:i+1] #Get sigle line of design matrix as an array
            positionMassOne = zeros(shape=(1, self.positions)) #Will be changed below...
            positionMassTwo = zeros(shape=(1, self.positions)) #Will be changed below...

            #Modify positionMass arrays in place to store positions of Mass1 and Mass2 for the observation:
            for position in range(shape(designLine)[1]):
                if designLine[0, position] == 1:
                    positionMassOne[0, position] = 1

                if designLine[0, position] == -1:
                    positionMassTwo[0, position] = 1

            #Multiply mass position matrix by transpose of estimated masses to get estimated mass of the line:
            estimatedMassOne = float64(matmul(positionMassOne, matrix.transpose(self.calculatedMasses)))
            estimatedMassTwo = float64(matmul(positionMassTwo, matrix.transpose(self.calculatedMasses)))

            #Calculate volume of MassOne and MassTwo:
            volumeMassOne = 0
            volumeMassTwo = 0
            for position in range(shape(positionMassOne)[1]):
                volumeMassOne += (positionMassOne[0, position] * self.calculatedMasses[0, position] / self.weightDensities[position]) *\
                    (1 + self.weightCCEs[position] * ((float64(self.environmentals[i][0]) - float64(self.envCorrections[0])) - self.referenceTemperature))

            for position in range(shape(positionMassTwo)[1]):
                volumeMassTwo += (positionMassTwo[0, position] * self.calculatedMasses[0, position] / self.weightDensities[position]) *\
                    (1 + self.weightCCEs[position] * ((float64(self.environmentals[i][0]) - float64(self.envCorrections[0])) - self.referenceTemperature))

            #Calculate the difference between masses measured in lab air:
            if self.directReadings == 0:
                obsOne = self.balanceReadings[i][0]
                obsTwo = self.balanceReadings[i][1]
                obsThree = self.balanceReadings[i][2]
                obsFour = self.balanceReadings[i][3]

                deltaLab = (((obsTwo - obsOne) + (obsThree - obsFour)) / 2) * \
                    self.aveSensitivities[round(float64(matmul(positionMassOne, matrix.transpose(self.weightNominals))), 5)]

            elif self.directReadings == 1:
                deltaLab = self.balanceReadings[i][0] * self.aveSensitivities['balance'] / 1000
            
            else:
                raise MARSException("SERIES " + str(self.seriesNumber + 1) + ": PLEASE ENTER A VALID DIRECT-READINGS ARGUMENT.\n1 = DIRECT READINGS ENTERED, 0 = DOUBLE SUBSTITUTION OBSERVATIONS ENTERED")
            
            #Gravity corrections
            if(self.weightHeights.size != 0):
                if(count_nonzero(self.weightHeights) == self.positions):
                    #Calculate COMs of massOne and massTwo
                    mass1Array = multiply(positionMassOne, self.calculatedMasses)
                    mass2Array = multiply(positionMassTwo, self.calculatedMasses)

                    COM1 = matmul(mass1Array, matrix.transpose(self.weightHeights))[0][0] / sum(mass1Array)
                    COM2 = matmul(mass2Array, matrix.transpose(self.weightHeights))[0][0] / sum(mass2Array)

                    #Calculate reference height (COM of restraint):
                    massRArray = multiply(self.restraintPos, self.calculatedMasses)
                    COMref = matmul(massRArray, matrix.transpose(self.weightHeights))[0][0] / sum(massRArray)

                    #Perform gravitational correction back to reference height
                    deltaLab = deltaLab + (self.gravityGradient / self.localGravity) * \
                        (estimatedMassTwo * (COM2 - COMref) - estimatedMassOne * (COM1 - COMref))

                else:
                    raise MARSException("SERIES " + str(self.seriesNumber + 1) + ": UNEQUAL NUMBER OF WEIGHT HEIGHTS AND POSITIONS\nHEIGHTS MUST BE > 0")

            #Extrapolate what delta would be in vaccum and add to matrixY
            deltaVaccum = deltaLab + airDensity * (volumeMassTwo - volumeMassOne) #grams
            self.matrixY[i, 0] = -1 * deltaVaccum

    def solution(self, seriesObjects):
        if(len(self.environmentals) != self.observations or len(self.balanceReadings) != self.observations):
            raise MARSException("SERIES " + str(self.seriesNumber + 1) + ": UNEQUAL NUMBER OF OBSERVATIONS, BALANCE OBSERVATIONS AND ENVIRONMENTALS")

        designTranspose = matrix.transpose(self.designMatrix)
        transposeXdesign = matmul(designTranspose, self.designMatrix)

        #Build matrix A by stacking restraintPos and restraintPos' on transpose x design matrix:
        matrixAtemp = hstack((transposeXdesign, matrix.transpose(self.restraintPos)))
        matrixA = vstack((matrixAtemp, append(self.restraintPos, 0)))
        
        try:
            inverseA = linalg.inv(matrixA)
        except:
            raise MARSException("SERIES " + str(self.seriesNumber + 1) + " DESIGN MATRIX HAS NO INVERSE")

        #Check that the inverse of matrixA got calculated correctly within a tolerance:
        if not allclose(matmul(matrixA, inverseA), identity(transposeXdesign.shape[0] + 1)):
            raise MARSException("SERIES " + str(self.seriesNumber + 1) + ": SOMETHING WENT WRONG WITH THE INVERSE MATRIX CALCULATION")

        matrixH = inverseA[shape(inverseA)[0] - 1:shape(inverseA)[0], 0:shape(inverseA)[1] - 1]
        matrixQ = inverseA[0:shape(inverseA)[0] - 1, 0:shape(inverseA)[1] - 1]

        #Calculate value of restraint R*:
        if self.seriesNumber == 0:
            rStar = (matmul(self.restraintPos, matrix.transpose(self.referenceValues)) / 1000) + matmul(self.restraintPos, matrix.transpose(self.weightNominals))
        else:
            if count_nonzero(seriesObjects[self.seriesNumber - 1].nextRestraint) == 0:
                raise MARSException("NO RESTRAINT PASSED TO SERIES " + str(self.seriesNumber + 1))

            #Pull restraint from last series:
            rStar = matmul(seriesObjects[self.seriesNumber - 1].nextRestraint, matrix.transpose(seriesObjects[self.seriesNumber - 1].calculatedMasses))

        self.calculateLoads()

        #If direct readings entered (a values), set sesitivity to Direct-Readings-SF, put this in self.aveSensitivities dictionary:
        if self.directReadings == 1:
            for i in range(self.observations):
                self.sensitivities.append(self.directReadingsSF)

            self.aveSensitivities = {'balance':self.directReadingsSF}
        
        #If doing double subs:
        else:
            self.calculateSensitivities()

        #Iterate 5 times through solution, update calculated masses matrix each time and repeat:
        for i in range(5):
            self.airDensities = []
            self.calculateDoubleSubs()

            matrixBHat = matmul(matmul(matrixQ, designTranspose), self.matrixY) + (matrix.transpose(matrixH) * rStar)
            self.calculatedMasses = matrix.transpose(matrixBHat)

        self.matrixBHat = matrixBHat

        alpha = 0.05
        self.fTest(alpha, matrixQ)
        self.tTest(alpha)

    def fTest(self, alpha, matrixQ):
        #Calculate YHat = XQX'Y = the predicted values from the best fit (in grams):
        self.df = (self.observations - self.positions) + 1
        matrixYHat = matmul(matmul(matmul(self.designMatrix, matrixQ), matrix.transpose(self.designMatrix)), self.matrixY)

        #Calculate the within process standard deviation (in mg):
        sumOfResiduals = 0 #grams^2
        for i in range(shape(matrixYHat)[0]):
            sumOfResiduals += (self.matrixY[i, 0] - matrixYHat[i, 0])**2
            self.deltas.append((self.matrixY[i, 0] - matrixYHat[i, 0]) * 1000)
        
        sw = sqrt(sumOfResiduals / self.df) * 1000 #mg

        fCritical = f.ppf(1 - alpha, self.df, 1000)
        fValue = sw**2 / self.sigmaW**2

        self.swObs = sw
        self.fCritical = fCritical
        self.fValue = fValue

        if fValue < fCritical:
            fPass = True
        else:
            fPass = False

    def tTest(self, alpha):
        self.acceptedCheckCorrection = matmul(self.checkStandardPos, matrix.transpose(self.referenceValues))[0][0]
        self.calculatedCheckCorrection = (matmul(self.checkStandardPos, matrix.transpose(self.calculatedMasses))[0][0] \
                                            - matmul(self.checkStandardPos, matrix.transpose(self.weightNominals))[0][0]) * 1000

        typeAUnc = self.sigmaT #May be changed
        self.tCritical = t.ppf(1 - alpha, 1000)
        self.tValue = (self.calculatedCheckCorrection - self.acceptedCheckCorrection) / typeAUnc