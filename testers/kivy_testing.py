from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty

import python_testing


class Main_Page(BoxLayout):
    def __init__(self, **kwargs):
        super(Main_Page, self).__init__(**kwargs)     # this is only for if kivy code goes in the py file

        self.btn1 = Button(text = "left", background_normal = "", background_color = [0.81,0.81,0,1])
        self.btn2 = Button(text = "right", background_normal = "", background_color = [1,1,0,0.74])
        self.btn3 = Button(text = "right", background_normal = "", background_color = [1,1,0.3,0.7])

        self.btn2.bind(on_release=self.btn_changer)

        self.add_widget(self.btn1)
        self.add_widget(self.btn2)
        self.add_widget(self.btn3)


    def btn_changer(self, instance):
        instance.background_color = [1,1,0.3,0.7]



class myApp(App):
    def build(self):
        return Main_Page()


if __name__ == "__main__":
    stock_app = myApp()
    stock_app.run()