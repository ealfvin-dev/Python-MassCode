import kivy

from kivy.config import Config

Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('graphics', 'fullscreen', 0)
Config.set('graphics', 'window_state', 'maximized')
Config.write()

from kivy.graphics import Color, Rectangle

from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.factory import Factory

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

import MassCode
import sys

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

    def __init__(self, **kwargs):
        super().__init__()

        with self.canvas.before:
            #Color(0.25, 0.25, 0.28, 0.85)
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
            "<Position>": 14, \
            "<Pounds>": 15, \
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

        self.requiredTags = ["@SERIES", "<Report-Number>", "<Restraint-ID>", "<Unc-Restraint>", "<Random-Error>", "<Date>", "<Technician-ID>", "<Check-Standard-ID>", "<Balance-ID>", "<Direct-Readings>", "<Direct-Reading-SF>", \
            "<Design-ID>", "<Design>", "<Position>", "<Pounds>", "<Restraint>", "<Check-Standard>", "<Linear-Combo>", "<Pass-Down>", \
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
                newLine = self.getTag(orderNum) + "  " + line
                textInput.insert_text(newLine)

                textBlockLength += len(newLine)

                if(len(text.splitlines()) > 1):
                    textInput.insert_text("\n")
                    textBlockLength += 1

                if(orderNum == 1 or orderNum == 4 or orderNum == 8 or orderNum == 11 or orderNum == 15 or orderNum == 19 or orderNum == 21 or orderNum == 24 or orderNum == 27):
                    textInput.insert_text("\n")

        return cursorStart, textBlockLength

    def getTag(self, orderNum):
        for tag in self.orderOfTags:
            if(self.orderOfTags[tag] == orderNum):
                return tag

    def highlight(self, startPos, textLength):
        self.ids.userText.select_text(startPos, startPos + textLength)
        self.ids.userText.selection_color = (0.1, 0.8, 0.2, 0.20)

    def checkTags(self, seriesArray, seriesNum):
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
                        self.orderOfTags[line.split()[0].strip()]
                    except KeyError:
                        if(seriesNum):
                            snText = str(seriesNum)
                        else:
                            snText = str(seriesNumber)

                        errorMessage = "UNKNOWN TAG IN SERIES " + snText + ", LINE " + str(lineNum) + ": " + line.split()[0].strip()

                        self.ids.errors.text = "ERROR:\n" + errorMessage
                        return False

        return True

    def checkIfAllTags(self, seriesText, seriesNum):
        #Checks if all tags in known tags dictionary exist in seriesText
        for tag in self.requiredTags:
            if((tag == "<Report-Number>" or tag == "<Restraint-ID>" or tag == "<Unc-Restraint>" or tag == "<Random-Error>") and seriesNum != 1):
                continue

            exists = 0
            for line in seriesText.splitlines():
                if(line.split() != []):
                    if(line.split()[0].strip() == tag):
                        exists = 1
                        break

            if(exists == 0):
                self.ids.errors.text = "ERROR:\n" + tag + " DOES NOT EXIST IN SERIES " + str(seriesNum)
                return False

        return True

    def textAdded(self):
        if(self.saved):
            self.ids.saveButton.background_color = (1, 0.85, 0.02, 1)
            self.ids.runButton.background_color = (0.62, 0.62, 0.62, 0.62)

            self.saved = False

    def getReportNum(self, text):
        for line in text:
            if(len(line) == 0):
                continue

            if(line.strip().split()[0] == "<Report-Number>"):
                try:
                    self.reportNum = line.strip().split()[1]
                    return line.strip().split()[1]
                except IndexError:
                    return False

        return False

    def addSeries(self):
        if(self.numberOfSeries == 14):
            return

        self.numberOfSeries += 1

        newSeriesId = "series" + str(self.numberOfSeries)

        self.ids[newSeriesId].text = "[color=#FFFFFF]Series " + str(self.numberOfSeries) +"[/color]"
        self.ids[newSeriesId].exists = True

        self.seriesTexts.append("@SERIES\n\n")

    def goToSeries(self, button, exists, seriesNum):
        if(exists):
            #Write current usertext into seriesTexts, pull new seriesText into userText
            self.seriesTexts[self.currentSeries - 1] = self.ids.userText.text

            self.ids.userText.text = self.seriesTexts[seriesNum - 1]
            self.ids.userText.cursor = (0, 0)
            self.ids.userText.select_text(0, 0)

            self.currentSeries = seriesNum

            for sn in range(1, 15):
                seriesID = "series" + str(sn)

                self.ids[seriesID].background_color = (0.155, 0.217, 0.292, 0.65)

                if(self.ids[seriesID].exists):
                    self.ids[seriesID].text = "[color=#FFFFFF]" + self.ids[seriesID].text[15:]

            button.background_color = (0.906, 0.918, 0.926, 1)
            button.text = "[color=#000000]" + button.text[15:]

            #Update TextInput text, save current text in self.seriesTexts[i]

    def save(self):
        #Save current working series Text into self.seriesTexts array
        self.seriesTexts[self.currentSeries - 1] = self.ids.userText.text

        reportNum = self.getReportNum(self.seriesTexts[0].splitlines())

        if(reportNum == False):
            self.ids.errors.text = "ERROR:\n" + "NO REPORT NUMBER PROVIDED, CANNOT SAVE"
            return

        self.saved = True
        self.ids.errors.text = ""
        
        fileText = ""
        for seriesText in self.seriesTexts:
            fileText += seriesText
            fileText += "\n"

        f = open(reportNum + "-config.txt", 'w')
        f.write(fileText)
        f.close()

        checkOK = self.checkTags(self.seriesTexts, False)

        if(checkOK):
            self.ids.errors.text = ""

            self.ids.runButton.background_color = (0.20, 0.68, 0.27, 0.98)
            self.ids.saveButton.background_color = (0.62, 0.62, 0.62, 0.62)

    def run(self):
        if(not self.saved):
            self.ids.errors.text = "ERROR:\n" + "FILE MUST BE SAVED BEFORE RUNNING"
        else:
            for i in range(len(self.seriesTexts)):
                checkAllExist = self.checkIfAllTags(self.seriesTexts[i], i + 1)

                if(not checkAllExist):
                    return

            checkWrittenTags = self.checkTags(self.seriesTexts, False)

            if(checkWrittenTags):
                self.ids.errors.text = ""
                try:
                    MassCode.run(self.reportNum + "-config.txt")
                except:
                    self.ids.errors.text = "ERROR:\n" + str(sys.exc_info())

class OrderedText(TextInput):
    def __init__(self, **kwargs):
        super().__init__()

        self.orderNum = 0
        self.next_focus = 0
        self.write_tab = False

class SeriesButton(Button):
    def __init__(self, **kwargs):
        super().__init__()

        self.markup = True

        self.seriesNum = 1
        self.exists = False
        self.background_color = (0.155, 0.217, 0.292, 0.65)
        #self.background_color = (0.956, 0.968, 0.976, 0.85)

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__()

        self.completed = False
        self.background_color = 0,0,0,0
        self.canvasColor = (0.08, 0.55, 1, 1)

        with self.canvas.before:
            Color(self.canvasColor)
            pos = self.pos
            size = self.size
            radius = [self.size[0] / 12,]

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

        self.parent.children[1].ids.labInfoButton.background_color = (0.62, 0.62, 0.62, 0.62)
        #self.parent.children[1].ids.labInfoButton.completed = True

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

        self.parent.children[1].ids.restraintButton.background_color = (0.62, 0.62, 0.62, 0.62)

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

        self.parent.children[1].ids.dateButton.background_color = (0.62, 0.62, 0.62, 0.62)

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

        self.parent.children[1].ids.balanceButton.background_color = (0.62, 0.62, 0.62, 0.62)

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

        self.parent.children[1].ids.designButton.background_color = (0.62, 0.62, 0.62, 0.62)

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

        cursorStart1, textLength1 = self.parent.children[1].writeText(weightsText, weightsOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(nominalsText, nominalsOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + 1)

        self.parent.children[1].ids.weightsButton.background_color = (0.62, 0.62, 0.62, 0.62)

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

        self.parent.children[1].ids.positionVectorsButton.background_color = (0.62, 0.62, 0.62, 0.62)

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

        self.parent.children[1].ids.statisticsButton.background_color = (0.62, 0.62, 0.62, 0.62)

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

        self.parent.children[1].ids.swButton.background_color = (0.62, 0.62, 0.62, 0.62)

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

        #Check if Num lines are the same for measurements and env data
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
            self.ids.measurementsPopError.text = "Same number of lines required for balance & environmental readings"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(balanceReadingsText, balanceReadingsOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(envText, envOrder)
        cursorStart3, textLength3 = self.parent.children[1].writeText(envCorrectionsText, envCorrectionsOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + textLength3 + 2)

        self.parent.children[1].ids.measurementsButton.background_color = (0.62, 0.62, 0.62, 0.62)

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

        self.parent.children[1].ids.gravityButton.background_color = (0.62, 0.62, 0.62, 0.62)

        self.dismiss()

class PyMac(App):
    def build(self):
        return MainLayout()

    def openLabInfoPop(self):
        if(self.root.currentSeries == 1):
            seriesText = self.root.ids.userText.text

            checkOK = self.root.checkTags([seriesText], self.root.currentSeries)

            if(checkOK):
                self.root.ids.errors.text = ""
                pop = LabInfoPopup()
                pop.open()

    def openRestraintPop(self):
        if(self.root.currentSeries == 1):
            seriesText = self.root.ids.userText.text

            checkOK = self.root.checkTags([seriesText], self.root.currentSeries)
            
            if(checkOK):
                self.root.ids.errors.text = ""
                pop = RestraintPopup()
                pop.open()

    def openDatePop(self):
        seriesText = self.root.ids.userText.text

        checkOK = self.root.checkTags([seriesText], self.root.currentSeries)
        
        if(checkOK):
            self.root.ids.errors.text = ""
            pop = DatePopup()
            pop.open()

    def openBalancePop(self):
        seriesText = self.root.ids.userText.text

        checkOK = self.root.checkTags([seriesText], self.root.currentSeries)
        
        if(checkOK):
            self.root.ids.errors.text = ""
            pop = BalancePopup()
            pop.open()

    def openDesignPop(self):
        seriesText = self.root.ids.userText.text

        checkOK = self.root.checkTags([seriesText], self.root.currentSeries)
        
        if(checkOK):
            self.root.ids.errors.text = ""
            pop = DesignPopup()
            pop.open()

    def openWeightsPop(self):
        seriesText = self.root.ids.userText.text

        checkOK = self.root.checkTags([seriesText], self.root.currentSeries)

        if(checkOK):
            self.root.ids.errors.text = ""
            pop = WeightsPopup()
            pop.open()

    def openVectorsPop(self):
        seriesText = self.root.ids.userText.text

        checkOK = self.root.checkTags([seriesText], self.root.currentSeries)

        if(checkOK):
            self.root.ids.errors.text = ""
            pop = VectorsPopup()
            pop.open()

    def openStatisticsPop(self):
        seriesText = self.root.ids.userText.text

        checkOK = self.root.checkTags([seriesText], self.root.currentSeries)

        if(checkOK):
            self.root.ids.errors.text = ""
            pop = StatisticsPopup()
            pop.open()

    def openSwPop(self):
        seriesText = self.root.ids.userText.text

        checkOK = self.root.checkTags([seriesText], self.root.currentSeries)

        if(checkOK):
            self.root.ids.errors.text = ""
            pop = SwPopup()
            pop.open()

    def openMeasurementsPop(self):
        seriesText = self.root.ids.userText.text

        checkOK = self.root.checkTags([seriesText], self.root.currentSeries)

        if(checkOK):
            self.root.ids.errors.text = ""
            pop = MeasurementsPopup()
            pop.open()

    def openGravityPop(self):
        seriesText = self.root.ids.userText.text

        checkOK = self.root.checkTags([seriesText], self.root.currentSeries)

        if(checkOK):
            self.root.ids.errors.text = ""
            pop = GravityPopup()
            pop.open()

if __name__ == "__main__":
    mainApp = PyMac()
    mainApp.run()