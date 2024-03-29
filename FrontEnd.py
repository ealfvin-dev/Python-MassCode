import kivy

from kivy.graphics import Color, Rectangle, Line
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.metrics import dp

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window, WindowBase
from kivy.clock import Clock

from kivy.config import Config

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.filechooser import FileSystemLocal
from kivy.uix.checkbox import CheckBox

from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image

import RunFile
import TestSuite
import InputChecks
import API
from MARSException import MARSException
from Configs import Configs

from ParsePlotData import *
from MakePlots import *

from os import path, remove, getcwd
from threading import Thread

from time import sleep

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__()
        
        self.fileName = ""
        self.configFilePath = ""
        self.outFilePath = ""
        self.notesFilePath = ""

        self.numberOfSeries = 1
        self.currentSeries = 1
        self.maxSeries = 20

        self.reportNum = ""
        self.seriesTexts = ["@SERIES\n\n"]
        self.outputText = ""

        with self.canvas.before:
            Color(rgba=Configs.backgroundColor)
            self.backgroundRect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)
        self.saved = False

        self.orderOfTags = {"#": 0, \
            "<Report-Number>": 1, \
            "<Restraint-ID>": 2, \
            "<Unc-Restraint>": 3, \
            #"<Random-Error>": 4, \
            "@SERIES": 5, \
            "<Date>": 6, \
            "<Technician-ID>": 7, \
            "<Balance-ID>": 8, \
            "<Direct-Readings>": 9, \
            "<Direct-Reading-SF>": 10, \
            "<Gravity-Grad>": 11, \
            "<Gravity-Local>": 12, \
            "<Height>": 13, \
            "<Check-ID>": 14, \
            "<Grams>": 15, \
            "<Position>": 16, \
            "<Design-ID>": 17, \
            "<Design>": 18, \
            "<Restraint>": 19, \
            "<Check-Standard>": 20, \
            "<Pass-Down>": 21, \
            "<Sigma-w>": 22, \
            "<Sigma-b>": 23, \
            "<sw-Mass>": 24, \
            "<sw-Density>": 25, \
            "<sw-CCE>": 26, \
            "<Environmentals>": 27, \
            "<Env-Corrections>": 28, \
            "<Balance-Reading>": 29}

    def _update_rect(self, instance, value):
        self.backgroundRect.pos = instance.pos
        self.backgroundRect.size = instance.size

    def writeText(self, text, orderNum):
        textInput = self.ids.userText
        rowStart = 0
        rowEnd = 0
        textInput.cursor = (0, 0)

        #Move cursor to the appropriate position
        for line in textInput.text.splitlines():
            rowStart += 1
            if(line.strip() == "" or line.strip()[0] == "#" or orderNum >= self.orderOfTags[line.strip().split()[0]]):
                textInput.cursor = (len(line), rowStart - 1)
            else:
                break

        #Insert text
        if(textInput.cursor == (0, 0)):
            textInput.insert_text("\n")
            textInput.cursor = (0, 0)
        else:
            textInput.insert_text("\n")

        rowStart = textInput.cursor[1] + 1

        for line in text.splitlines():
            if(line == "" or line == "\n"):
                textInput.insert_text("\n")
            else:
                if(orderNum != self.orderOfTags["#"] and orderNum != self.orderOfTags["@SERIES"]):
                    newLine = " " * (19 - len(self.getTag(orderNum)))
                else:
                    newLine = ""

                newLine += self.getTag(orderNum) + "  " + line
                textInput.insert_text(newLine)
                rowEnd = textInput.cursor[1] + 1

                if(len(text.splitlines()) > 1):
                    textInput.insert_text("\n")

                if(orderNum == 1 or orderNum == 3 or orderNum == 10 or orderNum == 15 or orderNum == 21 or orderNum == 23 or orderNum == 26 or orderNum == 28):
                    textInput.insert_text("\n")

        self.renderButtons(self.ids.userText.text)

        return rowStart, rowEnd

    def removeLines(self, tags):
        filteredText = ""
        previousLine = ""

        for line in self.ids.userText.text.splitlines():
            if(line.split() == []):
                if(previousLine != ""):
                    filteredText += "\n"
                    previousLine = ""
            elif(line.split()[0] not in tags):
                filteredText += line + "\n"
                previousLine = line

        self.ids.userText.text = filteredText

    def getTag(self, orderNum):
        for tag, order in self.orderOfTags.items():
            if(order == orderNum):
                return tag

    def highlight(self, startLine, endLine):
        startPosition = 0
        endPosition = 0
        lineNum = 1
        userTextArray = self.ids.userText.text.splitlines()

        while lineNum <= endLine:
            if(lineNum < startLine):
                startPosition += len(userTextArray[lineNum - 1]) + 1
                endPosition += len(userTextArray[lineNum - 1]) + 1
            else:
                endPosition += len(userTextArray[lineNum - 1]) + 1

            lineNum += 1

        endPosition -= 1
        self.ids.userText.selection_color = Configs.highlightNewTextColor
        self.ids.userText.select_text(startPosition, endPosition)

    def highlightError(self, series, startLine, endLine=None):
        self.goToSeries(series, True)

        self.ids.userText.focus = True
        self.ids.userText.cursor = (0, 0)
        self.ids.userText.focus = False

        if(endLine == None):
            endLine = startLine

        startPosition = 0
        endPosition = 0
        lineNum = 1
        userTextArray = self.ids.userText.text.splitlines()

        while lineNum <= endLine:
            if(lineNum < startLine):
                startPosition += len(userTextArray[lineNum - 1]) + 1
                endPosition += len(userTextArray[lineNum - 1]) + 1
            else:
                endPosition += len(userTextArray[lineNum - 1]) + 1

            lineNum += 1

        endPosition -= 1

        self.ids.userText.cursor = (0, endLine - 1)
        self.ids.userText.selection_color = Configs.highlightErrorColor
        self.ids.userText.select_text(startPosition, endPosition)

    def textAdded(self, cursor_row):
        if(self.saved):
            self.saved = False
            self.ids.runButton.colorGrey()
            self.ids.saveButton.colorBlue()

            if(self.ids.errors.text != "" and self.ids.errors.text.split()[1] == "SAVED"):
                self.clearErrors()

    def noteTextAdded(self):
        if(self.saved):
            self.saved = False
            self.ids.runButton.colorGrey()
            self.ids.saveButton.colorBlue()

            if(self.ids.errors.text != "" and self.ids.errors.text.split()[1] == "SAVED"):
                self.clearErrors()

    def displaySeriesNominal(self, inputText, seriesButton):
        #Call this from save(), gotoseries(), addpositionscallback()
        seriesNominal = 0
        units = ""
        foundNominal = False
        foundUnits = False

        for line in inputText.splitlines():
            if(line.split() == []):
                continue

            if(line.split()[0] == "<Position>" and foundNominal == False):
                try:
                    seriesNominal = line.split()[2]
                    foundNominal = True
                except IndexError:
                    pass
                
            elif(line.split()[0] == "<Grams>"):
                try:
                    unitsNum = line.split()[1]
                    if(unitsNum == "1"):
                        units = "g"
                        foundUnits = True
                    if(unitsNum == "0"):
                        units = "lb"
                        foundUnits = True
                except IndexError:
                    pass

        if(foundNominal and foundUnits):
            nominal = str(seriesNominal) + units
            seriesButton.text = "[color=#000000]Series " + str(seriesButton.seriesNum) + " - " + nominal + "[/color]"
        else:
            seriesButton.text = "[color=#000000]Series " + str(seriesButton.seriesNum) + "[/color]"

    def renderButtons(self, seriesText):
        #Make dictionary of tags, linked to True/False if they exist in userText.text
        tags = {"#": False, \
            "<Report-Number>": False, \
            "<Restraint-ID>": False, \
            "<Unc-Restraint>": False, \
            #"<Random-Error>": False, \
            "@SERIES": False, \
            "<Date>": False, \
            "<Technician-ID>": False, \
            "<Balance-ID>": False, \
            "<Direct-Readings>": False, \
            "<Direct-Reading-SF>": False, \
            "<Gravity-Grad>": False, \
            "<Gravity-Local>": False, \
            "<Height>": False, \
            "<Check-ID>": False, \
            "<Grams>": False, \
            "<Position>": False, \
            "<Design-ID>": False, \
            "<Design>": False, \
            "<Restraint>": False, \
            "<Check-Standard>": False, \
            "<Pass-Down>": False, \
            "<Sigma-w>": False, \
            "<Sigma-b>": False, \
            "<sw-Mass>": False, \
            "<sw-Density>": False, \
            "<sw-CCE>": False, \
            "<Environmentals>": False, \
            "<Env-Corrections>": False, \
            "<Balance-Reading>": False}

        for line in seriesText.splitlines():
            if(line.split() == []):
                continue

            try:
                tags[line.split()[0]]
                tags[line.split()[0]] = True
            except KeyError:
                pass

        directReadings = InputChecks.determineIfDirectReadings(seriesText)

        #Lab Info Button
        if(self.currentSeries == 1 and tags["<Report-Number>"] == False):
            self.ids.labInfoButton.colorBlue()
        else:
            self.ids.labInfoButton.colorGrey()

        #Restraint Button
        if(self.currentSeries == 1 and (tags["<Restraint-ID>"] == False or tags["<Unc-Restraint>"] == False)):
            self.ids.restraintButton.colorBlue()
        else:
            self.ids.restraintButton.colorGrey()

        #Date Button
        if(tags["<Date>"] and tags["<Technician-ID>"] and tags["<Balance-ID>"] and tags["<Direct-Readings>"] and \
            (tags["<Direct-Reading-SF>"] or directReadings == False)):
            self.ids.dateButton.colorGrey()
        else:
            self.ids.dateButton.colorBlue()

        #Weights Button
        if(tags["<Position>"] and tags["<Grams>"] and tags["<Check-ID>"]):
            self.ids.weightsButton.colorGrey()
        else:
            self.ids.weightsButton.colorBlue()

        #Gravity Button
        if(tags["<Height>"] and tags["<Gravity-Grad>"] and tags["<Gravity-Local>"]):
            self.ids.gravityButton.colorGrey()
        else:
            self.ids.gravityButton.colorBlue()

        #Design Button
        if(tags["<Design>"] and tags["<Design-ID>"]):
            self.ids.designButton.colorGrey()
        else:
            self.ids.designButton.colorBlue()

        #Positions Button
        if(tags["<Restraint>"] and tags["<Check-Standard>"] and tags["<Pass-Down>"]):
            self.ids.positionVectorsButton.colorGrey()
        else:
            self.ids.positionVectorsButton.colorBlue()

        #Statistics Buttons
        if(tags["<Sigma-b>"] and tags["<Sigma-w>"]):
            self.ids.statisticsButton.colorGrey()
        else:
            self.ids.statisticsButton.colorBlue()

        #Sensitivity Weight Button
        if((tags["<sw-Mass>"] and tags["<sw-Density>"] and tags["<sw-CCE>"]) or directReadings):
            self.ids.swButton.colorGrey()
        else:
            self.ids.swButton.colorBlue()

        #Measurements Button
        if(tags["<Balance-Reading>"] and tags["<Environmentals>"] and tags["<Env-Corrections>"]):
            self.ids.measurementsButton.colorGrey()
        else:
            self.ids.measurementsButton.colorBlue()

    def greyOutButtons(self):
        self.ids.labInfoButton.colorGrey()
        self.ids.restraintButton.colorGrey()
        self.ids.dateButton.colorGrey()
        self.ids.gravityButton.colorGrey()
        self.ids.statisticsButton.colorGrey()
        self.ids.designButton.colorGrey()
        self.ids.weightsButton.colorGrey()
        self.ids.positionVectorsButton.colorGrey()
        self.ids.swButton.colorGrey()
        self.ids.measurementsButton.colorGrey()

    def getGravityButtonColor(self):
        return Configs.gravityButtonColor

    def addSeries(self):
        if(self.numberOfSeries == self.maxSeries):
            return

        self.numberOfSeries += 1

        newSeriesId = "series" + str(self.numberOfSeries)
        self.ids[newSeriesId].text = "[color=#FFFFFF]Series " + str(self.numberOfSeries) +"[/color]"
        self.ids[newSeriesId].exists = True

        self.seriesTexts.append("@SERIES\n\n")

        self.ids.seriesSelectionMenu.height = dp(55) * self.numberOfSeries

        if(self.saved):
            self.saved = False
            self.ids.runButton.colorGrey()
            self.ids.saveButton.colorBlue()

            if(self.ids.errors.text != "" and self.ids.errors.text.split()[1] == "SAVED"):
                self.clearErrors()

    def goToSeries(self, seriesNum, exists):
        if(exists):
            #Check if input was saved
            wasSaved = self.saved

            if(self.currentSeries != None):
                #Write current usertext into seriesTexts
                self.seriesTexts[self.currentSeries - 1] = self.ids.userText.text

                #Render current series button nominal
                seriesButtonId = "series" + str(self.currentSeries)
                self.displaySeriesNominal(self.seriesTexts[self.currentSeries - 1], self.ids[seriesButtonId])

            #Pull new seriesText into userText
            self.ids.userText.text = self.seriesTexts[seriesNum - 1]

            if(wasSaved):
                self.ids.runButton.colorBlue()
                self.ids.saveButton.colorGrey()
                self.saved = True

            self.ids.userText.readonly = False
            self.ids.userText.cursor = (0, 0)
            self.ids.userText.select_text(0, 0)

            self.currentSeries = seriesNum

            #Render tabs:
            for sn in range(1, self.numberOfSeries + 1):
                seriesID = "series" + str(sn)
                seriesButton = self.ids[seriesID]

                if(seriesButton.exists):
                    seriesButton.background_color = Configs.menuColor
                    seriesButton.text = "[color=#FFFFFF]" + seriesButton.text[15:]

            self.ids.outputFileTab.background_color = Configs.menuColor

            if(self.ids.outputFileTab.exists):
                self.ids.outputFileTab.text = "[color=#FFFFFF]" + self.ids.outputFileTab.text[15:]

            targetButton = self.ids["series" + str(seriesNum)]
            targetButton.background_color = Configs.backgroundColor
            targetButton.text = "[color=#000000]" + targetButton.text[15:]

            self.renderButtons(self.ids.userText.text)

    def removeLastSeries(self):
        if(self.numberOfSeries == 1):
            self.sendError("CANNOT REMOVE SERIES 1")
            return

        lastSeriesText = self.seriesTexts[len(self.seriesTexts) - 1].strip()

        #If user is currently working in the last series
        if(self.currentSeries == self.numberOfSeries):
            lastSeriesText = self.ids.userText.text.strip()

        if(lastSeriesText == "" or lastSeriesText == "@SERIES"):
            self.clearErrors()

            if(self.currentSeries == self.numberOfSeries):
                self.goToSeries(self.numberOfSeries - 1, True)

            self.seriesTexts.pop()
            self.ids["series" + str(self.numberOfSeries)].text = ""
            self.ids["series" + str(self.numberOfSeries)].exists = False

            self.numberOfSeries -= 1
            self.ids.seriesSelectionMenu.height = dp(55) * self.numberOfSeries

            if(self.saved):
                self.saved = False
                self.ids.runButton.colorGrey()
                self.ids.saveButton.colorBlue()
        else:
            self.sendError("SERIES " + str(self.numberOfSeries) + " INPUT TEXT MUST BE EMPTY BEFORE REMOVING THE SERIES")
            self.goToSeries(self.numberOfSeries, True)

    def splitSeries(self, fileText):
        #Remove all series
        self.goToSeries(1, True)
        for i in range(self.numberOfSeries):
            self.seriesTexts[self.numberOfSeries - 1] = ""
            self.removeLastSeries()

        self.ids.userText.text = ""
        self.clearErrors()

        #Split fileText and populate series
        splitTexts = fileText.split("@SERIES")
        for i in range(len(splitTexts)):
            if(i == 0):
                pass
            else:
                splitTexts[i] = "@SERIES" + splitTexts[i]

        if(len(splitTexts) == 0):
            splitTexts.append("@SERIES\n\n")
        elif(len(splitTexts) == 1):
            pass
        else:
            splitTexts[1] = splitTexts[0] + splitTexts[1]
            splitTexts.pop(0)

        #Populate series with splitTexts
        for i in range(len(splitTexts)):
            if(i == 0):
                self.ids.userText.text = splitTexts[0].strip()
                continue

            self.addSeries()
            self.goToSeries(i + 1, True)
            self.ids.userText.text = splitTexts[i].strip()

        self.goToSeries(1, True)

    def reSplit(self):
        #If in the output tab, return
        if(self.currentSeries == None):
            return

        #Save current working series Text into self.seriesTexts array
        self.seriesTexts[self.currentSeries - 1] = self.ids.userText.text

        fileText = "".join(self.seriesTexts)
        self.splitSeries(fileText)

    def debug(self):
        #If in the output tab, return
        if(self.currentSeries == None):
            return

        #Save current working series Text into self.seriesTexts array
        self.seriesTexts[self.currentSeries - 1] = self.ids.userText.text

        self.renderButtons(self.ids.userText.text)

        checkReportNum = InputChecks.checkReportNumber(self.seriesTexts[0], self.sendError, self.highlightError)
        if(checkReportNum == False):
            return

        checkStructure = InputChecks.checkStructure(self.seriesTexts, self.sendError, self.highlightError, self.goToSeries)
        if(not checkStructure):
            return
            
        checkAllExist = InputChecks.checkIfAllTags(self.seriesTexts, self.sendError, self.goToSeries)
        if(not checkAllExist):
            return

        checkWrittenTags = InputChecks.checkTags(self.seriesTexts, False, self.highlightError, self.sendError)
        if(not checkWrittenTags):
            return

        checkRepeats = InputChecks.checkForRepeats(self.seriesTexts, self.sendError, self.highlightError)
        if(not checkRepeats):
            return

        checkInputValues = InputChecks.checkInputValues(self.seriesTexts, self.sendError, self.highlightError)
        if(not checkInputValues):
            return

        checkNumObservations = InputChecks.checkNumObservations(self.seriesTexts, self.sendError, self.highlightError, self.goToSeries)
        if(not checkNumObservations):
            return

        checkVectors = InputChecks.checkVectors(self.seriesTexts, self.sendError, self.highlightError, self.goToSeries)
        if(not checkVectors):
            return

        checkDesignVsWeights = InputChecks.checkDesignVsWeights(self.seriesTexts, self.sendError, self.highlightError, self.goToSeries)
        if(not checkDesignVsWeights):
            return

        checkRestraints = InputChecks.checkRestraints(self.seriesTexts, self.numberOfSeries, self.sendError, self.highlightError, self.goToSeries)
        if(not checkRestraints):
            return

        secondaryChecks = InputChecks.runSecondaryChecks(self.seriesTexts, self.reportNum, self.sendError, self.highlightError, debugMode=True)
        if(not secondaryChecks):
            return

        self.sendSuccess("INPUT FILE CHECKS PASSED")

    def saveNotes(self):
        notes = self.ids.notesText.text.strip()

        if(notes == ""):
            try:
                API.deleteNote(self.fileName)
            except:
                pass
        else:
            API.saveNote(self.fileName, notes)

        if(API.getWriteNotes() == 1):
            if(notes == ""):
                if(path.exists(self.notesFilePath)):
                    remove(self.notesFilePath)

            else:
                f = open(self.notesFilePath, 'w')
                f.write(notes)
                f.close()

    def save(self):
        #Save new file
        if(self.configFilePath == ""):
            saveLocPop = NewFileSaveLocPopup(mainLayout=self)
            saveLocPop.open()
            return

        #Save current working series text into self.seriesTexts array
        if(self.currentSeries != None):
            self.seriesTexts[self.currentSeries - 1] = self.ids.userText.text

        if(self.currentSeries != None):
            self.displaySeriesNominal(self.seriesTexts[self.currentSeries - 1], self.ids["series" + str(self.currentSeries)])
        
        fileText = ""
        for seriesText in self.seriesTexts:
            fileText += seriesText.strip()
            fileText += "\n\n"

        f = open(self.configFilePath, 'w')
        f.write(fileText)
        f.close()

        try:
            self.saveNotes()
        except:
            self.sendError("COULD NOT SAVE NOTES")

        self.saved = True
        self.sendSuccess("FILE SAVED")

        if(self.currentSeries != None):
            self.renderButtons(self.ids.userText.text)
            
        self.ids.runButton.colorBlue()
        self.ids.saveButton.colorGrey()

    def runReduction(self):
        #Perform checks to make sure the input file is in a runnable state
        #######################
        #start = time.time()

        if(not self.saved):
            self.sendError("FILE MUST BE SAVED BEFORE RUNNING")
            return

        checkStructure = InputChecks.checkStructure(self.seriesTexts, self.sendError, self.highlightError, self.goToSeries)
        if(not checkStructure):
            return
            
        checkAllExist = InputChecks.checkIfAllTags(self.seriesTexts, self.sendError, self.goToSeries)
        if(not checkAllExist):
            return

        checkWrittenTags = InputChecks.checkTags(self.seriesTexts, False, self.highlightError, self.sendError)
        if(not checkWrittenTags):
            return

        checkRepeats = InputChecks.checkForRepeats(self.seriesTexts, self.sendError, self.highlightError)
        if(not checkRepeats):
            return

        checkInputValues = InputChecks.checkInputValues(self.seriesTexts, self.sendError, self.highlightError)
        if(not checkInputValues):
            return

        checkNumObservations = InputChecks.checkNumObservations(self.seriesTexts, self.sendError, self.highlightError, self.goToSeries)
        if(not checkNumObservations):
            return

        checkVectors = InputChecks.checkVectors(self.seriesTexts, self.sendError, self.highlightError, self.goToSeries)
        if(not checkVectors):
            return

        checkDesignVsWeights = InputChecks.checkDesignVsWeights(self.seriesTexts, self.sendError, self.highlightError, self.goToSeries)
        if(not checkDesignVsWeights):
            return

        checkRestraints = InputChecks.checkRestraints(self.seriesTexts, self.numberOfSeries, self.sendError, self.highlightError, self.goToSeries)
        if(not checkRestraints):
            return
        #######################
        self.clearErrors()

        if(path.exists(self.configFilePath) == False):
            self.sendError(self.configFilePath + " NOT FOUND IN THE CURRENT FOLDER\nREOPEN " + self.configFilePath + " IN ITS CURRENT LOCATION")
            return

        try:
            results = RunFile.run(self.configFilePath, outFilePath=self.outFilePath)
            self.grabOutputFile()
            self.sendSuccess("FILE SUCCESSFULLY RUN\nOUTPUT SAVED AS " + path.split(self.outFilePath)[1])

            secondaryChecks = InputChecks.runSecondaryChecks(self.seriesTexts, self.reportNum, self.sendError, self.highlightError)
            if(secondaryChecks):
                resultsCheck = InputChecks.checkResults(results)
                if(resultsCheck):
                    self.openOutputFile()

        except MARSException as ex:
            self.sendError("RUNTIME ERROR: " + str(ex))
        except AssertionError:
            self.sendError("REQUIRED PYTHON 3.5 OR LATER")
        except:
            self.sendError("UNCAUGHT ERROR RUNNING INPUT FILE. CHECK INPUTS")

        #end = time.time()
        #print(str((end - start)*1000) + " ms")

    def sendError(self, message):
        self.ids.errors.foreground_color = Configs.redTextColor
        self.ids.errors.text = "ERROR:\n" + message

    def sendSuccess(self, message):
        self.ids.errors.foreground_color = Configs.greenTextColor
        self.ids.errors.text = message

    def clearErrors(self):
        self.ids.errors.text = ""

    def grabNotes(self):
        try:
            notes = API.getNote(self.fileName)
            self.ids.notesText.text = notes
        except:
            self.ids.notesText.text = ""

    def grabOutputFile(self):
        if(path.exists(self.outFilePath)):
            f = open(self.outFilePath, 'r')
            fileText = f.read()
            f.close()

            self.outputText = fileText
            
            #Render output button/tab
            if(self.currentSeries != None):
                self.ids.outputFileTab.text = "[color=#FFFFFF][b]Output[/b][/color]"
            else:
                self.ids.userText.text = fileText
                self.ids.userText.cursor = (0, 0)

            self.ids.outputFileTab.exists = True
        else:
            self.ids.outputFileTab.text = ""
            self.ids.outputFileTab.exists = False
            self.outputText = ""

    def openOutputFile(self):
        outputButton = self.ids.outputFileTab
        if(outputButton.exists):
            #If already on output tab, return
            if(self.currentSeries == None):
                return

            wasSaved = self.saved

            #Save current text and render current series button nominal
            self.seriesTexts[self.currentSeries - 1] = self.ids.userText.text
            seriesButtonId = "series" + str(self.currentSeries)
            self.displaySeriesNominal(self.seriesTexts[self.currentSeries - 1], self.ids[seriesButtonId])

            self.currentSeries = None

            #Pull output text into userText
            self.ids.userText.text = self.outputText

            if(wasSaved):
                self.ids.runButton.colorBlue()
                self.ids.saveButton.colorGrey()
                self.saved = True

            self.ids.userText.cursor = (0, 0)
            self.ids.userText.select_text(0, 0)
            self.ids.userText.readonly = True

            for sn in range(1, self.numberOfSeries + 1):
                seriesID = "series" + str(sn)
                seriesButton = self.ids[seriesID]

                if(seriesButton.exists):
                    seriesButton.background_color = Configs.menuColor
                    seriesButton.text = "[color=#FFFFFF]" + seriesButton.text[15:]

            outputButton.background_color = Configs.backgroundColor
            outputButton.text = "[color=#000000]" + outputButton.text[15:]

            self.greyOutButtons()

