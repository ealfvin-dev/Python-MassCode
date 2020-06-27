import kivy

from kivy.config import Config

Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('graphics', 'fullscreen', 0)
Config.set('graphics', 'window_state', 'maximized')
Config.write()

from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
from kivy.metrics import dp, mm

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox

import RunFile
import TestSuite
import InputChecks
import MARSException

import sys
import os
import threading

#import sqlite3
import time
def getNumChacacters(text):
    chars = 0

    for char in text:
        chars += 1

    return chars

class MainLayout(BoxLayout):
    reportNum = ""
    numberOfSeries = 1
    currentSeries = 1
    seriesTexts = ["@SERIES\n\n"]
    outputText = ""

    def __init__(self, **kwargs):
        super().__init__()

        with self.canvas.before:
            Color(0.906, 0.918, 0.926, 1)
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
            "<Check-Standard-ID>": 8, \
            "<Balance-ID>": 9, \
            "<Direct-Readings>": 10, \
            "<Direct-Reading-SF>": 11, \
            "<Design-ID>": 12, \
            "<Design>": 13, \
            "<Pounds>": 14, \
            "<Position>": 15, \
            "<Restraint>": 16, \
            "<Check-Standard>": 17, \
            "<Linear-Combo>": 18, \
            "<Pass-Down>": 19, \
            "<Sigma-t>": 20, \
            "<Sigma-w>": 21, \
            "<sw-Mass>": 22, \
            "<sw-Density>": 23, \
            "<sw-CCE>": 24, \
            "<Balance-Reading>": 25, \
            "<Environmentals>": 26, \
            "<Env-Corrections>": 27, \
            "<Gravity-Grad>": 28, \
            "<COM-Diff>": 29}

        self.requiredTags = ["<Report-Number>", "<Restraint-ID>", "<Unc-Restraint>", "<Random-Error>", "<Date>", "<Technician-ID>", "<Check-Standard-ID>", "<Balance-ID>", "<Direct-Readings>", "<Direct-Reading-SF>", \
            "<Design-ID>", "<Design>", "<Pounds>", "<Position>", "<Restraint>", "<Check-Standard>", "<Linear-Combo>", "<Pass-Down>", \
            "<Sigma-t>", "<Sigma-w>", "<sw-Mass>", "<sw-Density>", "<sw-CCE>", "<Balance-Reading>", "<Environmentals>", "<Env-Corrections>"]

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

                if(orderNum == 1 or orderNum == 4 or orderNum == 8 or orderNum == 11 or orderNum == 14 or orderNum == 19 or orderNum == 21 or orderNum == 24 or orderNum == 27):
                    textInput.insert_text("\n")

        return cursorStart, textBlockLength

    def getTag(self, orderNum):
        for tag in self.orderOfTags:
            if(self.orderOfTags[tag] == orderNum):
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

    def textAdded(self):
        if(self.saved):
            self.saved = False
            self.ids.saveButton.background_color = (0.0314, 0.62, 0.165, 0.9)
            self.ids.runButton.background_color = (0.62, 0.62, 0.62, 0.62)

    def getReportNum(self, text):
        for line in text:
            if(len(line.strip().split()) == 0):
                continue

            if(line.strip().split()[0] == "<Report-Number>"):
                try:
                    self.reportNum = line.strip().split()[1]
                    return line.strip().split()[1]
                except IndexError:
                    self.reportNum = ""
                    return False

        self.reportNum = ""
        return False

    def displaySeriesNominal(self, inputText, seriesButton):
        #Call this from save(), gotoseries(), addpositionscallback()
        seriesNominal = 0
        units = ""
        foundNominal = False
        foundUnits = False

        for line in inputText.splitlines():
            if(len(line.strip().split()) == 0):
                continue

            if(line.strip().split()[0] == "<Position>" and foundNominal == False):
                try:
                    seriesNominal = line.strip().split()[2]
                    foundNominal = True
                except IndexError:
                    pass
                
            elif(line.strip().split()[0] == "<Pounds>"):
                try:
                    unitsNum = line.strip().split()[1]
                    if(unitsNum == "0"):
                        units = "g"
                        foundUnits = True
                    if(unitsNum == "1"):
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
            "<Env-Corrections>": False, \
            "<Gravity-Grad>": False, \
            "<COM-Diff>": False}

        for line in seriesText.splitlines():
            if(line.strip() != "" and line.strip != "\n"):
                try:
                    tags[line.strip().split()[0]] = True
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
        if(tags["<Date>"] and tags["<Technician-ID>"] and tags["<Check-Standard-ID>"]):
            self.ids.dateButton.colorGrey()
        else:
            self.ids.dateButton.colorBlue()

        #Balance Button
        if(tags["<Balance-ID>"] and tags["<Direct-Readings>"] and tags["<Direct-Reading-SF>"]):
            self.ids.balanceButton.colorGrey()
        else:
            self.ids.balanceButton.colorBlue()

        #Gravity Button
        if(tags["<COM-Diff>"] and tags["<Gravity-Grad>"]):
            self.ids.gravityButton.colorGrey()
        else:
            self.ids.gravityButton.background_color = (0.368, 0.49, 0.60, 1)

        #Statistics Buttons
        if(tags["<Sigma-t>"] and tags["<Sigma-w>"]):
            self.ids.statisticsButton.colorGrey()
        else:
            self.ids.statisticsButton.colorBlue()

        #Design Button
        if(tags["<Design>"] and tags["<Design-ID>"]):
            self.ids.designButton.colorGrey()
        else:
            self.ids.designButton.colorBlue()

        #Weights Button
        if(tags["<Position>"] and tags["<Pounds>"]):
            self.ids.weightsButton.colorGrey()
        else:
            self.ids.weightsButton.colorBlue()

        #Positions Button
        if(tags["<Restraint>"] and tags["<Check-Standard>"] and tags["<Linear-Combo>"] and tags["<Pass-Down>"]):
            self.ids.positionVectorsButton.colorGrey()
        else:
            self.ids.positionVectorsButton.colorBlue()

        #Sensitivity Weight Button
        if(tags["<sw-Mass>"] and tags["<sw-Density>"] and tags["<sw-CCE>"]):
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
        self.ids.balanceButton.colorGrey()
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

    def goToSeries(self, seriesNum, exists):
        if(exists):
            if(self.currentSeries != None):
                #Write current usertext into seriesTexts
                self.seriesTexts[self.currentSeries - 1] = self.ids.userText.text

                #Render current series button nominal
                seriesButtonId = "series" + str(self.currentSeries)
                self.displaySeriesNominal(self.seriesTexts[self.currentSeries - 1], self.ids[seriesButtonId])

            #Pull new seriesText into userText
            self.ids.userText.readonly = False
            self.ids.userText.text = self.seriesTexts[seriesNum - 1]
            self.ids.userText.cursor = (0, 0)
            self.ids.userText.select_text(0, 0)

            self.currentSeries = seriesNum

            #Make all tabs black/blue:
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

            self.renderButtons(self.ids.userText.text)

    def removeLastSeries(self):
        if(self.numberOfSeries == 1):
            return

        lastSeriesText = self.seriesTexts[len(self.seriesTexts) - 1].strip().splitlines()

        #If user is currently working in the last series
        if(self.currentSeries == self.numberOfSeries):
            lastSeriesText = self.ids.userText.text.strip().splitlines()

        if(lastSeriesText == []):
            self.clearErrors()

            if(self.currentSeries == self.numberOfSeries):
                self.goToSeries(self.numberOfSeries - 1, True)

            self.seriesTexts.pop()
            self.ids["series" + str(self.numberOfSeries)].text = ""
            self.ids["series" + str(self.numberOfSeries)].exists = False

            self.numberOfSeries -= 1
        else:
            self.sendError("SERIES " + str(self.numberOfSeries) + " INPUT TEXT MUST BE EMPTY BEFORE REMOVING THE SERIES")

    def openFile(self, fileName):
        #fileName = None to open a new file
        if(fileName == None):
            configFile = ["@SERIES", "\n", "\n"]
        else:
            #Check if file exists
            try:
                configFile = open(fileName, 'r')
            except(FileNotFoundError):
                self.sendError("FILE NOT FOUND")
                return

        #Remove existing series
        self.goToSeries(1, True)
        self.ids.userText.text = ""

        for i in range(self.numberOfSeries):
            self.seriesTexts[self.numberOfSeries - 1] = ""
            self.removeLastSeries()

        self.clearErrors()
        seriesNum = 0

        for line in configFile:
            if(line.strip() == "@SERIES"):
                seriesNum += 1
                if(seriesNum > 1):
                    self.ids.userText.do_backspace()

                    self.addSeries()
                    self.goToSeries(seriesNum, True)

                    self.ids.userText.text = "@SERIES\n"
                    continue
                else:
                    self.ids.userText.text += "@SERIES\n"
            else:
                self.ids.userText.text += line

        if(fileName != None):
            configFile.close()

        self.ids.userText.do_backspace()    
        self.goToSeries(1, True)
        self.getReportNum(self.seriesTexts[0].splitlines())
        self.grabOutputFile()

    def save(self):
        #If in the output tab, return
        if(self.currentSeries == None):
            return

        #Save current working series Text into self.seriesTexts array
        self.seriesTexts[self.currentSeries - 1] = self.ids.userText.text

        reportNum = self.getReportNum(self.seriesTexts[0].splitlines())

        if(reportNum == False):
            self.sendError("NO REPORT NUMBER PROVIDED IN SERIES 1, CANNOT SAVE")
            return

        seriesButtonId = "series" + str(self.currentSeries)
        self.displaySeriesNominal(self.seriesTexts[self.currentSeries - 1], self.ids[seriesButtonId])
        
        fileText = ""
        for seriesText in self.seriesTexts:
            fileText += seriesText
            fileText += "\n"

        f = open(reportNum + "-config.txt", 'w')
        f.write(fileText)
        f.close()

        self.saved = True
        self.sendSuccess("FILE SAVED AS " + str(self.reportNum) + "-config.txt")

        self.renderButtons(self.ids.userText.text)

        self.ids.runButton.background_color = (0.0314, 0.62, 0.165, 0.9)
        self.ids.saveButton.background_color = (0.62, 0.62, 0.62, 0.62)

    def run(self):
        #Perform checks to make sure the input file is in a runnable state
        start = time.time()
        if(self.currentSeries == None):
            return

        if(not self.saved):
            self.sendError("FILE MUST BE SAVED BEFORE RUNNING")
            return
            
        checkAllExist = InputChecks.checkIfAllTags(self.seriesTexts, self.requiredTags, self.sendError, self.goToSeries)
        if(not checkAllExist):
            return

        checkWrittenTags = InputChecks.checkTags(self.seriesTexts, False, self.orderOfTags, self.highlightError, self.sendError)
        if(not checkWrittenTags):
            return

        checkRepeats = InputChecks.checkForRepeats(self.seriesTexts, self.sendError, self.highlightError)
        if(not checkRepeats):
            return

        requiredChecks = InputChecks.runRequiredChecks(self.seriesTexts, self.numberOfSeries, self.sendError, self.highlightError, self.goToSeries)
        if(not requiredChecks):
            return

        self.clearErrors()
        try:
            results = RunFile.run(self.reportNum + "-config.txt")
            self.grabOutputFile()
            self.sendSuccess("FILE SUCCESSFULLY RUN\nOUTPUT SAVED AS " + str(self.reportNum) + "-out.txt")

            secondaryChecks = InputChecks.runSecondaryChecks(self.seriesTexts, self.reportNum, self.sendError, self.highlightError)
            if(secondaryChecks):
                InputChecks.checkResults(results)
        except MARSException.MARSException as ex:
            self.sendError("RUNTIME ERROR: " + str(ex))
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
            #Save current text and render current series button nominal if coming from a series tab
            if(self.currentSeries != None):
                self.seriesTexts[self.currentSeries - 1] = self.ids.userText.text

                seriesButtonId = "series" + str(self.currentSeries)
                self.displaySeriesNominal(self.seriesTexts[self.currentSeries - 1], self.ids[seriesButtonId])

            self.currentSeries = None

            #Pull output text into userText
            self.ids.userText.text = self.outputText
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

        self.orderNum = 0
        self.write_tab = False

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
        self.background_color = (0.155, 0.217, 0.292, 0.65)

