import kivy

from kivy.config import Config

Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('graphics', 'fullscreen', 0)
Config.set('graphics', 'window_state', 'maximized')
Config.write()

from kivy.graphics import Color, Rectangle

from kivy.uix.popup import Popup
from kivy.factory import Factory

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

def getNumChacacters(text):
    chars = 0

    for char in text:
        chars += 1

    return chars

class MainLayout(BoxLayout):

    seriesNumber = 1

    def __init__(self, **kwargs):
        super().__init__()

        with self.canvas.before:
            Color(0.25, 0.25, 0.28, 0.55)
            self.backgroundRect = Rectangle(size=self.size, pos=self.pos)

            self.bind(size=self._update_rect, pos=self._update_rect)

        self.saved = False

        self.orderOfTags = {"#": 0, "<Report-Number>": 1, \
        "<Restraint-ID>": 2, "<Unc-Restraint>": 3, "<Random-Error>": 4, \
            "@Series": 5, "<Date>": 6, "<Technician-ID>": 7, "<Balance-ID>": 8, "<Check-Standard-ID>": 9}

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
            newLine = self.getTag(orderNum) + "  " + line
            textInput.insert_text(newLine)

            textBlockLength += len(newLine)

            if(len(text.splitlines()) > 1):
                textInput.insert_text("\n")
                textBlockLength += 1

            if(orderNum == 1 or orderNum == 4):
                textInput.insert_text("\n")

        return cursorStart, textBlockLength

    def getTag(self, orderNum):
        for key in self.orderOfTags:
            if(self.orderOfTags[key] == orderNum):
                return key

    def highlight(self, startPos, textLength):
        self.ids.userText.select_text(startPos, startPos + textLength)
        self.ids.userText.selection_color = 0.1, 0.8, 0.2, 0.20

    def checkTags(self):
        inputText = self.ids.userText.text.splitlines()

        lineNum = 0
        for line in inputText:
            lineNum += 1

            if(line.split() == []):
                pass

            elif(line.split()[0].strip() == ""):
                pass

            else:
                try:
                    self.orderOfTags[line.split()[0].strip()]
                except KeyError:
                    errorMessage = "UNKNOWN TAG ON LINE " + str(lineNum) + ": " + line.split()[0].strip()

                    self.ids.errors.text = "ERRORS:\n" + errorMessage
                    return False

        return True

    def textAdded(self):
        if(self.saved):
            self.ids.saveButton.background_color = (1, 0.85, 0.02, 1)
            self.ids.runButton.background_color = (0.62, 0.62, 0.62, 0.62)

            self.saved = False

    def save(self):
        self.saved = True

        self.ids.runButton.background_color = (0.20, 0.68, 0.27, 0.98)
        self.ids.saveButton.background_color = (0.62, 0.62, 0.62, 0.62)

    def run(self):
        if(not self.saved):
            pass
        else:
            print("Run Python MassCode")

class OrderedText(TextInput):
    def __init__(self, **kwargs):
        super().__init__()

        self.orderNum = 0

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

        dateOrder = self.ids.dateText.orderNum
        techIDOrder = self.ids.techIDText.orderNum

        if(dateText == "" or techIDText == ""):
            self.ids.datePopError.text = "Enter data for all fields"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(dateText, dateOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(techIDText, techIDOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + 1)

        self.parent.children[1].ids.dateButton.background_color = (0.62, 0.62, 0.62, 0.62)

        self.dismiss()

class BalanceIDPopup(Popup):
    def submit(self):
        balanceIDText = self.ids.balanceIDText.text
        checkIDText = self.ids.checkIDText.text

        balanceIDOrder = self.ids.balanceIDText.orderNum
        checkIDOrder = self.ids.checkIDText.orderNum

        if(balanceIDText == "" or checkIDText == ""):
            self.ids.balancePopError.text = "Enter data for all fields"
            return

        cursorStart1, textLength1 = self.parent.children[1].writeText(balanceIDText, balanceIDOrder)
        cursorStart2, textLength2 = self.parent.children[1].writeText(checkIDText, checkIDOrder)

        self.parent.children[1].highlight(cursorStart1, textLength1 + textLength2 + 1)

        self.parent.children[1].ids.balanceIDButton.background_color = (0.62, 0.62, 0.62, 0.62)

        self.dismiss()

class PyMac(App):
    def build(self):
        return MainLayout()

    def openLabInfoPop(self):
        pop = LabInfoPopup()

        checkOK = self.root.checkTags()

        if(checkOK):
            self.root.ids.errors.text = "ERRORS:"
            pop.open()

    def openRestraintPop(self):
        pop = RestraintPopup()

        checkOK = self.root.checkTags()
        
        if(checkOK):
            self.root.ids.errors.text = "ERRORS:"
            pop.open()

    def openDatePop(self):
        pop = DatePopup()

        checkOK = self.root.checkTags()
        
        if(checkOK):
            self.root.ids.errors.text = "ERRORS:"
            pop.open()

    def openBalanceIDPop(self):
        pop = BalanceIDPopup()

        checkOK = self.root.checkTags()
        
        if(checkOK):
            self.root.ids.errors.text = "ERRORS:"
            pop.open()

if __name__ == "__main__":
    mainApp = PyMac()
    mainApp.run()