class OrderedText(TextInput):
    def __init__(self, **kwargs):
        super().__init__()
        self.height = dp(39)

        with self.canvas.before:
            Color(rgba=Configs.menuColor)
            self.borderRect = Rectangle(size=(self.size[0] + dp(2), self.size[1] + dp(2)), pos=(self.pos[0] - dp(1), self.pos[1] - dp(1)))
        
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.font_name = "Menlo.ttc"
        self.text = ""
        self.orderNum = 0
        self.background_normal = ''

        try:
            self.font_size = dp(API.getFontSize())
        except:
            self.font_size = dp(12)

        self.write_tab = False
        self.multiline = False
        self.padding = [dp(5), dp(5), dp(5), dp(5)]

    def _update_rect(self, instance, value):
        self.borderRect.pos = (instance.pos[0] - dp(1), instance.pos[1] - dp(1))
        self.borderRect.size = (instance.size[0] + dp(2), instance.size[1] + dp(2))

    def getInputText(self, userText, tag):
        inputLines = []
        for line in userText.splitlines():
            if(len(line.split()) > 0 and line.split()[0] == tag):
                inputLines.append(tag.join(line.split(tag)[1:]).strip())

        if(inputLines == []):
            if(tag == "<Direct-Reading-SF>"):
                return "1.0"

        return "\n".join(inputLines)

class UserInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__()
        
        try:
            self.font_size = dp(API.getFontSize())
        except:
            self.font_size = dp(12)

        with self.canvas.before:
            Color(rgba=Configs.menuColor)
            self.borderRect = Rectangle(size=(self.size[0] + dp(2), self.size[1] + dp(2)), pos=(self.pos[0] - dp(1), self.pos[1] - dp(1)))
        
        self.bind(size=self._update_rect, pos=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.borderRect.pos = (instance.pos[0] - dp(1), instance.pos[1] - dp(1))
        self.borderRect.size = (instance.size[0] + dp(2), instance.size[1] + dp(2))

    def setSelectionColor(self):
        self.selection_color = Configs.highlightColor

class MainErrorText(TextInput):
    def __init__(self, **kwargs):
        super().__init__()
        
        try:
            self.font_size = dp(API.getFontSize())
        except:
            self.font_size = dp(12)

        self.text = "WELCOME TO MARS: MASS REDUCTION SOFTWARE!"
        self.foreground_color = Configs.greenTextColor
        self.selection_color = Configs.highlightColor

class ExtraButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.background_normal = ''
        self.color = (0, 0, 0, 1)
        self.background_color = (0.99, 0.99, 0.99, 0.98)
        self.font_size = dp(15)
        self.markup = True

        with self.canvas.before:
            Color(rgba=Configs.menuColor)
            self.borderRect = Rectangle(size=(self.size[0] + dp(2), self.size[1] + dp(2)), pos=(self.pos[0] - dp(1), self.pos[1] - dp(1)))
        
        self.bind(size=self._update_rect, pos=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.borderRect.pos = (instance.pos[0] - dp(1), instance.pos[1] - dp(1))
        self.borderRect.size = (instance.size[0] + dp(2), instance.size[1] + dp(2))

class TopMenuButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.size_hint = (1, None)
        self.height = dp(50)
        self.halign = 'center'
        self.font_size = dp(15)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = Configs.menuColor

        self.bind(state=self._updateState)

    def _updateState(self, instance, value):
        if(value == "down"):
            self.background_color = (0.155*0.25, 0.217*0.25, 0.292*0.25, 0.65)
        elif(value == "normal"):
            self.background_color = Configs.menuColor

class InputButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.size_hint = (None, None)
        self.buttonColor = Configs.inputButtonColor
        self.currentColor = self.buttonColor
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.markup = True
        self.font_size = dp(14)
        self.halign = 'center'
        self.size = (dp(118), dp(62))

        with self.canvas.before:
            self.canvasColor = Color(rgba=self.currentColor)
            self.backgroundRect = RoundedRectangle(size=self.size, pos=self.pos, radius=[self.width/27])

        self.bind(size=self._update_rect, pos=self._update_rect)
        self.bind(state=self._updateState)

        self.initialize()

    def _update_rect(self, instance, value):
        self.backgroundRect.pos = instance.pos
        self.backgroundRect.size = instance.size
        self.backgroundRect.radius = [instance.width/27]
    
    def _updateState(self, instance, value):
        if(value == "down"):
            self.canvasColor.rgba = (self.currentColor[0]*0.6, self.currentColor[1]*0.6, self.currentColor[2]*0.6, self.currentColor[3])
        elif(value == "normal"):
            self.canvasColor.rgba = self.currentColor

    def initialize(self):
        Clock.schedule_once(self.colorBlue, 0)

    def colorGrey(self, *args):
        self.currentColor = (0.52, 0.52, 0.52, 0.72)
        self.canvasColor.rgba = self.currentColor

    def colorBlue(self, *args):
        self.currentColor = self.buttonColor
        self.canvasColor.rgba = self.currentColor

class BottomButton(InputButton):
    def __init__(self, **kwargs):
        super().__init__()
        self.size = (dp(82), dp(50))
        self.buttonColor = Configs.greenButtonColor
        self.font_size = dp(14)

class RunButton(InputButton):
    def __init__(self, **kwargs):
        super().__init__()
        self.size = (dp(82), dp(50))
        self.buttonColor = Configs.greenButtonColor
        self.font_size = dp(14)

    def initialize(self):
        Clock.schedule_once(self.colorGrey, 0)

class CancelButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(150), dp(45))
        self.background_normal = ''
        self.background_down = ''
        self.background_color = Configs.cancelButtonColor
        self.font_size = dp(16)
        self.text = kwargs.get("text", "Cancel")
        self.halign = 'center'

        self.bind(state=self._updateState)

    def _updateState(self, instance, value):
        if(value == "down"):
            self.background_color = (0.70*0.6, 0.135*0.6, 0.05*0.6, 0.92)
        elif(value == "normal"):
            self.background_color = Configs.cancelButtonColor

class WriteButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(150), dp(45))
        self.background_normal = ''
        self.background_down = ''
        self.background_color = Configs.inputButtonColor
        self.font_size = dp(16)
        self.text = kwargs.get("text", "Write")
        self.halign = 'center'

        self.bind(state=self._updateState)

    def _updateState(self, instance, value):
        if(value == "down"):
            self.background_color = (0.13*0.5, 0.5*0.5, 0.95*0.5, 0.94)
        elif(value == "normal"):
            self.background_color = Configs.inputButtonColor

