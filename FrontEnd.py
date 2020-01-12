import kivy

from kivy.config import Config
from kivy.graphics import Color, Rectangle

from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

Config.set('graphics', 'fullscreen', 0)
Config.set('graphics', 'window_state', 'maximized')

#Config.set('graphics', 'height', '500')
#Config.set('graphics', 'width', '1000')
Config.write()

class MainLayout(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__()

        with self.canvas.before:
            Color(0.25, 0.25, 0.28, 0.55)
            self.backgroundRect = Rectangle(size=self.size, pos=self.pos)

            self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.backgroundRect.pos = instance.pos
        self.backgroundRect.size = instance.size

    def getID(self, instance):
        for idName, element in self.ids.items():
            if(instance == element):
                return str(idName)

    def addToTextBox(self, btn):
        tags = {"reportNumButton": "Report-Number: ",
                "restraintIdButton": "Restraint-ID: ",
                "referenceTempButton": "Reference-Temperature: ",
                "uncRestraintButton": "Unc-Restraint: ",
                "designIdButton": "Design-ID: ",
                "observationsButton": "Observations: ",
                "numWeightsButton": "Positions: ",
                "dateButton": "Date: ",
                "techIDButton": "Technition-ID: ",
                "balanceIDButton": "Balance-ID: ",
                "checkIDButton": "Check-Standard-ID: ",
                "restraintPositionButton": "Restraint: ",
                "checkPositionButton": "Check-Standard: ",
                "linearComboPositionButton": "Linear-Combo: ",
                "nextRestraintPositionButton": "Next-Series-Restraint: ",
                "randomErrorButton": "Random-Error: ",
                "swMassButton": "sw-Mass: ",
                "swDensityButton": "sw-Density: ",
                "swCCEButton": "sw-CCE: ",
                "sigmawButton": "Sigma-w: ",
                "sigmatButton": "Sigma-t: "}

        tag = tags[self.getID(btn)]
        self.ids.userText.text += (tag + "\n")

        btn.background_color = 0.62, 0.62, 0.62, 0.62

class PyMac(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    mainApp = PyMac()
    mainApp.run()