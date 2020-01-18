import kivy

from kivy.config import Config
from kivy.graphics import Color, Rectangle

from kivy.uix.popup import Popup
from kivy.factory import Factory

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

    def openPopUp(self):
        popupLayout = BoxLayout()
        popupLayout.orientation = "horizontal"

        col1 = BoxLayout()
        col1.orientation = "vertical"
        col2 = BoxLayout()
        col2.orientation = "vertical"

        label1 = Label()
        label2 = Label()

        label1.text = "text1"
        label2.text = "text2"

        input1 = TextInput()
        input2 = TextInput()

        doneButton = Button()
        cancelButton = Button()

        col1.add_widget(label1)
        col1.add_widget(input1)
        col1.add_widget(cancelButton)

        col2.add_widget(label2)
        col2.add_widget(input2)
        col2.add_widget(doneButton)

        popupLayout.add_widget(col1)
        popupLayout.add_widget(col2)

        popup = Popup()
        popup.auto_dismiss = False
        popup.title="First Popup"
        popup.size_hint=(0.5, 0.5)
        popup.content=popupLayout

        popup.open()

class PyMac(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    mainApp = PyMac()
    mainApp.run()