class SeriesSelectionMenu(GridLayout):
    def __init__(self, **kwargs):
        super().__init__()
        self.size_hint = (1, None)
        self.height = dp(55)
        self.cols = 1

class AddSeriesButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.size_hint = (1, None)
        self.height = dp(60)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = Configs.greenButtonColor
        self.text = "   Add Series"
        self.halign = 'center'
        self.font_size = dp(17)

        self.bind(state=self._updateState)

    def _updateState(self, instance, value):
        if(value == "down"):
            self.background_color = (self.background_color[0]*0.68, self.background_color[1]*0.68, self.background_color[2]*0.68, self.background_color[3])
        elif(value == "normal"):
            self.background_color = Configs.greenButtonColor

class SeriesButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.size_hint = (1, None)
        self.height = dp(55)
        self.seriesNum = 0
        self.exists = False
        self.text = ''
        self.markup = True
        self.halign = 'center'
        self.font_size = dp(17)
        self.background_normal = ''
        self.background_color = Configs.menuColor
        self.background_down =  ''

class RemoveSeriesButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.size_hint = (1, None)
        self.height = dp(50)
        self.background_normal = ''
        self.background_down = ''
        self.halign = 'center'
        self.text = "    Remove Last\nSeries"
        self.font_size = dp(16)
        self.background_color = Configs.cancelButtonColor

        self.bind(state=self._updateState)

    def _updateState(self, instance, value):
        if(value == "down"):
            self.background_color = (0.70*0.6, 0.135*0.6, 0.05*0.6, 0.92)
        elif(value == "normal"):
            self.background_color = Configs.cancelButtonColor

class PopupBase(Popup):
    def __init__(self, **kwargs):
        super().__init__()
        self.background = path.join("Images", "Popup_Background.png")
        self.title_color = (0, 0, 0, 1)
        self.title_size = dp(18)
        self.size_hint = (None, None)

class PopupLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.markup = True
        self.halign = "left"
        self.valign = "bottom"
        self.color = (0.095, 0.095, 0.096, 0.9)
        self.font_size = dp(15)

        self.bind(texture_size=self.updateLabel, width=self.updateLabel)

    def updateLabel(self, inst, value):
        self.height = self.texture_size[1]
        self.text_size = (self.width, None)

class PopupErrorLabel(Label):
    def __init__(self, **kwargs):
        super().__init__()
        self.markup = True
        self.halign = "left"
        self.valign = "bottom"
        self.color = Configs.redTextColor
        self.font_size = dp(15)
        self.height = dp(20)
        self.text = ""

        self.bind(width=self.updateLabel)

    def updateLabel(self, inst, value):
        self.text_size = (self.width, None)

class MarsImage(Image):
    def getImagePath(self, fileName):
        return path.join("Images", fileName)

    def getImagePosition(self, parentPos, parentWidth, parentTextWidth, xAdjustment=0, yAdjustment=0):
        posY = parentPos[1] + dp(17) + yAdjustment
        posX = parentPos[0] + (parentWidth - parentTextWidth) / 2 - dp(25) + xAdjustment

        return (posX, posY)

class DbEntryLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.markup = True
        self.halign = "left"
        self.valign = "center"
        self.color = (0.095, 0.095, 0.096, 0.9)
        self.font_size = dp(14)
        self.height = dp(37)

        self.bind(width=self.updateLabel)

    def updateLabel(self, inst, value):
        self.text_size = (self.width, self.height)

class DBSelectButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.size_hint = (0.13, None)
        self.height = dp(37)
        self.background_normal = ''
        self.background_color = Configs.greenButtonColor
        self.text = "Select"

        self.rowId = kwargs.get("rowId", "")

class DBDeleteButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.size_hint = (0.07, None)
        self.height = dp(37)
        self.background_normal = ''
        self.background_color = Configs.cancelButtonColor
        self.text = "Del"

        self.clicked = False
        self.rowId = kwargs.get("rowId", "")
        self.selectButtonPair = kwargs.get("selectButtonPair", None)

class DbScrollView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll_timeout = 0

        with self.canvas.before:
            Color(rgba=(0.98, 0.98, 0.98, 1))
            self.backgroundRect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.backgroundRect.pos = instance.pos
        self.backgroundRect.size = instance.size

class LabInfoPopup(PopupBase):
    def __init__(self, **kwargs):
        self.mainLayout = kwargs.get("mainLayout", None)
        super().__init__()

    def submit(self):
        #Check if all fields have been entered
        labInfoText = self.ids.labInfoText.text
        reportNumText = self.ids.reportNumText.text

        labInfoOrder = self.ids.labInfoText.orderNum
        reportNumOrder = self.ids.reportNumText.orderNum

        if(labInfoText == "" or reportNumText == ""):
            self.ids.labInfoPopError.text = "Enter data for all fields"
            return

        #Call the writeText function in the MainLayout to write text into input file
        self.mainLayout.removeLines(["#", "<Report-Number>"])

        rowStart1, rowEnd1 = self.mainLayout.writeText(labInfoText, labInfoOrder)
        rowStart2, rowEnd2 = self.mainLayout.writeText(reportNumText, reportNumOrder)

        #Highlight the text block added
        self.mainLayout.highlight(rowStart1, rowEnd2)

        self.dismiss()

class RestraintPopup(PopupBase):
    def __init__(self, **kwargs):
        self.mainLayout = kwargs.get("mainLayout", None)
        super().__init__()

    def submit(self):
        restraintIDText = self.ids.restraintIDText.text
        restraintUncertaintyText = self.ids.restraintUncertaintyText.text
        #randomErrorText = self.ids.randomErrorText.text

        restraintIDOrder = self.ids.restraintIDText.orderNum
        restraintUncertaintyOrder = self.ids.restraintUncertaintyText.orderNum
        #randomErrorOrder = self.ids.randomErrorText.orderNum

        if(restraintIDText == "" or restraintUncertaintyText == ""):
            self.ids.restraintPopError.text = "Enter data for all fields"
            return

        self.mainLayout.removeLines(["<Restraint-ID>", "<Unc-Restraint>"])

        rowStart1, rowEnd1 = self.mainLayout.writeText(restraintIDText, restraintIDOrder)
        rowStart2, rowEnd2 = self.mainLayout.writeText(restraintUncertaintyText, restraintUncertaintyOrder)
        #rowStart3, rowEnd3 = self.mainLayout.writeText(randomErrorText, randomErrorOrder)

        self.mainLayout.highlight(rowStart1, rowEnd2)

        self.dismiss()

class DatePopup(PopupBase):
    def __init__(self, **kwargs):
        self.mainLayout = kwargs.get("mainLayout", None)
        super().__init__()

    def submit(self):
        dateText = self.ids.dateText.text
        techIDText = self.ids.techIDText.text
        balanceIDText = self.ids.balanceIDText.text
        directReadingsText = "1" if self.ids.directReadingsCheckBox.active else "0"
        directReadingsSFText = self.ids.directReadingsSFText.text

        dateOrder = self.ids.dateText.orderNum
        techIDOrder = self.ids.techIDText.orderNum
        balanceOrder = self.ids.balanceIDText.orderNum
        directReadingsOrder = 9
        directReadingsSFOrder = self.ids.directReadingsSFText.orderNum

        if(self.ids.directReadingsCheckBox.active and directReadingsSFText == ""):
            self.ids.datePopError.text = "Enter data for all fields"
            return

        if(dateText == "" or techIDText == "" or balanceIDText == "" or \
            (self.ids.directReadingsCheckBox.active == False and self.ids.manualReadingsCheckBox.active == False)):
            self.ids.datePopError.text = "Enter data for all fields"
            return

        self.mainLayout.removeLines(["<Date>", "<Technician-ID>", "<Balance-ID>", "<Direct-Readings>", "<Direct-Reading-SF>"])

        rowStart1, rowEnd1 = self.mainLayout.writeText(dateText, dateOrder)
        rowStart2, rowEnd2 = self.mainLayout.writeText(techIDText, techIDOrder)
        rowStart3, rowEnd3 = self.mainLayout.writeText(balanceIDText, balanceOrder)
        rowStart4, rowEnd4 = self.mainLayout.writeText(directReadingsText, directReadingsOrder)

        if(self.ids.directReadingsCheckBox.active):
            rowStart5, rowEnd5 = self.mainLayout.writeText(directReadingsSFText, directReadingsSFOrder)
        else:
            self.mainLayout.writeText("", 10)
            rowStart5 = rowStart4
            rowEnd5 = rowEnd4

        self.mainLayout.highlight(rowStart1, rowEnd5)

        self.dismiss()

