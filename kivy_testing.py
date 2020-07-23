from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color
from kivy.core.window import Window
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty
import random



class Main_Page(BoxLayout):
    def __init__(self, **kwargs):
        super(Main_Page, self).__init__(**kwargs)     # this is only for if kivy code goes in the py file

        self.orientation = 'vertical'     # rows not cols
        self.btn = Button(text = "pre-change")
        self.btn.bind(on_release = self.changetext)
        self.add_widget(self.btn)


    def changetext(self, instance):
        instance.text = "new text bababbababayayyyy"






class myApp(App):
    def build(self):
        return Main_Page()


if __name__ == "__main__":
    stock_app = myApp()
    stock_app.run()