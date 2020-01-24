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
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

def findInsertion():
        pass

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

    def _update_rect(self, instance, value):
        self.backgroundRect.pos = instance.pos
        self.backgroundRect.size = instance.size

    def getID(self, instance):
        for idName, element in self.ids.items():
            if(instance == element):
                return str(idName)

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

class LabInfoPopup(Popup):
    def writeText(self):
        masterTextFile = self.parent.children[1].ids.userText
        labInfoText = ""

        userText = self.ids.labInfoText.text.split("\n") 

        charStart = 0 #self.findInsertion()

        for line in userText:
            if(line == ""):
                labInfoText += "\n"

            else:
                labInfoText += "#" + line + "\n"

        labInfoText += "\n"

        masterTextFile.cursor = (0,0)
        masterTextFile.insert_text(labInfoText)

        newTextLength = getNumChacacters(labInfoText)

        masterTextFile.select_text(charStart, newTextLength)
        masterTextFile.selection_color = 0.1, 0.8, 0.2, 0.20

        self.parent.children[1].ids.labInfoButton.background_color = (0.62, 0.62, 0.62, 0.62)

        self.dismiss()

class RestraintPopup(Popup):
    def writeText(self):
        restraintIDText = self.ids.restraintIDText.text
        restraintUncertaintyText = self.ids.restraintUncertaintyText.text
        randomErrorText = self.ids.randomErrorText.text

        if(restraintIDText == "" or restraintUncertaintyText == "" or randomErrorText == ""):
            self.ids.restraintPopError.text = "Enter data for all required fields"
            return

        self.parent.children[1].ids.restraintButton.background_color = (0.62, 0.62, 0.62, 0.62)
        self.dismiss()

class PyMac(App):
    def build(self):
        return MainLayout()

    def openLabInfoPop(self):
        pop = LabInfoPopup()
        pop.open()

    def openRestraintPop(self):
        pop = RestraintPopup()
        pop.open()

if __name__ == "__main__":
    mainApp = PyMac()
    mainApp.run()