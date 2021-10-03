from kivy.app import App
from kivymd.uix.screen import MDScreen


class BaseScreen(MDScreen):
    @property
    def root(self):
        return App.get_running_app().root