class DesignPopup(PopupBase):
    def __init__(self, **kwargs):
        self.mainLayout = kwargs.get("mainLayout", None)
        super().__init__()

    def writeDesign(self, design):
        if(design == "3-1"):
            self.ids.designText.text = "1 -1  0\n1  0 -1\n0  1 -1"
            self.ids.designText.cursor = (0, 0)
            self.ids.designIDText.text = "111"

        elif(design == "4-1"):
            self.ids.designText.text = "1 -1  0  0\n1  0 -1  0\n1  0  0 -1\n0  1 -1  0\n0  1  0 -1\n0  0  1 -1"
            self.ids.designText.cursor = (0, 0)
            self.ids.designIDText.text = "112"

        elif(design == "2 x 4-1"):
            self.ids.designText.text = "1 -1  0  0\n1  0 -1  0\n1  0  0 -1\n0  1 -1  0\n0  1  0 -1\n0  0  1 -1\n1 -1  0  0\n1  0 -1  0\n1  0  0 -1\n0  1 -1  0\n0  1  0 -1\n0  0  1 -1"
            self.ids.designText.cursor = (0, 0)
            self.ids.designIDText.text = "112"

        elif(design == "5-1"):
            self.ids.designText.text = "1 -1  0  0  0\n1  0 -1  0  0\n1  0  0 -1  0\n1  0  0  0 -1\n0  1 -1  0  0\n0  1  0 -1  0\n0  1  0  0 -1\n0  0  1 -1  0\n0  0  1  0 -1\n0  0  0  1 -1"
            self.ids.designText.cursor = (0, 0)
            self.ids.designIDText.text = "114"

        elif(design == "532111"):
            self.ids.designText.text = "1 -1 -1  1 -1  0\n1 -1 -1  0  1 -1\n1 -1 -1 -1  0  1\n1 -1 -1  0  0  0\n1  0 -1 -1 -1 -1\n0  1 -1  1 -1 -1\n0  1 -1 -1  1 -1\n0  1 -1 -1 -1  1\n0  0  1 -1 -1  0\n0  0  1 -1  0 -1\n0  0  1  0 -1 -1"
            self.ids.designText.cursor = (0, 0)
            self.ids.designIDText.text = "032"

        elif(design == "522111"):
            self.ids.designText.text = "1 -1 -1 -1 -1  1\n1 -1 -1 -1  1 -1\n1 -1 -1  1 -1 -1\n1 -1  0 -1 -1 -1\n1  0 -1 -1 -1 -1\n0  1 -1  1 -1  0\n0  1 -1 -1  0  1\n0  1 -1  0  1 -1"
            self.ids.designText.cursor = (0, 0)
            self.ids.designIDText.text = "310"

        self.ids.dropDownn.dismiss()
        self.ids.dropDownMain.text = design

    def evalDesign(self):
        design = self.ids.designText.text.splitlines()

        observations = 0
        positions = 0

        for line in design:
            if(line.strip() != ""):
                observations += 1

            if(len(line.strip().split()) > positions):
                positions = len(line.strip().split())

        self.ids.positionsLabel.text = "Positions:  " + str(positions)
        self.ids.observationsLabel.text = "Observations:  " + str(observations)

    def submit(self):
        designIDText = self.ids.designIDText.text
        designText = self.ids.designText.text

        designIDOrder = self.ids.designIDText.orderNum
        designOrder = self.ids.designText.orderNum

        if(designIDText == "" or designText == ""):
            self.ids.designPopError.text = "Enter data for all fields"
            return

        self.mainLayout.removeLines(["<Design-ID>", "<Design>"])

        rowStart1, rowEnd1 = self.mainLayout.writeText(designIDText, designIDOrder)
        rowStart2, rowEnd2 = self.mainLayout.writeText(designText, designOrder)

        self.mainLayout.highlight(rowStart1, rowEnd2)

        self.dismiss()

class WeightsPopup(PopupBase):
    def __init__(self, **kwargs):
        self.mainLayout = kwargs.get("mainLayout", None)
        super().__init__()

    def submit(self):
        checkIDText = self.ids.checkIDText.text
        nominalsText = "1" if self.ids.gramsCheckBox.active else "0"
        weightsText = self.ids.weightsText.text

        checkIDOrder = self.ids.checkIDText.orderNum
        nominalsOrder = 15
        weightsOrder = self.ids.weightsText.orderNum

        if(checkIDText == "" or weightsText == "" or \
            (self.ids.gramsCheckBox.active == False and self.ids.poundsCheckBox.active == False)):
            self.ids.weightsPopError.text = "Enter data for all fields"
            return

        self.mainLayout.removeLines(["<Check-ID>", "<Grams>", "<Position>"])

        rowStart1, rowEnd1 = self.mainLayout.writeText(checkIDText, checkIDOrder)
        rowStart2, rowEnd2 = self.mainLayout.writeText(nominalsText, nominalsOrder)
        rowStart3, rowEnd3 = self.mainLayout.writeText(weightsText, weightsOrder)

        self.mainLayout.highlight(rowStart1, rowEnd3)

        #Render series nominal
        seriesButtonId = "series" + str(self.mainLayout.currentSeries)
        self.mainLayout.displaySeriesNominal(self.mainLayout.ids.userText.text, self.mainLayout.ids[seriesButtonId])

        self.dismiss()

class VectorsPopup(PopupBase):
    def __init__(self, **kwargs):
        self.mainLayout = kwargs.get("mainLayout", None)
        super().__init__()

    def submit(self):
        restraintText = self.ids.restraintVectorText.text
        checkText = self.ids.checkVectorText.text
        nextRestraintText = self.ids.nextRestraintText.text

        restraintOrder = self.ids.restraintVectorText.orderNum
        checkOrder = self.ids.checkVectorText.orderNum
        nextRestraintOrder = self.ids.nextRestraintText.orderNum

        if(restraintText == "" or checkText == "" or nextRestraintText == ""):
            self.ids.vectorsPopError.text = "Enter data for all fields"
            return

        self.mainLayout.removeLines(["<Restraint>", "<Check-Standard>", "<Pass-Down>"])

        rowStart1, rowEnd1 = self.mainLayout.writeText(restraintText, restraintOrder)
        rowStart2, rowEnd2 = self.mainLayout.writeText(checkText, checkOrder)
        rowStart3, rowEnd3 = self.mainLayout.writeText(nextRestraintText, nextRestraintOrder)

        self.mainLayout.highlight(rowStart1, rowEnd3)

        self.dismiss()

class StatisticsPopup(PopupBase):
    def __init__(self, **kwargs):
        self.mainLayout = kwargs.get("mainLayout", None)
        super().__init__()

    def submit(self):
        sigmawText = self.ids.sigmawText.text.strip()
        sigmatText = self.ids.sigmatText.text.strip()

        sigmawOrder = self.ids.sigmawText.orderNum
        sigmatOrder = self.ids.sigmatText.orderNum

        if(sigmawText == "" or sigmatText == ""):
            self.ids.sigmaPopError.color = Configs.redTextColor
            self.ids.sigmaPopError.text = "Enter data for all fields"
            return

        self.mainLayout.removeLines(["<Sigma-w>", "<Sigma-b>"])

        rowStart1, rowEnd1 = self.mainLayout.writeText(sigmawText, sigmawOrder)
        rowStart2, rowEnd2 = self.mainLayout.writeText(sigmatText, sigmatOrder)

        self.mainLayout.highlight(rowStart1, rowEnd2)

        self.dismiss()

    def evalSaveButtons(self, saveDisabled):
        sigw = self.ids.sigmawText.text.strip()
        sigt = self.ids.sigmatText.text.strip()

        if(saveDisabled == True and (sigw != "" and sigt != "")):
            self.ids.saveStatsButton.disabled = False

        elif(saveDisabled == False and (sigw == "" or sigt == "")):
            self.ids.saveStatsButton.disabled = True

    def saveStats(self, sigw, sigt):
        saveStatisticsPopup = SaveStatisticsPopup(sigw, sigt)
        saveStatisticsPopup.open()

    def getStats(self):
        statsDbPopup = StatsDbPopup(self)
        statsDbPopup.buildDbPopup()
        statsDbPopup.open()

class SaveStatisticsPopup(PopupBase):
    def __init__(self, sigw, sigt, **kwargs):
        self.sigw = sigw
        self.sigt = sigt
        super().__init__()

    def saveStats(self):
        if(self.ids.nominalText.text.strip() != "" and self.ids.descriptionText.text.strip() != ""):
            try:
                API.saveStats(self.ids.nominalText.text.strip(), self.ids.descriptionText.text.strip(), self.sigw, self.sigt)

                self.ids.statsError.color = Configs.greenTextColor
                self.ids.statsError.text = "Added " + self.ids.descriptionText.text.strip() + " stats"
                Thread(target=self.displaySuccess).start()
            except:
                self.ids.statsError.color = Configs.redTextColor
                self.ids.statsError.text = "Error adding stats to database"
        else:
            self.ids.statsError.color = Configs.redTextColor
            self.ids.statsError.text = "Enter all fields"

    def displaySuccess(self):
        sleep(1)
        self.dismiss()

