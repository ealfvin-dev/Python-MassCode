import kivy

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

textFile = TextInput(font_size=30, background_normal = '', text="#PyMac\n#Comments")

class MainLayout(BoxLayout):

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

        btn.background_color = 0.6, 0.6, 0.6, 0.6

class PyMac(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    mainApp = PyMac()
    mainApp.run()