class InputButton(Button):
    def __init__(self, **kwargs):
        super().__init__()

        self.background_normal = ''
        #self.background_color = (0.62, 0.62, 0.62, 0.62)
        self.background_color = (0.13, 0.5, 0.95, 0.94)
        self.markup = True
        self.halign = 'center'

    def colorGrey(self):
        self.background_color = ((0.62, 0.62, 0.62, 0.62))

    def colorBlue(self):
        self.background_color = (0.13, 0.5, 0.95, 0.94)

class CancelButton(Button):
    def __init__(self, **kwargs):
        super().__init__()

        self.background_normal = ''
        self.background_color = (0.70, 0.135, 0.05, 0.92)
        self.text = "Cancel"
        self.halign = 'center'

class WriteButton(Button):
    def __init__(self, **kwargs):
        super().__init__()

        self.background_normal = ''
        self.background_color = (0.13, 0.5, 0.95, 0.94)
        self.text = "Write"
        self.halign = 'center'

        #self.bind(on_release=root.submit)

# class RoundedButton(Button):
#     def __init__(self, **kwargs):
#         super().__init__()

#         self.completed = False
#         self.background_color = 0,0,0,0
#         self.canvasColor = (0.08, 0.55, 1, 1)

#         with self.canvas.before:
#             Color(self.canvasColor)
#             pos = self.pos
#             size = self.size
#             radius = [self.size[0] / 12,]

    def goToSeries(self, exists, seriesNum):
        if(exists):
            self.background_color = (0.25, 0.25, 0.28, 1.0)
            self.text = "[color=#FFFFFF]" + self.text + "[/color]"

