import kivy

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class PyMac(App):
    def build(self):
        rootLayout = BoxLayout(orientation='horizontal', spacing=10, padding=(0, 30, 30, 30))
        menuColOne = BoxLayout(orientation='vertical', spacing=100, padding=(100, 0, 100, 0))
        menuColTwo = BoxLayout(orientation='vertical', spacing=100, padding=(100, 0, 100, 0))
        menu = BoxLayout(orientation='horizontal')
        textLayout = BoxLayout(orientation='vertical', spacing=20)

        buttonColor = (0.145, 0.5725, 0.967, 0.97)

        text = TextInput(font_size=40, background_normal = '')
        errors = TextInput(background_normal = '')

        #Header
        headerLabel = Label(text="[color=#CCD3D9][size=56][b]HEADER[/b][/size][/color]", markup=True)

        reportNumButton = Button(text="Report #", background_normal = '', background_color=buttonColor)
        restraintIDButton = Button(text="Restraint ID", background_normal = '', background_color=buttonColor)
        referenceTempButton = Button(text="Reference Temp (" + u"\u00b0" + "C)", background_normal = '', background_color=buttonColor)

        #Design
        designLabel = Label(text="[color=#CCD3D9][size=56][b]DESIGN[/b][/size][/color]", markup=True)

        designButton = Button(text="Design", background_normal = '', background_color=buttonColor)
        observationsButton = Button(text="# Observations", background_normal = '', background_color=buttonColor)
        numWeights = Button(text="# Weights", background_normal = '', background_color=buttonColor)

        #Restraint/Check

        menuColOne.add_widget(designLabel)
        menuColOne.add_widget(designButton)
        menuColOne.add_widget(observationsButton)

        menuColTwo.add_widget(headerLabel)
        menuColTwo.add_widget(reportNumButton)
        menuColTwo.add_widget(restraintIDButton)
        menuColTwo.add_widget(referenceTempButton)

        textLayout.add_widget(text)
        textLayout.add_widget(errors)

        menu.add_widget(menuColOne)
        menu.add_widget(menuColTwo)
        rootLayout.add_widget(menu)
        rootLayout.add_widget(textLayout)

        return rootLayout

if __name__ == "__main__":
    PyMac().run()