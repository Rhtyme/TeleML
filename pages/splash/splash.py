from threading import Thread

from pages.base_screen import BaseScreen
from kivy.clock import Clock
from kivymd.toast import toast
from classifier import model as classifier_model


class SplashScreen(BaseScreen):

    def _finish_init(self, dt):
        print('SplashScreen on_enter ***')
        Thread(target=classifier_model.get_model_request(self.root.on_model_loaded)).start()
        print('new thread started')

    def __init__(self, *args, **kwargs):
        BaseScreen.__init__(self, *args, **kwargs)
        print('SplashScreen init ***')

    def on_enter(self, *args):
        toast('Initializing resources...')
        Clock.schedule_once(self._finish_init, 3)