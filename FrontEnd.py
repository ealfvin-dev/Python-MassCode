import kivy

from kivy.config import Config

Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('graphics', 'fullscreen', 0)
Config.set('graphics', 'window_state', 'maximized')
Config.write()

from kivy.graphics import Color, Rectangle, Line
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp

from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image

import RunFile
import TestSuite
import InputChecks
import API
from MARSException import MARSException

import sys
import os
import threading

import time

class MainLayout(BoxLayout):
    reportNum = ""
    numberOfSeries = 1
    currentSeries = 1
    seriesTexts = ["@SERIES\n\n"]
    outputText = ""

    def __init__(self, **kwargs):
        super().__init__()

        with self.canvas.before:
            Color(rgba=(231/255, 234/255, 236/255, 1))
            #Color(0.936, 0.938, 0.946, 1)
            self.backgroundRect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)
        self.saved = False

        self.orderOfTags = {"#": 0, \
            "<Report-Number>": 1, \
            "<Restraint-ID>": 2, \
            "<Unc-Restraint>": 3, \
            "<Random-Error>": 4, \
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
            "<Sigma-t>": 23, \
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

        row = -1
        textInput.cursor = (0, 0)
        cursorStart = 0

        #Move cursor to the appropriate position
        for line in textInput.text.splitlines():
            row += 1

            if(line.strip() == ""):
                textInput.cursor = (len(line), row)
                cursorStart += len(line)
                cursorStart += 1
            elif(line == "\n"):
                textInput.cursor = (0, row)
                cursorStart += 1
            elif(line.strip()[0] == "#"):
                textInput.cursor = (len(line), row)
                cursorStart += len(line)
                cursorStart += 1
            elif(orderNum < self.orderOfTags[line.strip().split()[0]]):
                break
            else:
                textInput.cursor = (len(line), row)

                cursorStart += len(line)
                cursorStart += 1

        #Insert text and record length for highlighting
        textBlockLength = 0

        if(textInput.cursor == (0, 0)):
            textInput.insert_text("\n")
            textInput.cursor = (0, 0)
        else:
            textInput.insert_text("\n")

        for line in text.splitlines():
            if(line == "" or line == "\n"):
                textInput.insert_text("\n")
                textBlockLength += 1
            else:
                if(orderNum != 0 and orderNum != 5):
                    newLine = " " * (19 - len(self.getTag(orderNum)))
                else:
                    newLine = ""

                newLine += self.getTag(orderNum) + "  " + line
                textInput.insert_text(newLine)
                textBlockLength += len(newLine)

                if(len(text.splitlines()) > 1):
                    textInput.insert_text("\n")
                    textBlockLength += 1

                if(orderNum == 1 or orderNum == 4 or orderNum == 10 or orderNum == 21 or orderNum == 23 or orderNum == 26 or orderNum == 28):
                    textInput.insert_text("\n")

        return cursorStart, textBlockLength

    def getTag(self, orderNum):
        for tag, order in self.orderOfTags.items():
            if(order == orderNum):
                return tag

    def highlight(self, startPos, textLength):
        self.ids.userText.select_text(startPos, startPos + textLength)
        self.ids.userText.selection_color = (0.1, 0.8, 0.2, 0.20)

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
        self.ids.userText.selection_color = (0.9, 0.05, 0.1, 0.28)
        self.ids.userText.select_text(startPosition, endPosition)

    def textAdded(self, cursor_row):
        if(self.saved):
            self.saved = False
            self.ids.runButton.colorGrey()
            self.ids.saveButton.colorBlue()

        if(self.currentSeries == 1):
            self.getReportNum(self.ids.userText.text)

    def getReportNum(self, text=None):
        if(text == None): text = self.seriesTexts[0]

        for line in text.splitlines():
            if(line.split() == []):
                continue

            if(line.split()[0] == "<Report-Number>"):
                try:
                    self.reportNum = line.split()[1]
                    self.ids.configFileName.text = line.split()[1] + "-config.txt"
                    return line.split()[1]
                except IndexError:
                    self.reportNum = ""
                    self.ids.configFileName.text = ""
                    return False

        self.reportNum = ""
        self.ids.configFileName.text = ""
        return False

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
            "<Random-Error>": False, \
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
            "<Sigma-t>": False, \
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

        #Lab Info Button
        if(self.currentSeries == 1 and tags["<Report-Number>"] == False):
            self.ids.labInfoButton.colorBlue()
        else:
            self.ids.labInfoButton.colorGrey()

        #Restraint Button
        if(self.currentSeries == 1 and (tags["<Restraint-ID>"] == False or tags["<Unc-Restraint>"] == False or tags["<Random-Error>"] == False)):
            self.ids.restraintButton.colorBlue()
        else:
            self.ids.restraintButton.colorGrey()

        #Date Button
        if(tags["<Date>"] and tags["<Technician-ID>"] and tags["<Balance-ID>"] and tags["<Direct-Readings>"] and tags["<Direct-Reading-SF>"]):
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
        if(tags["<Sigma-t>"] and tags["<Sigma-w>"]):
            self.ids.statisticsButton.colorGrey()
        else:
            self.ids.statisticsButton.colorBlue()

        #Sensitivity Weight Button
        if((tags["<sw-Mass>"] and tags["<sw-Density>"] and tags["<sw-CCE>"]) or InputChecks.determineIfDirectReadings(seriesText)):
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

    def addSeries(self):
        if(self.numberOfSeries == 13):
            return

        self.numberOfSeries += 1

        newSeriesId = "series" + str(self.numberOfSeries)
        self.ids[newSeriesId].text = "[color=#FFFFFF]Series " + str(self.numberOfSeries) +"[/color]"
        self.ids[newSeriesId].exists = True

        self.seriesTexts.append("@SERIES\n\n")

        if(self.saved):
            self.saved = False
            self.ids.runButton.colorGrey()
            self.ids.saveButton.colorBlue()

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
            for sn in range(1, 14):
                seriesID = "series" + str(sn)
                self.ids[seriesID].background_color = (0.155, 0.217, 0.292, 0.65)

                if(self.ids[seriesID].exists):
                    self.ids[seriesID].text = "[color=#FFFFFF]" + self.ids[seriesID].text[15:]

            self.ids.outputFileTab.background_color = (0.155, 0.217, 0.292, 0.65)
            if(self.ids.outputFileTab.exists):
                self.ids.outputFileTab.text = "[color=#FFFFFF]" + self.ids.outputFileTab.text[15:]

            targetButton = self.ids["series" + str(seriesNum)]
            targetButton.background_color = (0.906, 0.918, 0.926, 1)
            targetButton.text = "[color=#000000]" + targetButton.text[15:]

            self.getReportNum()
            self.renderButtons(self.ids.userText.text)

    def removeLastSeries(self):
        if(self.numberOfSeries == 1):
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
        self.getReportNum()
        self.grabOutputFile()

    def save(self):
        #If in the output tab, return
        if(self.currentSeries == None):
            return

        #Save current working series Text into self.seriesTexts array
        self.seriesTexts[self.currentSeries - 1] = self.ids.userText.text

        #Run tests to check the provided report number before saving
        reportNum = self.getReportNum()
        if(reportNum == False):
            self.sendError("NO REPORT NUMBER PROVIDED IN SERIES 1, CANNOT SAVE")
            self.goToSeries(1, True)
            return

        checkReportNum = InputChecks.checkReportNumber(self.seriesTexts[0], self.sendError, self.highlightError)
        if(checkReportNum == False):
            return

        self.displaySeriesNominal(self.seriesTexts[self.currentSeries - 1], self.ids["series" + str(self.currentSeries)])
        
        fileText = ""
        for seriesText in self.seriesTexts:
            fileText += seriesText.strip()
            fileText += "\n\n"

        f = open(reportNum + "-config.txt", 'w')
        f.write(fileText)
        f.close()

        self.saved = True
        self.sendSuccess("FILE SAVED AS " + str(self.reportNum) + "-config.txt")

        self.renderButtons(self.ids.userText.text)
        self.ids.runButton.colorBlue()
        self.ids.saveButton.colorGrey()

    def run(self):
        #Perform checks to make sure the input file is in a runnable state
        #######################
        start = time.time()
        if(self.currentSeries == None):
            return

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

        requiredChecks = InputChecks.runRequiredChecks(self.seriesTexts, self.numberOfSeries, self.sendError, self.highlightError, self.goToSeries)
        if(not requiredChecks):
            return
        #######################
        self.clearErrors()

        try:
            results = RunFile.run(self.reportNum + "-config.txt")
            self.grabOutputFile()
            self.sendSuccess("FILE SUCCESSFULLY RUN\nOUTPUT SAVED AS " + str(self.reportNum) + "-out.txt")

            secondaryChecks = InputChecks.runSecondaryChecks(self.seriesTexts, self.reportNum, self.sendError, self.highlightError)
            if(secondaryChecks):
                InputChecks.checkResults(results)

        except MARSException as ex:
            self.sendError("RUNTIME ERROR: " + str(ex))
        except AssertionError:
            self.sendError("REQUIRED PYTHON 3.5 OR LATER")
        except:
            self.sendError("UNCAUGHT ERROR RUNNING INPUT FILE. CHECK INPUT")

        end = time.time()
        print(str((end - start)*1000) + " ms")

    def sendError(self, message):
        self.ids.errors.foreground_color = (0.9, 0.05, 0.05, 0.85)
        self.ids.errors.text = "ERROR:\n" + message

    def sendSuccess(self, message):
        self.ids.errors.foreground_color = (0.05, 0.65, 0.1, 0.98)
        self.ids.errors.text = message

    def clearErrors(self):
        self.ids.errors.text = ""

    def grabOutputFile(self):
        outFile = self.reportNum + "-out.txt"

        if(os.path.exists(outFile)):
            self.outputText = ""
            f = open(outFile, 'r')
            for line in f:
                self.outputText += line
            
            #Render output button/tab
            self.ids.outputFileTab.text = "[color=#FFFFFF][b]Output[/b][/color]"
            self.ids.outputFileTab.exists = True
        else:
            self.ids.outputFileTab.text = ""
            self.ids.outputFileTab.exists = False
            self.outputText = ""

    def openOutputFile(self, thisButton):
        if(thisButton.exists):
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

            for sn in range(1, 14):
                seriesID = "series" + str(sn)
                self.ids[seriesID].background_color = (0.155, 0.217, 0.292, 0.65)

                if(self.ids[seriesID].exists):
                    self.ids[seriesID].text = "[color=#FFFFFF]" + self.ids[seriesID].text[15:]

            thisButton.background_color = (0.906, 0.918, 0.926, 1)
            thisButton.text = "[color=#000000]" + thisButton.text[15:]

            self.greyOutButtons()

class OrderedText(TextInput):
    def __init__(self, **kwargs):
        super().__init__()

        with self.canvas.before:
            Color(rgba=(0.155, 0.217, 0.292, 0.65))
            self.borderRect = Rectangle(size=(self.size[0] + dp(2), self.size[1] + dp(2)), pos=(self.pos[0] - dp(1), self.pos[1] - dp(1)))
        
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.font_name = "./Menlo.ttc"
        self.text = ""
        self.orderNum = 0
        self.background_normal = ''
        self.font_size = dp(13)
        self.write_tab = False
        self.multiline = False
        self.padding = [dp(5), dp(5), dp(5), dp(5)]

    def _update_rect(self, instance, value):
        self.borderRect.pos = (instance.pos[0] - dp(1), instance.pos[1] - dp(1))
        self.borderRect.size = (instance.size[0] + dp(2), instance.size[1] + dp(2))

class UserInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__()

        with self.canvas.before:
            Color(rgba=(0.155, 0.217, 0.292, 0.65))
            self.borderRect = Rectangle(size=(self.size[0] + dp(2), self.size[1] + dp(2)), pos=(self.pos[0] - dp(1), self.pos[1] - dp(1)))
        
        self.bind(size=self._update_rect, pos=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.borderRect.pos = (instance.pos[0] - dp(1), instance.pos[1] - dp(1))
        self.borderRect.size = (instance.size[0] + dp(2), instance.size[1] + dp(2))

class ExtraButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.background_normal = ''
        self.color = (0, 0, 0, 1)
        self.background_color = (0.99, 0.99, 0.99, 0.98)
        self.font_size = dp(15)

        with self.canvas.before:
            Color(rgba=(0.155, 0.217, 0.292, 0.65))
            self.borderRect = Rectangle(size=(self.size[0] + dp(2), self.size[1] + dp(2)), pos=(self.pos[0] - dp(1), self.pos[1] - dp(1)))
        
        self.bind(size=self._update_rect, pos=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.borderRect.pos = (instance.pos[0] - dp(1), instance.pos[1] - dp(1))
        self.borderRect.size = (instance.size[0] + dp(2), instance.size[1] + dp(2))

class SeriesButton(Button):
    def __init__(self, **kwargs):
        super().__init__()

        self.seriesNum = 0
        self.exists = False
        self.text = ''
        self.markup = True
        self.halign = 'center'
        self.background_normal = ''
        self.background_color = (0.155, 0.217, 0.292, 0.65)
        self.background_down =  ''

class TopMenuButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.halign = 'center'
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0.155, 0.217, 0.292, 0.65)

        self.bind(state=self._updateState)

    def _updateState(self, instance, value):
        if(value == "down"):
            self.background_color = (0.155*0.3, 0.217*0.3, 0.292*0.3, 0.65)
        elif(value == "normal"):
            self.background_color = (0.155, 0.217, 0.292, 0.65)

class InputButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.buttonColor = (0.13, 0.5, 0.95, 0.94)
        self.currentColor = self.buttonColor
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.markup = True
        self.halign = 'center'

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
        self.currentColor = (0.62, 0.62, 0.62, 0.62)
        self.canvasColor.rgba = self.currentColor

    def colorBlue(self, *args):
        self.currentColor = self.buttonColor
        self.canvasColor.rgba = self.currentColor

class SaveButton(InputButton):
    pass

class RunButton(InputButton):
    def initialize(self):
        Clock.schedule_once(self.colorGrey, 0)

class CancelButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.size_hint = (None, None)
        self.size = (dp(150), dp(45))
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0.70, 0.135, 0.05, 0.92)
        self.font_size = dp(16)
        self.text = "Cancel"
        self.halign = 'center'

        self.bind(state=self._updateState)

    def _updateState(self, instance, value):
        if(value == "down"):
            self.background_color = (0.70*0.6, 0.135*0.6, 0.05*0.6, 0.92)
        elif(value == "normal"):
            self.background_color = (0.70, 0.135, 0.05, 0.92)

class WriteButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.size_hint = (None, None)
        self.size = (dp(150), dp(45))
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0.13, 0.5, 0.95, 0.94)
        self.font_size = dp(16)
        self.text = "Write"
        self.halign = 'center'

        self.bind(state=self._updateState)

    def _updateState(self, instance, value):
        if(value == "down"):
            self.background_color = (0.13*0.5, 0.5*0.5, 0.95*0.5, 0.94)
        elif(value == "normal"):
            self.background_color = (0.13, 0.5, 0.95, 0.94)

class AddSeriesButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.markup = True
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0.00, 0.76, 0.525, 1)
        self.text = "[b]+[/b] Add Series"
        self.halign = 'center'

        self.bind(state=self._updateState)

    def _updateState(self, instance, value):
        if(value == "down"):
            self.background_color = (0.00*0.68, 0.76*0.68, 0.525*0.68, 1)
        elif(value == "normal"):
            self.background_color = (0.00, 0.76, 0.525, 1)

class RemoveSeriesButton(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.markup = True
        self.background_normal = ''
        self.background_down = ''
        self.halign = 'center'
        self.text = "[b]-[/b] Remove\nLast Series"
        self.background_color = (0.70, 0.135, 0.05, 0.92)

        self.bind(state=self._updateState)

    def _updateState(self, instance, value):
        if(value == "down"):
            self.background_color = (0.70*0.6, 0.135*0.6, 0.05*0.6, 0.92)
        elif(value == "normal"):
            self.background_color = (0.70, 0.135, 0.05, 0.92)

class PopupBase(Popup):
    def __init__(self, **kwargs):
        super().__init__()
        self.background = './Popup_Background.png'
        self.title_color = (0, 0, 0, 1)
        self.title_size = dp(18)
        self.size_hint = (None, None)

class PopupLabel(Label):
    def __init__(self, **kwargs):
        super().__init__()
        self.markup = True
        self.halign = "left"
        self.valign = "bottom"
        self.color = (0.095, 0.095, 0.096, 0.9)
        self.font_size = dp(15)

class LabInfoPopup(PopupBase):
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
        cursorStart1, textLength1 = self.parent.children[1].writeText(labInfoText, labInfoOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(reportNumText, reportNumOrder)

        #Highlight the block added across total textLength. Add 1 because there is one extra line break character between sections
        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + 1)

        self.parent.children[1].ids.labInfoButton.colorGrey()
        self.parent.children[1].getReportNum(text=self.parent.children[1].ids.userText.text)

        self.dismiss()

class RestraintPopup(PopupBase):
    def submit(self):
        restraintIDText = self.ids.restraintIDText.text
        restraintUncertaintyText = self.ids.restraintUncertaintyText.text
        randomErrorText = self.ids.randomErrorText.text

        restraintIDOrder = self.ids.restraintIDText.orderNum
        restraintUncertaintyOrder = self.ids.restraintUncertaintyText.orderNum
        randomErrorOrder = self.ids.randomErrorText.orderNum

        if(restraintIDText == "" or restraintUncertaintyText == "" or randomErrorText == ""):
            self.ids.restraintPopError.text = "Enter data for all fields"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(restraintIDText, restraintIDOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(restraintUncertaintyText, restraintUncertaintyOrder)
        cursorStart3, textLength3 = self.parent.children[1].writeText(randomErrorText, randomErrorOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + textLength3 + 2)
        self.parent.children[1].ids.restraintButton.colorGrey()

        self.dismiss()

class DatePopup(PopupBase):
    def submit(self):
        dateText = self.ids.dateText.text
        techIDText = self.ids.techIDText.text
        balanceIDText = self.ids.balanceIDText.text
        directReadingsText = self.ids.directReadingsText.text
        directReadingsSFText = self.ids.directReadingsSFText.text

        dateOrder = self.ids.dateText.orderNum
        techIDOrder = self.ids.techIDText.orderNum
        balanceOrder = self.ids.balanceIDText.orderNum
        directReadingsOrder = self.ids.directReadingsText.orderNum
        directReadingsSFOrder = self.ids.directReadingsSFText.orderNum

        if(dateText == "" or techIDText == "" or balanceIDText == "" or directReadingsText == "" or directReadingsSFText == ""):
            self.ids.datePopError.text = "Enter data for all fields"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(dateText, dateOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(techIDText, techIDOrder)
        cursorStart3, textLength3 = self.parent.children[1].writeText(balanceIDText, balanceOrder)
        cursorStart4, textLength4 = self.parent.children[1].writeText(directReadingsText, directReadingsOrder)
        cursorStart5, textLength5 = self.parent.children[1].writeText(directReadingsSFText, directReadingsSFOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + textLength3 + textLength4 + textLength5 + 4)
        self.parent.children[1].ids.dateButton.colorGrey()

        self.dismiss()

class DesignPopup(PopupBase):
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

        cursorStart1, textLength1 = self.parent.children[1].writeText(designIDText, designIDOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(designText, designOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + 1)
        self.parent.children[1].ids.designButton.colorGrey()

        self.dismiss()

class WeightsPopup(PopupBase):
    def submit(self):
        checkIDText = self.ids.checkIDText.text
        nominalsText = self.ids.nominalsText.text
        weightsText = self.ids.weightsText.text

        checkIDOrder = self.ids.checkIDText.orderNum
        nominalsOrder = self.ids.nominalsText.orderNum
        weightsOrder = self.ids.weightsText.orderNum

        if(checkIDText == "" or nominalsText == "" or weightsText == ""):
            self.ids.weightsPopError.text = "Enter data for all fields"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(checkIDText, checkIDOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(nominalsText, nominalsOrder)
        cursorStart3, textLength3 = self.parent.children[1].writeText(weightsText, weightsOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + textLength3 + 2)
        self.parent.children[1].ids.weightsButton.colorGrey()

        #Render series nominal
        seriesButtonId = "series" + str(self.parent.children[1].currentSeries)
        self.parent.children[1].displaySeriesNominal(self.parent.children[1].ids.userText.text, self.parent.children[1].ids[seriesButtonId])

        self.dismiss()

class VectorsPopup(PopupBase):
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

        cursorStart1, textLength1 = self.parent.children[1].writeText(restraintText, restraintOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(checkText, checkOrder)
        cursorStart3, textLength3 = self.parent.children[1].writeText(nextRestraintText, nextRestraintOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + textLength3 + 2)
        self.parent.children[1].ids.positionVectorsButton.colorGrey()

        self.dismiss()

class StatisticsPopup(PopupBase):
    def submit(self):
        sigmawText = self.ids.sigmawText.text.strip()
        sigmatText = self.ids.sigmatText.text.strip()

        sigmawOrder = self.ids.sigmawText.orderNum
        sigmatOrder = self.ids.sigmatText.orderNum

        if(sigmawText == "" or sigmatText == ""):
            self.ids.sigmaPopError.text = "Enter data for all fields"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(sigmawText, sigmawOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(sigmatText, sigmatOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + 1)
        self.parent.children[1].ids.statisticsButton.colorGrey()

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
        print("Using saved sigma...")

class SaveStatisticsPopup(PopupBase):
    def __init__(self, sigw, sigt, **kwargs):
        self.sigw = sigw
        self.sigt = sigt
        super().__init__()

    def saveStats(self):
        if(self.ids.balanceNameText.text.strip() != "" and self.ids.nominalText.text.strip() != ""):
            try:
                API.saveStats(self.ids.balanceNameText.text.strip(), self.ids.nominalText.text.strip(), self.ids.descriptionText.text.strip(), float(self.sigw), float(self.sigt))

                self.ids.statsError.color = (0.05, 0.65, 0.1, 0.98)
                self.ids.statsError.text = "Added standard deviations on the " + self.ids.balanceNameText.text.strip()
                threading.Thread(target=self.displaySuccess).start()
            except:
                self.ids.statsError.text = "Error adding to database"
        else:
            self.ids.statsError.text = "Balance & Description required to add to database"

    def displaySuccess(self):
        time.sleep(1.25)
        self.dismiss()

class SwPopup(PopupBase):
    def submit(self):
        swMassText = self.ids.swMassText.text
        swDensityText = self.ids.swDensityText.text
        swCCEText = self.ids.swCCEText.text

        swMassOrder = self.ids.swMassText.orderNum
        swDensityOrder = self.ids.swDensityText.orderNum
        swCCEOrder = self.ids.swCCEText.orderNum

        if(swMassText == "" or swDensityText == "" or swCCEText == ""):
            self.ids.swPopError.text = "Enter data for all fields"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(swMassText, swMassOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(swDensityText, swDensityOrder)
        cursorStart3, textLength3 = self.parent.children[1].writeText(swCCEText, swCCEOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + textLength3 + 2)
        self.parent.children[1].ids.swButton.colorGrey()

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
        print("Using saved sw...")

class SaveSwPopup(PopupBase):
    def __init__(self, mass, density, cce, **kwargs):
        self.swMass = mass
        self.swDensity = density
        self.swCCE = cce
        super().__init__()

    def saveSw(self):
        if(self.ids.swNameText.text.strip() != ""):
            try:
                API.saveSw(self.ids.swNameText.text.strip(), float(self.swMass), float(self.swDensity), float(self.swCCE))

                self.ids.swNameError.color = (0.05, 0.65, 0.1, 0.98)
                self.ids.swNameError.text = "Added " + self.ids.swNameText.text.strip()
                threading.Thread(target=self.displaySuccess).start()
            except:
                self.ids.swNameError.text = "Error adding to database"
        else:
            self.ids.swNameError.text = "Name required to add sw"

    def displaySuccess(self):
        time.sleep(1.25)
        self.dismiss()

class MeasurementsPopup(PopupBase):
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

        cursorStart1, textLength1 = self.parent.children[1].writeText(envText, envOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(envCorrectionsText, envCorrectionsOrder)
        cursorStart3, textLength3 = self.parent.children[1].writeText(balanceReadingsText, balanceReadingsOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + textLength3 + 2)
        self.parent.children[1].ids.measurementsButton.colorGrey()

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

        cursorStart1, textLength1 = self.parent.children[1].writeText(gradientText, gradientOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(localGravText, localGravOrder)
        cursorStart3, textLength3 = self.parent.children[1].writeText(heightText, heightOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + textLength3 + 2)
        self.parent.children[1].ids.gravityButton.colorGrey()

        self.dismiss()

class OpenFilePopup(Popup):
    def openFile(self, fileName):
        try:
            with open(fileName) as configFile:
                fileText = configFile.read()
        except(FileNotFoundError):
            self.parent.children[1].sendError(fileName + " NOT FOUND IN CURRENT DIRECTORY")
            self.dismiss()
            return

        self.parent.children[1].splitSeries(fileText)
        self.dismiss()

class OpenNewFilePopup(Popup):
    def setMessage(self, newFile):
        #Save current working series Text into self.seriesTexts array
        seriesNum = self.parent.children[1].currentSeries
        self.parent.children[1].seriesTexts[seriesNum - 1] = self.parent.children[1].ids.userText.text

        rep = self.parent.children[1].getReportNum()
        if(rep == False):
            self.ids.newFileMessage.text = "No report number provided in Series 1,\nfile cannot be saved. Open new file anyway?"
            self.ids.openNewFileButton.text = "Don't Save &\nOpen"
            if(newFile == True):
                self.ids.openNewFileButton.bind(on_release=self.openNewFileNoSave)
            else:
                self.ids.openNewFileButton.bind(on_release=self.openFileSearchNoSave)
        else:
            self.ids.newFileMessage.text = "Save before opening new file?"
            self.ids.openNewFileButton.text = "Save & Open"
            self.ids.cancelNewFileButton.text = "Don't Save\n& Open"
            if(newFile == True):
                self.ids.openNewFileButton.bind(on_release=self.openNewFile)
                self.ids.cancelNewFileButton.bind(on_release=self.openNewFileNoSave)
            else:
                self.ids.openNewFileButton.bind(on_release=self.openFileSearch)
                self.ids.cancelNewFileButton.bind(on_release=self.openFileSearchNoSave)

    def openFileSearch(self, e):
        self.parent.children[1].save()

        fileSearchPop = OpenFilePopup()
        self.dismiss()
        fileSearchPop.open()

    def openFileSearchNoSave(self, e):
        fileSearchPop = OpenFilePopup()
        self.dismiss()
        fileSearchPop.open()

    def openNewFile(self, e):
        self.parent.children[1].save()
        self.parent.children[1].splitSeries("@SERIES\n\n")
        self.dismiss()

    def openNewFileNoSave(self, e):
        self.parent.children[1].splitSeries("@SERIES\n\n")
        self.dismiss()

class ValidationPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__()
        self.bind(on_open=self.runTestThread)

    def runTestThread(self, e):
        threading.Thread(target=self.runTestSuite).start()

    def runTestSuite(self):
        self.ids.testingMessage.text = "Running Tests..."
        self.ids.validationText.text = ""

        #Run tests from RunTest.TestSuite class
        testSuite = TestSuite.TestSuite()
        results = testSuite.runFromFE()

        self.ids.validationText.text = results
        self.ids.testingMessage.text = ""
        return

class StartupTestsPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__()
        self.bind(on_open=self.runTestThread)

    def runTestThread(self, *args):
        threading.Thread(target=self.runStartupTests).start()

    def runStartupTests(self):
        start = time.time()
        testSuite = TestSuite.TestSuite()
        testSuite.runFromFE()
        end = time.time()
        print(str((end - start)*1000) + " ms")

        if(testSuite.failed == 0):
            self.dismiss()
        else:
            self.ids.testStatus.color = (0.9, 0.05, 0.05, 0.85)
            self.ids.testStatus.text = "[b]" + str(testSuite.failed) + " INTERNAL TESTING FAILURE/S. OPEN LOGS TO SEE DETAILS[/b]"
            self.ids.openLogButton.bind(on_release=self.openTestLog)
            self.ids.openLogButton.background_color = (0.13, 0.5, 0.95, 0.94)

        return

    def openTestLog(self, e):
        testLogPop = ValidationPopup()
        self.dismiss()
        testLogPop.open()

class RequestClosePopUp(Popup):
    pass

class Mars(App):
    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        return MainLayout()

    def on_start(self):
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
                pop = LabInfoPopup()
                pop.open()

    def openRestraintPop(self):
        if(self.root.currentSeries == 1):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)
            
            if(checkOK):
                self.root.clearErrors()
                pop = RestraintPopup()
                pop.open()

    def openDatePop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)
            
            if(checkOK):
                self.root.clearErrors()
                pop = DatePopup()
                pop.open()

    def openDesignPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)
            
            if(checkOK):
                self.root.clearErrors()
                pop = DesignPopup()
                pop.open()
                pop.ids.dropDownn.dismiss()

    def openWeightsPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = WeightsPopup()
                pop.open()

    def openVectorsPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = VectorsPopup()
                pop.open()

    def openStatisticsPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = StatisticsPopup()
                pop.open()

    def openSwPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = SwPopup()
                pop.open()

    def openMeasurementsPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = MeasurementsPopup()
                pop.open()

    def openGravityPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = GravityPopup()
                pop.open()

    def openFilePop(self):
        freshOpen = self.root.numberOfSeries == 1 and self.root.ids.userText.text.strip() == "@SERIES"
        if(self.root.saved == False and freshOpen == False):
            pop = OpenNewFilePopup()
            pop.open()
            pop.setMessage(False)
        else:
            pop = OpenFilePopup()
            pop.open()

    def openNewFilePop(self):
        freshOpen = self.root.numberOfSeries == 1 and self.root.ids.userText.text.strip() == "@SERIES"
        if(self.root.saved == False and freshOpen == False):
            pop = OpenNewFilePopup()
            pop.open()
            pop.setMessage(True)
        else:
            self.root.splitSeries("@SERIES\n\n")

    def openValidationPop(self):
        pop = ValidationPopup()
        pop.open()

if(__name__ == "__main__"):
    mainApp = Mars()
    mainApp.run()