from kivy.properties import ObjectProperty
from pages.base_screen import BaseScreen
from kivy.clock import Clock
from kivymd.toast import toast


class SignInPhone(BaseScreen):
    phone = ObjectProperty()

    def _finish_init(self, dt):
        pass
        #self.root.process_is_authorized()

    def __init__(self, *args, **kwargs):
        BaseScreen.__init__(self, *args, **kwargs)
        print('SignInPhone init ***')

    def on_enter(self, *args):
        print('SignInPhone on_enter ***')
        Clock.schedule_once(self._finish_init, .5)

    def on_get_code_pressed(self):
        phone_number = self.phone.text
        print('on_get_code_pressed pressed, phone:', phone_number)
        if not phone_number:
            toast('Phone number can not be empty')
            return
        self.root.on_get_code_btn_pressed(phone=phone_number)
        # self.root.ids.w_toolbar.left_action_items.append(menu)