class StatsDbPopup(PopupBase):
    def __init__(self, rootPop):
        super().__init__()
        self.auto_dismiss = False
        self.title = "Statistics Database"
        self.size = (dp(750), dp(580))
        self.stagedDelete = []
        self.deleteButtonRef = None

        self.rootPop = rootPop

    def resizeGrid(self, inst, value):
        inst.height = value

    def resizeBottomLayout(self, inst, value):
        inst.spacing = value - 2*dp(150)

    def goBack(self, inst):
        self.dismiss()

    def selectStat(self, inst):
        try:
            statData = API.getStat(inst.rowId)[0]
        except:
            self.rootPop.ids.sigmaPopError.color = Configs.redTextColor
            self.rootPop.ids.sigmaPopError.text = "Error getting statistics from database"
            return

        self.rootPop.ids.sigmawText.text = statData[1]
        self.rootPop.ids.sigmatText.text = statData[2]

        self.rootPop.ids.sigmaPopError.color = Configs.greenTextColor
        self.rootPop.ids.sigmaPopError.text = "Loaded " + statData[0] + " statistics"

        self.dismiss()

    def renderDeleteButton(self):
        if(self.stagedDelete == []):
            self.deleteButtonRef.text = ""
            self.deleteButtonRef.disabled = True
            self.deleteButtonRef.opacity = 0
        else:
            self.deleteButtonRef.text = "Delete (" + str(len(self.stagedDelete)) + ")"
            self.deleteButtonRef.disabled = False
            self.deleteButtonRef.opacity = 1

    def stageDelete(self, inst):
        rowId = inst.rowId

        if(inst.clicked == False):
            self.stagedDelete.append(rowId)
            
            inst.background_color = (0.42, 0.42, 0.42, 0.42)
            inst.text = "Undo"
            inst.color = (0, 0, 0, 1)
            inst.selectButtonPair.disabled = True

            inst.clicked = True
        else:
            #unstage rowId for delete
            for i in range(len(self.stagedDelete)):
                if(self.stagedDelete[i] == rowId):
                    self.stagedDelete.pop(i)
                    break

            inst.background_color = Configs.cancelButtonColor
            inst.text = "Del"
            inst.color = (1, 1, 1, 1)
            inst.selectButtonPair.disabled = False

            inst.clicked = False

        self.renderDeleteButton()

    def commitDelete(self, inst):
        self.stagedDelete.sort(reverse=True)
        for rowId in self.stagedDelete:
            API.deleteStat(rowId)

        self.stagedDelete = []
        self.buildDbPopup()

    def buildDbPopup(self):
        try:
            statsData = API.getStats()
        except:
            statsData = []

        mainPopLayout = BoxLayout(orientation="vertical", spacing=dp(12), padding=(dp(10), dp(10)))
        sv = DbScrollView(do_scroll_x=False, do_scroll_y=True, size_hint=(1, None), height=dp(400))

        dbGrid = GridLayout(size_hint=(1, None), spacing=dp(5), padding=(dp(15), dp(15)), cols=1)
        dbGrid.bind(minimum_height=self.resizeGrid)

        bottomLayout = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(50))
        bottomLayout.bind(width=self.resizeBottomLayout)

        titleLabel = PopupLabel(text="Saved Statistics", size_hint=(1, None))

        #Table Header
        dbEntryLayout = GridLayout(size_hint=(1, None), height=dp(37), spacing=dp(5), rows=1)
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.14, None), text="[b]Nominal[/b]"))
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.27, None), text="[b]Description[/b]"))
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.12, None), text="[b]" + chr(963) + "[size=8dp]w[/size][/b]"))
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.12, None), text="[b]" + chr(963) + "[size=8dp]b[/size][/b]"))
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.15, None), text="[b]Entered On[/b]"))
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.13, None), text=""))
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.07, None), text=""))

        dbGrid.add_widget(dbEntryLayout)

        #Table Content
        for entry in statsData:
            dbEntryLayout = GridLayout(size_hint=(1, None), height=dp(37), spacing=dp(5), rows=1)
            dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.14, None), text=entry[1]))
            dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.27, None), text=entry[2]))
            dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.12, None), text=entry[3]))
            dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.12, None), text=entry[4]))
            dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.15, None), text=entry[5]))

            selectStatButton = DBSelectButton(rowId=entry[0])
            deleteStatButton = DBDeleteButton(rowId=entry[0], selectButtonPair=selectStatButton)

            selectStatButton.bind(on_release=self.selectStat)
            deleteStatButton.bind(on_release=self.stageDelete)

            dbEntryLayout.add_widget(selectStatButton)
            dbEntryLayout.add_widget(deleteStatButton)

            dbGrid.add_widget(dbEntryLayout)

        sv.add_widget(dbGrid)

        backButton = WriteButton(text="Back")
        backButton.bind(on_release=self.goBack)

        deleteButton = CancelButton(text="", disabled=True, opacity=0)
        deleteButton.bind(on_release=self.commitDelete)
        self.deleteButtonRef = deleteButton

        bottomLayout.add_widget(backButton)
        bottomLayout.add_widget(deleteButton)

        mainPopLayout.add_widget(titleLabel)
        mainPopLayout.add_widget(sv)
        mainPopLayout.add_widget(bottomLayout)

        self.content = mainPopLayout

class SwPopup(PopupBase):
    def __init__(self, **kwargs):
        self.mainLayout = kwargs.get("mainLayout", None)
        super().__init__()

    def submit(self):
        swMassText = self.ids.swMassText.text
        swDensityText = self.ids.swDensityText.text
        swCCEText = self.ids.swCCEText.text

        swMassOrder = self.ids.swMassText.orderNum
        swDensityOrder = self.ids.swDensityText.orderNum
        swCCEOrder = self.ids.swCCEText.orderNum

        if(swMassText == "" or swDensityText == "" or swCCEText == ""):
            self.ids.swPopError.color = Configs.redTextColor
            self.ids.swPopError.text = "Enter data for all fields"
            return

        self.mainLayout.removeLines(["<sw-Mass>", "<sw-Density>", "<sw-CCE>"])

        rowStart1, rowEnd1 = self.mainLayout.writeText(swMassText, swMassOrder)
        rowStart2, rowEnd2 = self.mainLayout.writeText(swDensityText, swDensityOrder)
        rowStart3, rowEnd3 = self.mainLayout.writeText(swCCEText, swCCEOrder)

        self.mainLayout.highlight(rowStart1, rowEnd3)

        self.dismiss()

    def evalSaveButtons(self, saveDisabled):
        mass = self.ids.swMassText.text.strip()
        density = self.ids.swDensityText.text.strip()
        cce = self.ids.swCCEText.text.strip()

        if(saveDisabled == True and (mass != "" and density != "" and cce != "")):
            self.ids.saveSwButton.disabled = False

        elif(saveDisabled == False and (mass == "" or density == "" or cce == "")):
            self.ids.saveSwButton.disabled = True

    def saveSw(self, mass, density, cce):
        saveSwPopup = SaveSwPopup(mass, density, cce)
        saveSwPopup.open()

    def getSw(self):
        swDbPopup = SwDbPopup(self)
        swDbPopup.buildDbPopup()
        swDbPopup.open()

class SaveSwPopup(PopupBase):
    def __init__(self, mass, density, cce, **kwargs):
        self.swMass = mass
        self.swDensity = density
        self.swCCE = cce
        super().__init__()

        self.ids.addButton.bind(on_release=self.saveSw)

    def saveSw(self, inst):
        if(self.ids.swNameText.text.strip() != ""):
            Thread(target=self.setDebounce).start()
            try:
                API.saveSw(self.ids.swNameText.text.strip(), self.swMass, self.swDensity, self.swCCE)

                self.ids.swNameError.color = Configs.greenTextColor
                self.ids.swNameError.text = "Added " + self.ids.swNameText.text.strip()
                Thread(target=self.pauseSuccess).start()
            except:
                self.ids.swNameError.color = Configs.redTextColor
                self.ids.swNameError.text = "Error adding sw to database"
        else:
            self.ids.swNameError.color = Configs.redTextColor
            self.ids.swNameError.text = "Name required to add sw"

    def pauseSuccess(self):
        sleep(1)
        self.dismiss()

    def setDebounce(self, *args):
        self.ids.addButton.unbind(on_release=self.saveSw)

class SwDbPopup(PopupBase):
    def __init__(self, rootPop):
        super().__init__()
        self.auto_dismiss = False
        self.title = "Sensitivity Weight Database"
        self.size = (dp(750), dp(580))
        self.stagedDelete = []
        self.deleteButtonRef = None

        self.rootPop = rootPop

    def resizeGrid(self, inst, value):
        inst.height = value

    def resizeBottomLayout(self, inst, value):
        inst.spacing = value - 2*dp(150)

    def goBack(self, inst):
        self.dismiss()

    def selectSw(self, inst):
        try:
            swData = API.getSw(inst.rowId)[0]
        except:
            self.rootPop.ids.swPopError.color = Configs.redTextColor
            self.rootPop.ids.swPopError.text = "Error getting sw from database"
            return

        self.rootPop.ids.swMassText.text = swData[1]
        self.rootPop.ids.swDensityText.text = swData[2]
        self.rootPop.ids.swCCEText.text = swData[3]

        self.rootPop.ids.swPopError.color = Configs.greenTextColor
        self.rootPop.ids.swPopError.text = "Loaded " + swData[0]

        self.dismiss()

    def renderDeleteButton(self):
        if(self.stagedDelete == []):
            self.deleteButtonRef.text = ""
            self.deleteButtonRef.disabled = True
            self.deleteButtonRef.opacity = 0
        else:
            self.deleteButtonRef.text = "Delete (" + str(len(self.stagedDelete)) + ")"
            self.deleteButtonRef.disabled = False
            self.deleteButtonRef.opacity = 1

    def stageDelete(self, inst):
        rowId = inst.rowId

        if(inst.clicked == False):
            self.stagedDelete.append(rowId)
            
            inst.background_color = (0.42, 0.42, 0.42, 0.42)
            inst.text = "Undo"
            inst.color = (0, 0, 0, 1)
            inst.selectButtonPair.disabled = True

            inst.clicked = True
        else:
            #unstage rowId for delete
            for i in range(len(self.stagedDelete)):
                if(self.stagedDelete[i] == rowId):
                    self.stagedDelete.pop(i)
                    break

            inst.background_color = Configs.cancelButtonColor
            inst.text = "Del"
            inst.color = (1, 1, 1, 1)
            inst.selectButtonPair.disabled = False

            inst.clicked = False

        self.renderDeleteButton()

    def commitDelete(self, inst):
        self.stagedDelete.sort(reverse=True)
        for rowId in self.stagedDelete:
            API.deleteSw(rowId)

        self.stagedDelete = []
        self.buildDbPopup()

    def buildDbPopup(self):
        try:
            swData = API.getSws()
        except:
            swData = []

        mainPopLayout = BoxLayout(orientation="vertical", spacing=dp(12), padding=(dp(10), dp(10)))
        sv = DbScrollView(do_scroll_x=False, do_scroll_y=True, size_hint=(1, None), height=dp(400))

        dbGrid = GridLayout(size_hint=(1, None), spacing=dp(5), padding=(dp(15), dp(15)), cols=1)
        dbGrid.bind(minimum_height=self.resizeGrid)

        bottomLayout = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(50))
        bottomLayout.bind(width=self.resizeBottomLayout)

        titleLabel = PopupLabel(text="Saved Sensitivity Weights", size_hint=(1, None))

        #Table Header
        dbEntryLayout = GridLayout(size_hint=(1, None), height=dp(37), spacing=dp(5), rows=1)
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.17, None), text="[b]Name[/b]"))
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.24, None), text="[b]Mass (mg)[/b]"))
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.11, None), text="[b]Density[/b]"))
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.13, None), text="[b]CCE[/b]"))
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.15, None), text="[b]Entered On[/b]"))
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.13, None), text=""))
        dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.07, None), text=""))

        dbGrid.add_widget(dbEntryLayout)

        #Table Content
        for entry in swData:
            dbEntryLayout = GridLayout(size_hint=(1, None), height=dp(37), spacing=dp(5), rows=1)
            dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.17, None), text=entry[1]))
            dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.24, None), text=entry[2]))
            dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.11, None), text=entry[3]))
            dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.13, None), text=entry[4]))
            dbEntryLayout.add_widget(DbEntryLabel(size_hint=(0.15, None), text=entry[5]))

            selectSwButton = DBSelectButton(rowId=entry[0])
            deleteSwButton = DBDeleteButton(rowId=entry[0], selectButtonPair=selectSwButton)

            selectSwButton.bind(on_release=self.selectSw)
            deleteSwButton.bind(on_release=self.stageDelete)

            dbEntryLayout.add_widget(selectSwButton)
            dbEntryLayout.add_widget(deleteSwButton)

            dbGrid.add_widget(dbEntryLayout)

        sv.add_widget(dbGrid)

        backButton = WriteButton(text="Back")
        backButton.bind(on_release=self.goBack)

        deleteButton = CancelButton(text="", disabled=True, opacity=0)
        deleteButton.bind(on_release=self.commitDelete)
        self.deleteButtonRef = deleteButton

        bottomLayout.add_widget(backButton)
        bottomLayout.add_widget(deleteButton)

        mainPopLayout.add_widget(titleLabel)
        mainPopLayout.add_widget(sv)
        mainPopLayout.add_widget(bottomLayout)

        self.content = mainPopLayout

