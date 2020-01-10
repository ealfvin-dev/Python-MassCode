import kivy

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

textFile = TextInput(font_size=30, background_normal = '', text="#PyMac\n#Comments")

class MainLayout(BoxLayout):
    def addToTextBox(self, btn):
        tags = {"Report #": "Report-Number: "}
        self.ids.userText.text += tags[btn.text]

class PyMac(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    mainApp = PyMac()
    mainApp.run()