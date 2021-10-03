import asyncio
import threading

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.toast import toast

import pages.screen_names as constants
import atexit
from tele_utils import utils as tele_helper
import asynckivy
from pydispatch import dispatcher
import pages.event_signals as event_signals

from classifier import model as classifier_model
from kivymd.uix.navigationdrawer import NavigationLayout

from kivy.uix.screenmanager import NoTransition, SlideTransition, ScreenManager
from kivymd.uix.screen import MDScreen
from classifier.model import Model
from threading import Thread


# todo for materials icons: https://materialdesignicons.com/

class TeleMlMain(BoxLayout):
    default_transition = SlideTransition(direction='left')
    back_transition = SlideTransition(direction='right')
    model: Model

    def __init__(self, *args, **kwargs):
        BoxLayout.__init__(self, *args, **kwargs)
        print('init method of TeleMlMain')
        Clock.max_iteration = 20
        self._panel_disable = True
        atexit.register(self.on_clean)
        self.init_client()

    def on_model_loaded(self, model_):
        def main_thread_model_loaded(model__):
            self.model = model__
            Clock.schedule_once(self.process_is_authorized, 0.5)

        Clock.schedule_once(lambda dt: main_thread_model_loaded(model_), 0.5)

    def _finish_init(self, dt):
        print(self.ids)
        self.navigate_to(constants.SCREEN_SIGN_IN_PHONE)

    def navigate_to(self, page: str, is_back=False):
        screen_manager: ScreenManager = self.ids.screen_manager
        cur_screen_: MDScreen = screen_manager.current_screen
        # if cur_screen_.name == page:
        #     print('on method navigate_to, it is already in screen: ', page)
        #     return

        if is_back:
            screen_manager.transition = self.back_transition
        screen_manager.current = page
        screen_manager.transition = self.default_transition

    def on_get_code_btn_pressed(self, phone: str):
        print('on_get_code_btn_pressed called, phone: ', phone)
        coro = tele_helper.send_code_request(self.client, phone, self.on_get_code_request_result)
        asyncio.get_event_loop().run_until_complete(coro)

    def on_get_code_request_result(self, phone, success):
        if success:
            sign_in_code = self.ids.id_screen_sign_in_code
            sign_in_code.phone = phone
            sign_in_code.ids.phone_label.text = ("The code sent to the number " + phone)
            self.navigate_to(constants.SCREEN_SIGN_IN_CODE)
        else:
            toast('something went wrong, please check your connection and try again!')

    def on_sign_in_btn_pressed(self, phone: str, code: str):
        print('on_get_code_btn_pressed called, phone: ', phone)
        coro = tele_helper.sign_in_request(self.client, phone, code, self.on_sign_in_request_result)
        asyncio.get_event_loop().run_until_complete(coro)

    def on_sign_in_request_result(self, success):
        if success:
            Clock.schedule_once(self.process_is_authorized, 0.5)
            # self.process_is_authorized()
        else:
            toast('something went wrong, please check your connection and try again!')

    def on_dialog_item_press(self, value_dialog_id, value_dialog_title):
        screen_manager = self.ids.screen_manager
        chat_screen = screen_manager.get_screen(constants.SCREEN_CHAT)
        chat_screen.setup_info(value_dialog_title, value_dialog_id)
        self.navigate_to(constants.SCREEN_CHAT)

    def on_back_to_phone_pressed(self):
        self.navigate_to(page=constants.SCREEN_SIGN_IN_PHONE, is_back=True)

    def on_do_sign_in_btn_pressed(self):
        self.navigate_to(page=constants.SCREEN_DIALOGS)

    def on_chat_back_btn_pressed(self):
        self.navigate_to(page=constants.SCREEN_DIALOGS, is_back=True)

    def on_clean(self):
        print('on clean called')

    def on_logout_press(self):
        coro = tele_helper.log_out(self.client, self.on_logout_request_result)
        asyncio.get_event_loop().run_until_complete(coro)

    def on_logout_request_result(self, result):
        if result:
            screen_manager: ScreenManager = self.ids.screen_manager
            dialogs_screen = screen_manager.get_screen(constants.SCREEN_DIALOGS)
            if dialogs_screen:
                dialogs_screen.on_clean()
            self.init_client()
            self.navigate_to(constants.SCREEN_SPLASH)
        else:
            toast('Something went wrong, please try again!!!')

    def init_client(self):
        self.client = tele_helper.init_tele_client()

    def process_is_authorized(self, dt=None):
        '''
        starts a process of checking for authorization
        :return: void
        '''
        print('process_is_authorized called')
        coro = tele_helper.is_authorized(self.client, self.on_init_response_is_authorized)
        asyncio.get_event_loop().run_until_complete(coro)

    def on_init_response_is_authorized(self, is_authorized):
        '''
        called from tele_utils when the process of authorization is done, and there is a result
        :return: void
        '''
        print('on_init_response_is_authorized: ', is_authorized)
        if is_authorized:
            toast('You are authorized, well done!')
            self.navigate_to(constants.SCREEN_DIALOGS)
        else:
            toast('You are not authorized, please insert your number')
            self.navigate_to(constants.SCREEN_SIGN_IN_PHONE)

    def on_request_dialogs(self, callback):
        '''
        the method starts fetching dialogs from tele_utils, and the callback is called when a result is delivered
        :return:
        '''
        pass


class Main(MDApp):

    def __init__(self, *args, **kwargs):
        MDApp.__init__(self, *args, **kwargs)
        self.theme_cls.primary_palette = "Blue"


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Main().run())
    loop.close()