class MeasurementsPopup(PopupBase):
    def __init__(self, **kwargs):
        self.mainLayout = kwargs.get("mainLayout", None)
        super().__init__()

    def submit(self):
        envText = self.ids.envText.text
        envCorrectionsText = self.ids.envCorrectionsText.text
        balanceReadingsText = self.ids.balanceReadingsText.text

        envOrder = self.ids.envText.orderNum
        envCorrectionsOrder = self.ids.envCorrectionsText.orderNum
        balanceReadingsOrder = self.ids.balanceReadingsText.orderNum

        if(envText == "" or envCorrectionsText == "" or balanceReadingsText == ""):
            self.ids.measurementsPopError.text = "Enter data for all fields"
            return

        #Check if Num lines are the same for measurements and environmental data
        numBalReadings = 0
        numEnvReadings = 0

        for line in balanceReadingsText.splitlines():
            if(line == "" or line == "\n"):
                pass
            else:
                numBalReadings += 1

        for line in envText.splitlines():
            if(line == "" or line == "\n"):
                pass
            else:
                numEnvReadings += 1

        if(numBalReadings != numEnvReadings):
            self.ids.measurementsPopError.text = str(numBalReadings) + " lines of environmentals required, " + str(numEnvReadings) + " provided"
            return

        self.mainLayout.removeLines(["<Environmentals>", "<Env-Corrections>", "<Balance-Reading>"])

        rowStart1, rowEnd1 = self.mainLayout.writeText(envText, envOrder)
        rowStart2, rowEnd2 = self.mainLayout.writeText(envCorrectionsText, envCorrectionsOrder)
        rowStart3, rowEnd3 = self.mainLayout.writeText(balanceReadingsText, balanceReadingsOrder)

        self.mainLayout.highlight(rowStart1, rowEnd3)

        self.dismiss()

    def autoFill(self):
        try:
            envs = self.ids.envText.text.splitlines()[0]
            linesNeeded = len(self.ids.balanceReadingsText.text.splitlines())
            if linesNeeded == 0: return

            envsArray = []
            for i in range(linesNeeded):
                envsArray.append(envs)
            
            self.ids.envText.text = "\n".join(envsArray)
        except IndexError:
            pass

class GravityPopup(PopupBase):
    def __init__(self, **kwargs):
        self.mainLayout = kwargs.get("mainLayout", None)
        super().__init__()
        self.bind(on_open=self.setWeightIds)

    def submit(self):
        gradientText = self.ids.gradientText.text
        localGravText = self.ids.localGravityText.text
        heightText = self.ids.heightText.text

        gradientOrder = self.ids.gradientText.orderNum
        localGravOrder = self.ids.localGravityText.orderNum
        heightOrder = self.ids.heightText.orderNum

        if(gradientText == "" or heightText == "" or localGravText == ""):
            self.ids.gravityPopError.text = "Enter data for all fields"
            return

        self.mainLayout.removeLines(["<Gravity-Grad>", "<Gravity-Local>", "<Height>"])

        rowStart1, rowEnd1 = self.mainLayout.writeText(gradientText, gradientOrder)
        rowStart2, rowEnd2 = self.mainLayout.writeText(localGravText, localGravOrder)
        rowStart3, rowEnd3 = self.mainLayout.writeText(heightText, heightOrder)

        self.mainLayout.highlight(rowStart1, rowEnd3)
        self.dismiss()

    def setWeightIds(self, e):
        ids = []
        userText = self.mainLayout.ids.userText.text
        for line in userText.splitlines():
            if(line.split() == []):
                continue
            if(line.split()[0] == "<Position>"):
                ids.append(line.split()[1])

        self.ids.gravityWeightIds.text = "\n".join(ids)

    def getUserFontSize(self):
        try:
            return dp(API.getFontSize())
        except:
            return dp(12)

class OpenFilePopup(Popup):
    def __init__(self, **kwargs):
        super().__init__()
        self.mainLayout = kwargs.get("mainLayout", None)

    def openFile(self, selection):
        try:
            selection[0]
            fileName = path.split(selection[0])[1]
            if(not "-config.txt" in fileName):
                self.mainLayout.sendError("NO FILE SELECTED")
                self.dismiss()
                return
        except IndexError:
            self.mainLayout.sendError("NO FILE SELECTED")
            self.dismiss()
            return

        try:
            with open(selection[0]) as configFile:
                fileText = configFile.read()
        except:
            self.mainLayout.sendError("ERROR OPENING SELECTED FILE " + selection[0])
            self.dismiss()
            return

        basePath = selection[0][: len(selection[0]) - 11]

        self.mainLayout.fileName = fileName[: len(fileName) - 11]
        self.mainLayout.configFilePath = selection[0]
        self.mainLayout.outFilePath = basePath + "-out.txt"
        self.mainLayout.notesFilePath = basePath + "-notes.txt"

        self.mainLayout.splitSeries(fileText)
        self.mainLayout.grabOutputFile()
        self.mainLayout.grabNotes()

        self.mainLayout.ids.configFileName.text = path.split(selection[0])[1]

        self.dismiss()

    def getDefaultPath(self):
        try:
            filePath = API.getDefaultPath()
            return filePath
        except:
            return path.abspath(getcwd())

class OpenNewFilePopup(Popup):
    def __init__(self, **kwargs):
        super().__init__()
        self.mainLayout = kwargs.get("mainLayout", None)

    def setMessage(self, newFile):
        seriesNum = self.mainLayout.currentSeries

        if(seriesNum != None):
            self.mainLayout.seriesTexts[seriesNum - 1] = self.mainLayout.ids.userText.text

        self.ids.newFileMessage.text = "Opening new file without saving?"
        self.ids.openNewFileButton.text = "Back"
        self.ids.cancelNewFileButton.text = "Don't Save\n& Open"
        if(newFile == True):
            self.ids.openNewFileButton.bind(on_release=self.dismiss)
            self.ids.cancelNewFileButton.bind(on_release=self.openNewFileNoSave)
        else:
            self.ids.openNewFileButton.bind(on_release=self.dismiss)
            self.ids.cancelNewFileButton.bind(on_release=self.openFileSearchNoSave)

    def openFileSearchNoSave(self, e):
        fileSearchPop = OpenFilePopup(mainLayout=self.mainLayout)
        self.dismiss()
        fileSearchPop.open()

    def openNewFileNoSave(self, e):
        fileSavePop = NewFileSaveLocPopup(mainLayout=self.mainLayout)
        self.dismiss()
        fileSavePop.open()

class NewFileSaveLocPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__()
        self.mainLayout = kwargs.get("mainLayout", None)

    def setSaveLoc(self, filePath, fileNameInput):
        configFilePath = path.join(filePath, fileNameInput.strip() + "-config.txt")
        outFilePath = path.join(filePath, fileNameInput.strip() + "-out.txt")
        notesFilePath = path.join(filePath, fileNameInput.strip() + "-notes.txt")

        if(fileNameInput.strip() == ""):
            self.ids.saveFileMessage.text = "Please provide a file name"
            return

        if(path.exists(configFilePath)):
            self.ids.saveFileMessage.text = fileNameInput.strip() + "-config.txt" + " already exists in this folder"
            return

        if(self.mainLayout.configFilePath == ""):
            self.mainLayout.fileName = fileNameInput.strip()
            self.mainLayout.configFilePath = configFilePath
            self.mainLayout.outFilePath = outFilePath
            self.mainLayout.notesFilePath = notesFilePath

            self.mainLayout.save()
            self.mainLayout.ids.configFileName.text = path.split(configFilePath)[1]
            self.dismiss()

        else:
            self.mainLayout.fileName = fileNameInput.strip()
            self.mainLayout.configFilePath = configFilePath
            self.mainLayout.outFilePath = outFilePath
            self.mainLayout.notesFilePath = notesFilePath

            #Reset output file, notes, and usertext
            self.mainLayout.grabOutputFile()
            self.mainLayout.grabNotes()
            self.mainLayout.splitSeries("@SERIES\n\n")

            self.mainLayout.save()
            self.mainLayout.ids.configFileName.text = path.split(configFilePath)[1]
            self.dismiss()

    def getDefaultPath(self):
        try:
            filePath = API.getDefaultPath()
            return filePath
        except:
            return path.abspath(getcwd())

class ValidationPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__()
        self.bind(on_open=self.runTestThread)

    def runTestThread(self, e):
        Thread(target=self.runTestSuite).start()

    def runTestSuite(self):
        self.ids.testingMessage.text = "Running Tests..."
        self.ids.validationText.text = ""

        #Run tests from RunTest.TestSuite class
        testSuite = TestSuite.TestSuite()
        results = testSuite.runAll()

        self.ids.validationText.text = results
        self.ids.testingMessage.text = ""
        return

class VisualizationPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__()
        self.size_hint = (0.9, 0.9)
        self.series = 1
        self.title = "Data Visualization"
        self.auto_dismiss = False
        self.deltas = kwargs.get("deltas", [])
        self.sensitivities = kwargs.get("sensitivities", [])
        self.temperatures = kwargs.get("temperatures", [])
        self.sws = kwargs.get("sws", 0)
        self.reportNum = kwargs.get("reportNum", "")
        self.nominals = kwargs.get("nominals", [])

    def goBack(self, inst):
        closeFigures()
        self.dismiss()

    def gotoNext(self, inst):
        if(self.series < len(self.deltas)):
            self.series += 1
            closeFigures()
            self.buildVisPop()
    
    def gotoPrev(self, inst):
        if(self.series > 1):
            self.series -= 1
            closeFigures()
            self.buildVisPop()

    def adjustSpacing(self, inst, value):
        inst.spacing = value / 2 - dp(290)

    def buildVisPop(self):
        self.title = "Data Visualization Dashboard"

        try:
            nominal = " - " + self.nominals[self.series - 1]
        except:
            nominal = ""

        mainPopLayout = BoxLayout(orientation="vertical", spacing=dp(12), padding=(dp(10), dp(10)))
        graphLayout = BoxLayout(orientation="horizontal", spacing=dp(10))
        barGraphLayout = BoxLayout(orientation="vertical", spacing=dp(10))
        bottomLayout = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(50))
        navLayout = BoxLayout(orientation="horizontal", size_hint=(None, 1), width=dp(300))

        try:
            deltaPlot = FigureCanvasKivyAgg(plotDeltas(self.deltas[self.series - 1], self.sws[self.series - 1], dp(9)))
        except:
            deltaPlot = Label(text="Delta Plot: No Data")

        try:
            sensitivityPlot = FigureCanvasKivyAgg(plotSensitivities(self.sensitivities[self.series - 1], dp(9)))
        except:
            sensitivityPlot = Label(text="Sensitivity Plot: No Data")

        try:
            scatter = FigureCanvasKivyAgg(plotScatter(self.sensitivities[self.series - 1], self.deltas[self.series - 1], self.temperatures[self.series - 1], dp(9), dp(120)))
        except:
            scatter = Label(text="Scatter Plot: No Data")

        backButton = WriteButton(text="Back")
        backButton.bind(on_release=self.goBack)

        seriesLabel = Label(text="Series " + str(self.series) + nominal, size_hint=(None, 1), width=dp(200), halign='center')
        nextSeries = Button(text=">", size_hint=(None, 1), width=dp(40), background_normal='', background_color = (0.99, 0.99, 0.99, 0.5), font_size=dp(24))
        prevSeries = Button(text="<", size_hint=(None, 1), width=dp(40), background_normal='', background_color = (0.99, 0.99, 0.99, 0.5), font_size=dp(24))

        nextSeries.bind(on_release=self.gotoNext)
        prevSeries.bind(on_release=self.gotoPrev)

        navLayout.add_widget(prevSeries)
        navLayout.add_widget(seriesLabel)
        navLayout.add_widget(nextSeries)

        bottomLayout.add_widget(backButton)
        bottomLayout.add_widget(navLayout)
        bottomLayout.bind(width=self.adjustSpacing)

        barGraphLayout.add_widget(deltaPlot)
        barGraphLayout.add_widget(sensitivityPlot)

        graphLayout.add_widget(barGraphLayout)
        graphLayout.add_widget(scatter)
        mainPopLayout.add_widget(graphLayout)
        mainPopLayout.add_widget(bottomLayout)

        self.content = mainPopLayout

class SettingsPopup(PopupBase):
    def __init__(self, **kwargs):
        super().__init__()
        self.mainLayout = kwargs.get("mainLayout", None)

    def getFontSize(self):
        try:
            fontSize = str(API.getFontSize())
            return fontSize
        except:
            return "12"

    def getDefaultPath(self):
        try:
            filePath = API.getDefaultPath()
            return filePath
        except:
            return path.abspath(getcwd())

    def chooseDefaultPath(self):
        pathPopup = DefaultPathPopup(self)
        pathPopup.open()

    def saveSettings(self):
        fontSize = self.ids.fontSize.text.strip()
        filePath = self.ids.filePath.text.strip()
        runTests = 1 if self.ids.testsCheckBox.active else 0
        writeNotes = 1 if self.ids.notesCheckBox.active else 0

        if(fontSize == ""):
            self.ids.settingsError.text = "Please enter a font size"
            return

        try:
            int(fontSize)
        except:
            self.ids.settingsError.text = "Please enter a numerical font size"
            return

        if(filePath == ""):
            self.ids.settingsError.text = "Please enter a file path"
            return

        API.saveSettings(int(fontSize), filePath, runTests, writeNotes)

        self.mainLayout.ids.userText.font_size = dp(int(fontSize))
        self.mainLayout.ids.notesText.font_size = dp(int(fontSize))
        self.mainLayout.ids.errors.font_size = dp(int(fontSize))
        self.dismiss()

class DefaultPathPopup(Popup):
    def __init__(self, rootPop):
        super().__init__()
        self.rootPop = rootPop

    def setDefaultPath(self, filePath):
        self.rootPop.ids.filePath.text = filePath
        self.dismiss()

    def getDefaultPath(self):
        try:
            filePath = API.getDefaultPath()
            return filePath
        except:
            return path.abspath(getcwd())

class StartupTestsPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__()
        self.bind(on_open=self.runTestThread)

    def runTestThread(self, *args):
        Thread(target=self.runStartupTests).start()

    def runStartupTests(self):
        #start = time.time()
        testSuite = TestSuite.TestSuite()
        testSuite.runAll()
        #end = time.time()
        #print(str((end - start)*1000) + " ms")

        if(testSuite.failed == 0):
            self.dismiss()
        else:
            self.ids.testStatus.color = (0.95, 0.15, 0.15, 0.95)
            self.ids.testStatus.text = "[b]" + str(testSuite.failed) + " INTERNAL TESTING FAILURE/S. OPEN LOGS TO SEE DETAILS[/b]"
            self.ids.openLogButton.bind(on_release=self.openTestLog)
            self.ids.openLogButton.background_color = Configs.inputButtonColor

        return

    def openTestLog(self, e):
        testLogPop = ValidationPopup()
        self.dismiss()
        testLogPop.open()

class RequestClosePopUp(Popup):
    pass

class StartupTestsCheckBox(CheckBox):
    def getStartupTestsValue(self):
        if(API.getRunInternalTests() == 1):
            return True
        else:
            return False

class NotesCheckBox(CheckBox):
    def getNotesValue(self):
        if(API.getWriteNotes() == 1):
            return True
        else:
            return False

class CreateInputCheckBox(CheckBox):
    def getInputBoolean(self, userText, tag):
        for line in userText.splitlines():
            if(tag in line):
                if(line.split(tag)[1].strip() == "1"):
                    return True
                else:
                    return False
        
        return False

    def getNotInputBoolean(self, userText, tag):
        for line in userText.splitlines():
            if(tag in line):
                if(line.split(tag)[1].strip() == "0"):
                    return True
                else:
                    return False
        
        return False

class Mars(App):
    def build(self):
        Builder.load_file('Mars-FE.kv')
        Config.set('input', 'mouse', 'mouse,disable_multitouch')
        Config.set('graphics', 'fullscreen', 0)
        Config.set('graphics', 'window_state', 'maximized')
        Config.write()

        Window.bind(on_request_close=self.on_request_close)
        return MainLayout()

    def on_start(self):
        if(API.getRunInternalTests() == 1):
            Clock.schedule_once(self.openStartTests, 0)

    def openStartTests(self, dt):
        startTestsPop = StartupTestsPopup()
        startTestsPop.open()

    def on_request_close(self, *args):
        if(self.root.saved == False):
            pop = RequestClosePopUp()
            pop.open()
            return True
        else:
            Window.close()
            return

    def closeApp(self):
        Window.close()

    def openLabInfoPop(self):
        if(self.root.currentSeries == 1):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = LabInfoPopup(mainLayout=self.root)
                pop.open()

    def openRestraintPop(self):
        if(self.root.currentSeries == 1):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)
            
            if(checkOK):
                self.root.clearErrors()
                pop = RestraintPopup(mainLayout=self.root)
                pop.open()

    def openDatePop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)
            
            if(checkOK):
                self.root.clearErrors()
                pop = DatePopup(mainLayout=self.root)
                pop.open()

    def openDesignPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)
            
            if(checkOK):
                self.root.clearErrors()
                pop = DesignPopup(mainLayout=self.root)
                pop.open()
                pop.ids.dropDownn.dismiss()

    def openWeightsPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = WeightsPopup(mainLayout=self.root)
                pop.open()

    def openVectorsPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = VectorsPopup(mainLayout=self.root)
                pop.open()

    def openStatisticsPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = StatisticsPopup(mainLayout=self.root)
                pop.open()

    def openSwPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = SwPopup(mainLayout=self.root)
                pop.open()

    def openMeasurementsPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = MeasurementsPopup(mainLayout=self.root)
                pop.open()

    def openGravityPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = GravityPopup(mainLayout=self.root)
                pop.open()

    def openFilePop(self):
        freshOpen = self.root.numberOfSeries == 1 and self.root.ids.userText.text.strip() == "@SERIES"
        if(self.root.saved == False and freshOpen == False):
            self.root.clearErrors()
            pop = OpenNewFilePopup(mainLayout=self.root)
            pop.open()
            pop.setMessage(False)
        else:
            self.root.clearErrors()
            pop = OpenFilePopup(mainLayout=self.root)
            pop.open()

    def openNewFilePop(self):
        freshOpen = self.root.numberOfSeries == 1 and self.root.ids.userText.text.strip() == "@SERIES"
        if(self.root.saved == False and freshOpen == False):
            self.root.clearErrors()
            pop = OpenNewFilePopup(mainLayout=self.root)
            pop.open()
            pop.setMessage(True)
        else:
            self.root.clearErrors()
            saveLocPop = NewFileSaveLocPopup(mainLayout=self.root)
            saveLocPop.open()

    def openValidationPop(self):
        pop = ValidationPopup()
        pop.open()

    def openVisualizationPop(self):
        try:
            with open(self.root.outFilePath, 'r') as f:
                fileText = f.read()
        except:
            fileText = ""

        try:
            deltas = getDeltas(fileText)
        except:
            deltas = []

        try:
            sws = getSws(fileText)
        except:
            sws = []

        try:
            sensitivities = getSensitivities(fileText)
        except:
            sensitivities = []

        try:
            temperatures = getTemperatures(fileText)
        except:
            temperatures = []

        try:
            nominals = getNominals(fileText)
        except:
            nominals = []

        pop = VisualizationPopup(deltas=deltas, sensitivities=sensitivities, temperatures=temperatures, sws=sws, reportNum=self.root.reportNum, nominals=nominals)
        pop.buildVisPop()
        pop.open()

    def openSettingPop(self):
        pop = SettingsPopup(mainLayout=self.root)
        pop.open()

if(__name__ == "__main__"):
    try:
        API.getSettings()
    except:
        API.saveSettings(12, path.abspath(getcwd()), 1, 0)

    mainApp = Mars()
    mainApp.run()