class LabInfoPopup(Popup):
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

        self.dismiss()

class RestraintPopup(Popup):
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

class DatePopup(Popup):
    def submit(self):
        dateText = self.ids.dateText.text
        techIDText = self.ids.techIDText.text
        checkIDText = self.ids.checkIDText.text

        dateOrder = self.ids.dateText.orderNum
        techIDOrder = self.ids.techIDText.orderNum
        checkIDOrder = self.ids.checkIDText.orderNum

        if(dateText == "" or techIDText == "" or checkIDText == ""):
            self.ids.datePopError.text = "Enter data for all fields"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(dateText, dateOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(techIDText, techIDOrder)
        cursorStart3, textLength3 = self.parent.children[1].writeText(checkIDText, checkIDOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + textLength3 + 2)

        self.parent.children[1].ids.dateButton.colorGrey()

        self.dismiss()

class BalancePopup(Popup):
    def submit(self):
        balanceIDText = self.ids.balanceIDText.text
        directReadingsText = self.ids.directReadingsText.text
        directReadingsSFText = self.ids.directReadingsSFText.text

        balanceOrder = self.ids.balanceIDText.orderNum
        directReadingsOrder = self.ids.directReadingsText.orderNum
        directReadingsSFOrder = self.ids.directReadingsSFText.orderNum

        if(balanceIDText == "" or directReadingsText == "" or directReadingsSFText == ""):
            self.ids.balancePopError.text = "Enter data for all fields"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(balanceIDText, balanceOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(directReadingsText, directReadingsOrder)
        cursorStart3, textLength3 = self.parent.children[1].writeText(directReadingsSFText, directReadingsSFOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + textLength3 + 2)

        self.parent.children[1].ids.balanceButton.colorGrey()

        self.dismiss()

class DesignPopup(Popup):
    def writeDesign(self, design):
        if(design == "3-1"):
            self.ids.designText.text = "1 -1  0\n1  0 -1\n0  1 -1"
            self.ids.designText.cursor = (0, 0)
            self.ids.designIDText.text = "111"

        if(design == "4-1"):
            self.ids.designText.text = "1 -1  0  0\n1  0 -1  0\n1  0  0 -1\n0  1 -1  0\n0  1  0 -1\n0  0  1 -1"
            self.ids.designText.cursor = (0, 0)
            self.ids.designIDText.text = "112"

        if(design == "5-1"):
            self.ids.designText.text = "1 -1  0  0  0\n1  0 -1  0  0\n1  0  0 -1  0\n1  0  0  0 -1\n0  1 -1  0  0\n0  1  0 -1  0\n0  1  0  0 -1\n0  0  1 -1  0\n0  0  1  0 -1\n0  0  0  1 -1"
            self.ids.designText.cursor = (0, 0)
            self.ids.designIDText.text = "114"

        if(design == "532111"):
            self.ids.designText.text = "1 -1 -1  1 -1  0\n1 -1 -1  0  1 -1\n1 -1 -1 -1  0  1\n1 -1 -1  0  0  0\n1  0 -1 -1 -1 -1\n0  1 -1  1 -1 -1\n0  1 -1 -1  1 -1\n0  1 -1 -1 -1  1\n0  0  1 -1 -1  0\n0  0  1 -1  0 -1\n0  0  1  0 -1 -1"
            self.ids.designText.cursor = (0, 0)
            self.ids.designIDText.text = "032"

        if(design == "522111"):
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

class WeightsPopup(Popup):
    def submit(self):
        weightsText = self.ids.weightsText.text
        nominalsText = self.ids.nominalsText.text

        weightsOrder = self.ids.weightsText.orderNum
        nominalsOrder = self.ids.nominalsText.orderNum

        if(weightsText == "" or nominalsText == ""):
            self.ids.weightsPopError.text = "Enter data for all fields"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(nominalsText, nominalsOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(weightsText, weightsOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + 1)

        self.parent.children[1].ids.weightsButton.colorGrey()

        #Render series nominal
        seriesButtonId = "series" + str(self.parent.children[1].currentSeries)
        self.parent.children[1].displaySeriesNominal(self.parent.children[1].ids.userText.text, self.parent.children[1].ids[seriesButtonId])

        self.dismiss()

class VectorsPopup(Popup):
    def submit(self):
        restraintText = self.ids.restraintVectorText.text
        checkText = self.ids.checkVectorText.text
        linearComboText = self.ids.linearComboText.text
        nextRestraintText = self.ids.nextRestraintText.text

        restraintOrder = self.ids.restraintVectorText.orderNum
        checkOrder = self.ids.checkVectorText.orderNum
        linearComboOrder = self.ids.linearComboText.orderNum
        nextRestraintOrder = self.ids.nextRestraintText.orderNum

        if(restraintText == "" or checkText == "" or linearComboText == "" or nextRestraintText == ""):
            self.ids.vectorsPopError.text = "Enter data for all fields"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(restraintText, restraintOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(checkText, checkOrder)
        cursorStart3, textLength3 = self.parent.children[1].writeText(linearComboText, linearComboOrder)
        cursorStart4, textLength4 = self.parent.children[1].writeText(nextRestraintText, nextRestraintOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + textLength3 + textLength4 + 3)

        self.parent.children[1].ids.positionVectorsButton.colorGrey()

        self.dismiss()

class StatisticsPopup(Popup):
    def submit(self):
        sigmatText = self.ids.sigmatText.text
        sigmawText = self.ids.sigmawText.text

        sigmatOrder = self.ids.sigmatText.orderNum
        sigmawOrder = self.ids.sigmawText.orderNum

        if(sigmatText == "" or sigmawText == ""):
            self.ids.sigmaPopError.text = "Enter data for all fields"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(sigmatText, sigmatOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(sigmawText, sigmawOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + 1)

        self.parent.children[1].ids.statisticsButton.colorGrey()

        self.dismiss()

class SwPopup(Popup):
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

class MeasurementsPopup(Popup):
    def submit(self):
        balanceReadingsText = self.ids.balanceReadingsText.text
        envText = self.ids.envText.text
        envCorrectionsText = self.ids.envCorrectionsText.text

        balanceReadingsOrder = self.ids.balanceReadingsText.orderNum
        envOrder = self.ids.envText.orderNum
        envCorrectionsOrder = self.ids.envCorrectionsText.orderNum

        if(balanceReadingsText == "" or envText == "" or envCorrectionsText == ""):
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

        cursorStart1, textLength1 = self.parent.children[1].writeText(balanceReadingsText, balanceReadingsOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(envText, envOrder)
        cursorStart3, textLength3 = self.parent.children[1].writeText(envCorrectionsText, envCorrectionsOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + textLength3 + 2)

        self.parent.children[1].ids.measurementsButton.colorGrey()

        self.dismiss()

class GravityPopup(Popup):
    def submit(self):
        gradientText = self.ids.gradientText.text
        COMText = self.ids.COMText.text

        gradientOrder = self.ids.gradientText.orderNum
        COMOrder = self.ids.COMText.orderNum

        if(gradientText == "" or COMText == ""):
            self.ids.gravityPopError.text = "Enter data for all fields"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(gradientText, gradientOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(COMText, COMOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + 1)

        self.parent.children[1].ids.gravityButton.colorGrey()

        self.dismiss()

class OpenFilePopup(Popup):
    pass

class OpenNewFilePopup(Popup):
    def setMessage(self, newFile):
        rep = self.parent.children[1].getReportNum(self.parent.children[1].ids.userText.text.splitlines())
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
            self.ids.cancelNewFileButton.text = "[color=#FFFFFF]Don't Save\n& Open[/color]"
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
        self.parent.children[1].openFile(None)
        self.dismiss()

    def openNewFileNoSave(self, e):
        self.parent.children[1].openFile(None)
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

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.orderOfTags, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = LabInfoPopup()
                pop.open()

    def openRestraintPop(self):
        if(self.root.currentSeries == 1):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.orderOfTags, self.root.highlightError, self.root.sendError)
            
            if(checkOK):
                self.root.clearErrors()
                pop = RestraintPopup()
                pop.open()

    def openDatePop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.orderOfTags, self.root.highlightError, self.root.sendError)
            
            if(checkOK):
                self.root.clearErrors()
                pop = DatePopup()
                pop.open()

    def openBalancePop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.orderOfTags, self.root.highlightError, self.root.sendError)
            
            if(checkOK):
                self.root.clearErrors()
                pop = BalancePopup()
                pop.open()

    def openDesignPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.orderOfTags, self.root.highlightError, self.root.sendError)
            
            if(checkOK):
                self.root.clearErrors()
                pop = DesignPopup()
                pop.open()
                pop.ids.dropDownn.dismiss()

    def openWeightsPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.orderOfTags, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = WeightsPopup()
                pop.open()

    def openVectorsPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.orderOfTags, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = VectorsPopup()
                pop.open()

    def openStatisticsPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.orderOfTags, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = StatisticsPopup()
                pop.open()

    def openSwPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.orderOfTags, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = SwPopup()
                pop.open()

    def openMeasurementsPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.orderOfTags, self.root.highlightError, self.root.sendError)

            if(checkOK):
                self.root.clearErrors()
                pop = MeasurementsPopup()
                pop.open()

    def openGravityPop(self):
        if(self.root.currentSeries != None):
            seriesText = self.root.ids.userText.text

            checkOK = InputChecks.checkTags([seriesText], self.root.currentSeries, self.root.orderOfTags, self.root.highlightError, self.root.sendError)

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
            self.root.openFile(None)

    def openValidationPop(self):
        pop = ValidationPopup()
        pop.open()

if(__name__ == "__main__"):
    mainApp = Mars()
    mainApp.run()